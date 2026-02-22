<?php
/**
 * ========================================
 * 保质期管理系统 - 综合管理后台
 * 文件名: index.php
 * 版本: v2.8.2
 * 创建日期: 2026-02-15
 * 更新日期: 2026-02-18
 * ========================================
 */

// 升级配置 - 使用安全的内网源
define('APP_VERSION', '2.14.2');
define('UPDATE_URL', null); // 禁用外部自动升级，改用手动升级
define('UPDATE_SERVER', 'feishu'); // 从飞书获取升级包

session_start();
require_once 'db.php';

// 自动迁移
function autoMigrate() {
    $conn = getDBConnection();
    if (!$conn) return;
    
    $cols = [
        'products' => [
            'category_id' => 'INT(11) UNSIGNED DEFAULT 0 AFTER id',
            'inventory_cycle' => "VARCHAR(20) DEFAULT 'none' AFTER removal_buffer",
            'last_inventory_at' => "DATETIME DEFAULT NULL AFTER inventory_cycle"
        ],
        'batches' => [
            'session_id' => 'VARCHAR(50) DEFAULT NULL AFTER quantity'
        ]
    ];
    foreach($cols as $table => $fields) {
        foreach($fields as $col => $def) {
            $res = $conn->query("SHOW COLUMNS FROM `$table` LIKE '$col'");
            if ($res && $res->num_rows == 0) { $conn->query("ALTER TABLE `$table` ADD COLUMN `$col` $def"); }
        }
    }
    
    $conn->query("CREATE TABLE IF NOT EXISTS `categories` (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) UNIQUE, type VARCHAR(20), rule TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    $conn->query("INSERT IGNORE INTO `categories` (name, type, rule) VALUES ('小食品', 'snack', '{\"need_buffer\":true, \"scrap_on_removal\":true}'), ('物料', 'material', '{\"need_buffer\":false, \"scrap_on_removal\":false}'), ('咖啡豆', 'coffee', '{\"need_buffer\":true, \"scrap_on_removal\":false, \"allow_gift\":true}')");
    $conn->query("CREATE TABLE IF NOT EXISTS `inventory_sessions` (id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY, session_key VARCHAR(50) UNIQUE, user_id INT UNSIGNED, item_count INT DEFAULT 0, created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
}
autoMigrate();

if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    $action = $_GET['api']; $conn = getDBConnection();

    // 登录接口（不需要鉴权）
    if ($action === 'login') {
        $data = json_decode(file_get_contents('php://input'), true);
        $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
        $stmt->bind_param("s", $data['username']); $stmt->execute();
        $row = $stmt->get_result()->fetch_assoc();
        if ($row && password_verify($data['password'], $row['password'])) {
            $_SESSION['user_id'] = $row['id']; $_SESSION['username'] = $row['username'];
            echo json_encode(['success'=>true]); exit;
        }
        echo json_encode(['success'=>false, 'message'=>'账号或密码错误']); exit;
    }
    if ($action === 'logout') { session_destroy(); echo json_encode(['success'=>true]); exit; }
    
    // ⚠️ 安全修复：升级接口需要管理员权限
    if ($action === 'check_upgrade' || $action === 'execute_upgrade') {
        if (!isset($_SESSION['user_id'])) {
            echo json_encode(['success'=>false, 'message'=>'需要登录']); exit;
        }
        // 检查是否是管理员
        $stmt = $conn->prepare("SELECT is_admin FROM users WHERE id = ?");
        $stmt->bind_param("i", $_SESSION['user_id']);
        $stmt->execute();
        $result = $stmt->get_result()->fetch_assoc();
        if (!$result || !$result['is_admin']) {
            echo json_encode(['success'=>false, 'message'=>'需要管理员权限']); exit;
        }
        
        if ($action === 'check_upgrade') {
            // 检查是否有新版本（从飞书或手动检查）
            echo json_encode([
                'success'=>true, 
                'current'=>APP_VERSION, 
                'latest'=>APP_VERSION,
                'has_update'=>false,
                'message'=>'请前往飞书查看最新版本'
            ]); exit;
        }
        
        if ($action === 'execute_upgrade') {
            // 禁用远程升级，需要手动上传文件
            echo json_encode([
                'success'=>false, 
                'message'=>'出于安全考虑，自动升级已禁用。请手动下载升级包并上传。'
            ]); exit;
        }
    }

    checkAuth();
    
    if ($action === 'search_products') {
        $q = trim($_GET['q'] ?? '');
        if ($q === '') {
            echo json_encode(['success' => true, 'data' => []]);
            exit;
        }
        // 模糊搜索：SKU 或 品名
        $like = '%' . $q . '%';
        $stmt = $conn->prepare("SELECT id, sku, name FROM products WHERE sku LIKE ? OR name LIKE ? ORDER BY id DESC LIMIT 20");
        $stmt->bind_param('ss', $like, $like);
        $stmt->execute();
        $res = $stmt->get_result();
        $list = [];
        while ($row = $res->fetch_assoc()) {
            $list[] = $row;
        }
        echo json_encode(['success' => true, 'data' => $list]);
        exit;
    }

    if ($action === 'get_product') {
        $sku = $_GET['sku'] ?? '';
        $stmt = $conn->prepare("SELECT p.*, c.rule as category_rule FROM products p LEFT JOIN categories c ON p.category_id = c.id WHERE p.sku = ? LIMIT 1");
        $stmt->bind_param("s", $sku); $stmt->execute();
        $product = $stmt->get_result()->fetch_assoc();
        if ($product) {
            $stmt_batch = $conn->prepare("SELECT * FROM batches WHERE product_id = ? ORDER BY expiry_date ASC");
            $stmt_batch->bind_param("i", $product['id']); $stmt_batch->execute();
            $batch_res = $stmt_batch->get_result(); $batches = [];
            while ($b = $batch_res->fetch_assoc()) {
                $rule = json_decode($product['category_rule'] ?? '{}', true);
                $buffer = ($rule['need_buffer'] ?? true) ? (int)$product['removal_buffer'] : 0;
                $remDate = date('Y-m-d', strtotime($b['expiry_date']." - $buffer days"));
                $diff = (strtotime($remDate) - strtotime(date('Y-m-d'))) / 86400;
                $b['status'] = $diff < 0 ? 'expired' : ($diff < 30 ? 'urgent' : 'healthy');
                $b['removal_date'] = $remDate; $b['days_left'] = $diff;
                $batches[] = $b;
            }
            $product['batches'] = $batches;
            echo json_encode(['success'=>true, 'exists'=>true, 'product'=>$product]);
        } else { echo json_encode(['success'=>true, 'exists'=>false]); }
        exit;
    }
    if ($action === 'save_product') {
        $data = json_decode(file_get_contents('php://input'), true);
        $sku = $data['sku']; $name = $data['name']; $catid = (int)$data['category_id']; $buffer = (int)$data['removal_buffer'];
        $sid = $data['session_id'] ?? null;
        $stmt = $conn->prepare("SELECT id FROM products WHERE sku = ?");
        $stmt->bind_param("s", $sku); $stmt->execute();
        $res = $stmt->get_result();
        if ($res->num_rows > 0) {
            $pid = $res->fetch_assoc()['id'];
            $stmt = $conn->prepare("UPDATE products SET category_id=?, removal_buffer=? WHERE id=?");
            $stmt->bind_param("iii", $catid, $buffer, $pid); $stmt->execute();
        } else {
            $stmt = $conn->prepare("INSERT INTO products (sku, name, category_id, removal_buffer) VALUES (?, ?, ?, ?)");
            $stmt->bind_param("ssii", $sku, $name, $catid, $buffer); $stmt->execute();
            $pid = $conn->insert_id;
        }
        foreach ($data['batches'] as $b) {
            $stmt = $conn->prepare("INSERT INTO batches (product_id, expiry_date, quantity, session_id) VALUES (?, ?, ?, ?)");
            $stmt->bind_param("isis", $pid, $b['expiry_date'], $b['quantity'], $sid); $stmt->execute();
        }
        echo json_encode(['success'=>true]); exit;
    }
    
    // ⚠️ 安全修复：使用prepared statement防止SQL注入
    if ($action === 'submit_session') {
        $data = json_decode(file_get_contents('php://input'), true);
        $sid = $data['session_id'];
        
        // 使用prepared statement
        $stmt = $conn->prepare("SELECT COUNT(*) as count FROM batches WHERE session_id = ?");
        $stmt->bind_param("s", $sid);
        $stmt->execute();
        $res = $stmt->get_result();
        $count = $res->fetch_assoc()['count'];
        
        $stmt = $conn->prepare("INSERT INTO inventory_sessions (session_key, user_id, item_count) VALUES (?, ?, ?)");
        $stmt->bind_param("sii", $sid, $_SESSION['user_id'], $count);
        $stmt->execute();
        
        echo json_encode(['success'=>true]); exit;
    }
    if ($action === 'get_past_sessions') {
        $res = $conn->query("SELECT * FROM inventory_sessions ORDER BY created_at DESC LIMIT 50");
        $list = []; while($r = $res->fetch_assoc()) $list[] = $r;
        echo json_encode(['success'=>true, 'data'=>$list]); exit;
    }
    if ($action === 'get_session_details') {
        $sid = $_GET['session_id'];
        // ⚠️ 安全修复：使用prepared statement
        $stmt = $conn->prepare("SELECT p.sku, p.name, b.expiry_date, b.quantity, p.removal_buffer 
                                 FROM batches b 
                                 JOIN products p ON b.product_id = p.id 
                                 WHERE b.session_id = ? 
                                 ORDER BY DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) ASC");
        $stmt->bind_param("s", $sid); $stmt->execute();
        $res = $stmt->get_result(); $list = []; while($r = $res->fetch_assoc()) $list[] = $r;
        echo json_encode(['success'=>true, 'data'=>$list]); exit;
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>保质期管理 v<?php echo APP_VERSION; ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <style>
        :root { 
            --primary-color: #667eea; 
            --secondary-color: #764ba2;
            /* 淡蓝苹果风格 */
            --apple-blue: #007AFF;
            --apple-light-blue: #E3F2FD;
            --apple-bg: #F5F5F7;
        }
        body { 
            background: var(--apple-bg); 
            padding-bottom: 50px; 
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
        }
        .app-header { 
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 12px 0; 
            border-bottom: 1px solid rgba(0,0,0,0.1);
            position: sticky; 
            top: 0; 
            z-index: 100; 
        }
        .custom-card { 
            background: white; 
            border-radius: 16px; 
            padding: 16px; 
            margin-bottom: 15px; 
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        .portal-btn { 
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border-radius: 16px; 
            padding: 25px 20px; 
            box-shadow: 0 4px 15px rgba(0,122,255,0.15); 
            margin-bottom: 15px; 
            display: flex; 
            align-items: center; 
            gap: 15px; 
            width: 100%; 
            border: none;
            transition: all 0.3s ease;
        }
        .portal-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,122,255,0.25);
        }
        .portal-btn i { 
            font-size: 2rem; 
            width: 50px; 
            height: 50px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            border-radius: 12px; 
            color: white;
        }
        .bg-new { 
            background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
        }
        .bg-past { 
            background: linear-gradient(135deg, #34C759 0%, #248A3D 100%);
        }
        .view-section { display: none; } 
        .view-section.active { display: block; }
        #scanOverlay { 
            position: fixed; 
            top: 0; 
            left: 0; 
            width: 100%; 
            height: 100%; 
            background: #000; 
            z-index: 2000; 
            display: none; 
            flex-direction: column; 
        }
        #reader { width: 100%; height: 100%; }
        .pending-item { 
            border-left: 4px solid var(--apple-blue); 
            padding: 12px; 
            background: #fff; 
            margin-bottom: 8px; 
            border-radius: 12px; 
            font-size: 0.9rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .btn-primary {
            background: var(--apple-blue);
            border-color: var(--apple-blue);
            border-radius: 12px;
            font-weight: 600;
        }
        .form-control, .form-select {
            border-radius: 12px;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 12px 16px;
        }
        .form-control:focus, .form-select:focus {
            border-color: var(--apple-blue);
            box-shadow: 0 0 0 3px rgba(0,122,255,0.1);
        }
    </style>
</head>
<body>
    <div id="scanOverlay">
        <div class="p-3 d-flex justify-content-between text-white">
            <button class="btn btn-dark rounded-pill" id="stopScanBtn">
                <i class="bi bi-x-lg"></i>
            </button>
            <div class="fw-bold">扫一扫</div>
            <div style="width:40px"></div>
        </div>
        <div id="reader"></div>
    </div>
    <div class="app-header mb-3">
        <div class="container d-flex justify-content-between align-items-center">
            <div>
                <h1 class="h5 mb-0 fw-bold" style="color: var(--apple-blue)">
                    保质期管理 v<?php echo APP_VERSION; ?>
                </h1>
            </div>
            <?php if(isset($_SESSION['user_id'])): ?>
            <div class="dropdown">
                <button class="btn btn-light btn-sm rounded-pill" data-bs-toggle="dropdown">
                    <i class="bi bi-list"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                    <li><a class="dropdown-item" href="admin.php">管理后台</a></li>
                    <li><a class="dropdown-item text-danger" href="#" id="logoutBtn">退出登录</a></li>
                </ul>
            </div>
            <?php endif; ?>
        </div>
    </div>
    <div class="container">
        <?php if(!isset($_SESSION['user_id'])): ?>
        <div class="custom-card text-center mt-5">
            <h3 class="h4 mb-4 fw-bold">🔐 请登录</h3>
            <form id="loginForm">
                <input type="text" class="form-control mb-3" id="loginUser" placeholder="用户名" required>
                <input type="password" class="form-control mb-3" id="loginPass" placeholder="密码" required>
                <button type="submit" class="btn btn-primary w-100">进入系统</button>
            </form>
        </div>
        <?php else: ?>
        <div id="portalView" class="view-section active">
            <button class="portal-btn" onclick="switchView('new')">
                <i class="bi bi-plus-circle-fill bg-new"></i>
                <div class="text-start">
                    <span class="fw-bold text-dark">新增盘点录入</span><br>
                    <small class="text-muted">快速扫码记效期</small>
                </div>
            </button>
            <button class="portal-btn" onclick="switchView('past')">
                <i class="bi bi-clock-history bg-past"></i>
                <div class="text-start">
                    <span class="fw-bold text-dark">查看往期盘点</span><br>
                    <small class="text-muted">浏览历史记录</small>
                </div>
            </button>
            <div class="custom-card">
                <div class="progress mb-2" style="height:10px">
                    <div id="bar-expired" class="progress-bar bg-danger"></div>
                    <div id="bar-urgent" class="progress-bar bg-warning"></div>
                    <div id="bar-healthy" class="progress-bar bg-success"></div>
                </div>
                <div class="row text-center small g-0">
                    <div class="col-4 text-danger fw-bold" id="val-expired">0</div>
                    <div class="col-4 text-warning fw-bold" id="val-urgent">0</div>
                    <div class="col-4 text-success fw-bold" id="val-healthy">0</div>
                </div>
            </div>
        </div>
        <div id="newView" class="view-section">
            <button class="btn btn-link btn-sm text-decoration-none mb-2" onclick="switchView('portal')">
                <i class="bi bi-chevron-left"></i> 返回门户
            </button>
            <div class="scan-trigger-area mb-3 shadow-sm" 
                 id="startScanBtn" 
                 style="padding:40px 20px; 
                        background: linear-gradient(135deg, #E3F2FD, #BBDEFB); 
                        border-radius: 20px; 
                        text-align: center; 
                        color: #007AFF;">
                <i class="bi bi-qr-code-scan d-block h1"></i>
                <span class="fw-bold">点击添加 (扫一扫)</span>
            </div>

            <!-- 手动输入 / 模糊搜索（扫码失败备用） -->
            <div class="custom-card mb-3">
                <div class="fw-bold mb-2">📝 手动输入 / 粘贴二维码</div>
                
                <!-- 快速粘贴区 -->
                <div class="mb-2">
                    <input id="qrPasteInput" 
                           class="form-control" 
                           placeholder="📋 用微信扫码后，直接粘贴URL到这里（支持星巴克URL、纯数字码、SKU）">
                    <button id="qrPasteBtn" class="btn btn-success btn-sm w-100 mt-2">
                        ✅ 解析粘贴的内容
                    </button>
                </div>
                
                <hr class="my-2">
                
                <!-- 搜索区 -->
                <div class="input-group">
                    <input id="manualSearchInput" class="form-control" placeholder="输入SKU片段或品名关键词…">
                    <button id="manualSearchBtn" class="btn btn-outline-primary" type="button">🔍 搜索</button>
                </div>
                <div id="manualSearchResults" class="mt-2"></div>
                <div class="text-muted small mt-2">
                    <strong>提示：</strong>
                    <ul class="mb-0 ps-3">
                        <li>微信扫码后，复制URL粘贴到上面的输入框</li>
                        <li>支持星巴克URL：https://artwork.starbucks.com.cn/...</li>
                        <li>支持纯数字码：001117979820251124#20251124#20260523</li>
                        <li>支持纯SKU：11179798</li>
                    </ul>
                </div>
            </div>

            <div id="pendingList"></div>
            
            <!-- 草稿操作按钮 -->
            <div class="row g-2 mb-3">
                <div class="col-6">
                    <button id="saveDraftBtn" class="btn btn-outline-success w-100">
                        💾 保存草稿
                    </button>
                </div>
                <div class="col-6">
                    <button id="clearDraftBtn" class="btn btn-outline-danger w-100">
                        🗑️ 清空草稿
                    </button>
                </div>
            </div>
            
            <div class="d-grid mt-3">
                <button class="btn btn-primary btn-lg shadow fw-bold" 
                        id="submitSessionBtn" 
                        disabled
                        style="border-radius: 16px;">
                    提交本次盘点单
                </button>
            </div>
        </div>
        <div id="pastView" class="view-section">
            <button class="btn btn-link btn-sm text-decoration-none mb-2" onclick="switchView('portal')">
                <i class="bi bi-chevron-left"></i> 返回门户
            </button>
            <div id="sessionList"></div>
        </div>
        <?php endif; ?>
    </div>
    <div class="modal fade" id="entryModal" data-bs-backdrop="static">
        <div class="modal-dialog">
            <div class="modal-content" style="border-radius: 16px; border: none;">
                <div class="modal-header border-bottom-0">
                    <h5 class="fw-bold">录入详情</h5>
                    <button class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body bg-light">
                    <form id="productForm">
                        <div class="custom-card mb-2">
                            <input type="text" class="form-control mb-2" id="sku" readonly>
                            <select class="form-select mb-2" id="categoryId">
                                <option value="0">分类</option>
                            </select>
                            <input type="text" class="form-control mb-2" id="productName" placeholder="商品名称">
                            <input type="number" class="form-control" id="removalBuffer" placeholder="缓冲天数">
                        </div>
                        <div id="batchesContainer"></div>
                        <button type="button" class="btn btn-outline-success btn-sm w-100" id="addBatchBtn">
                            + 批次
                        </button>
                    </form>
                </div>
                <div class="modal-footer border-top-0 d-grid">
                    <button class="btn btn-primary" id="confirmEntryBtn">确定添加</button>
                </div>
            </div>
        </div>
    </div>
    <div class="modal fade" id="detailModal">
        <div class="modal-dialog modal-dialog-scrollable">
            <div class="modal-content" style="border-radius: 16px;">
                <div class="modal-header border-bottom-0">
                    <h5 class="fw-bold">盘点单明细 (AI 整理)</h5>
                    <button class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-0">
                    <table class="table table-sm small mb-0">
                        <thead>
                            <tr>
                                <th>商品</th>
                                <th>效期</th>
                                <th>数</th>
                            </tr>
                        </thead>
                        <tbody id="inventoryDetailBody"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let html5QrCode = null, currentSessionId = 'S'+Date.now(), pendingData = [];
        
        // 本地存储相关函数
        const STORAGE_KEY = 'inventory_draft';
        
        function saveDraft() {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify(pendingData));
                console.log('草稿已保存:', pendingData.length, '条记录');
                showAlert('✅ 草稿已自动保存', 'success');
            } catch (e) {
                console.error('保存草稿失败:', e);
            }
        }
        
        function loadDraft() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {
                    pendingData = JSON.parse(saved);
                    console.log('已加载草稿:', pendingData.length, '条记录');
                    updatePendingList();
                    if (pendingData.length > 0) {
                        showAlert(`📋 已恢复 ${pendingData.length} 条草稿记录`, 'info');
                    }
                }
            } catch (e) {
                console.error('加载草稿失败:', e);
            }
        }
        
        function clearDraft() {
            try {
                localStorage.removeItem(STORAGE_KEY);
                console.log('草稿已清空');
            } catch (e) {
                console.error('清空草稿失败:', e);
            }
        }
        
        function switchView(v) {
            document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
            document.getElementById(v+'View').classList.add('active');
            if(v==='past') loadPast();
            if(v==='new') loadCats();  // 切换到新增盘点视图时加载分类
        }
        function showAlert(m, t='info') { 
            const el = document.createElement('div'); 
            el.className = `alert alert-${t} fade show shadow position-fixed top-0 start-50 translate-middle-x mt-3`; 
            el.style.zIndex='3000'; 
            el.innerText=m; 
            document.body.appendChild(el); 
            setTimeout(()=>el.remove(), 2500); 
        }
        document.addEventListener('DOMContentLoaded', () => {
            // 加载草稿数据
            loadDraft();
            
            if(document.getElementById('portalView')) { refreshHealth(); loadCats(); checkUpgrade(); }
            document.getElementById('loginForm')?.addEventListener('submit', async(e)=>{ 
                e.preventDefault(); 
                const res = await fetch('index.php?api=login',{
                    method:'POST', 
                    body:JSON.stringify({
                        username:document.getElementById('loginUser').value, 
                        password:document.getElementById('loginPass').value
                    })
                }); 
                if((await res.json()).success) location.reload(); 
                else showAlert('账号或密码错误','danger'); 
            });
            document.getElementById('logoutBtn')?.addEventListener('click', async () => { 
                await fetch('index.php?api=logout'); 
                location.reload(); 
            });
            document.getElementById('startScanBtn')?.addEventListener('click', ()=>{ 
                document.getElementById('scanOverlay').style.display='flex'; 
                if(!html5QrCode) html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start(
                    {facingMode:"environment"},
                    {fps:10, qrbox:{width:250, height:250}},
                    (text)=>{
                        html5QrCode.stop();
                        document.getElementById('scanOverlay').style.display='none';
                        searchSKU(text);
                    }
                ); 
            });
            document.getElementById('stopScanBtn')?.addEventListener('click', ()=>{ 
                if(html5QrCode) html5QrCode.stop(); 
                document.getElementById('scanOverlay').style.display='none'; 
            });
            document.getElementById('addBatchBtn')?.addEventListener('click', ()=>addBatchRow());

            // 手动输入 / 模糊搜索
            document.getElementById('manualSearchBtn')?.addEventListener('click', ()=>manualSearch());
            document.getElementById('manualSearchInput')?.addEventListener('keydown', (e)=>{
                if (e.key === 'Enter') {
                    e.preventDefault();
                    manualSearch();
                }
            });

            // 粘贴二维码URL后解析
            document.getElementById('qrPasteBtn')?.addEventListener('click', ()=>{
                const input = document.getElementById('qrPasteInput');
                const qrCode = input.value.trim();
                
                if (!qrCode) {
                    showAlert('请先粘贴二维码URL或内容', 'warning');
                    return;
                }

                // 直接调用searchSKU解析
                searchSKU(qrCode);
                
                // 清空输入框
                input.value = '';
            });
            
            // 粘贴输入框支持回车触发
            document.getElementById('qrPasteInput')?.addEventListener('keydown', (e)=>{
                if (e.key === 'Enter') {
                    e.preventDefault();
                    document.getElementById('qrPasteBtn').click();
                }
            });

            // 草稿操作按钮
            document.getElementById('saveDraftBtn')?.addEventListener('click', () => {
                saveDraft();
            });
            
            document.getElementById('clearDraftBtn')?.addEventListener('click', () => {
                if (confirm('确定要清空所有草稿数据吗？此操作不可恢复！')) {
                    pendingData = [];
                    clearDraft();
                    updatePendingList();
                    showAlert('🗑️ 草稿已清空', 'info');
                }
            });

            document.getElementById('confirmEntryBtn')?.addEventListener('click', ()=>{
                const batches = []; 
                document.querySelectorAll('.batch-row').forEach(r=>{ 
                    batches.push({
                        expiry_date:r.querySelector('.e-in').value, 
                        quantity:r.querySelector('.q-in').value
                    }); 
                });
                pendingData.push({
                    sku:document.getElementById('sku').value, 
                    name:document.getElementById('productName').value, 
                    category_id:document.getElementById('categoryId').value, 
                    removal_buffer:document.getElementById('removalBuffer').value, 
                    batches, 
                    session_id:currentSessionId
                });
                updatePendingList();
                saveDraft();  // 自动保存草稿
                bootstrap.Modal.getInstance(document.getElementById('entryModal')).hide();
            });
            document.getElementById('submitSessionBtn')?.addEventListener('click', async()=>{
                for(let item of pendingData) {
                    await fetch('index.php?api=save_product',{
                        method:'POST', 
                        body:JSON.stringify(item)
                    });
                }
                await fetch('index.php?api=submit_session',{
                    method:'POST', 
                    body:JSON.stringify({session_id:currentSessionId})
                });
                showAlert('提交成功','success'); 
                pendingData=[]; 
                currentSessionId='S'+Date.now(); 
                clearDraft();  // 清空草稿
                updatePendingList(); 
                switchView('portal'); 
                refreshHealth();
            });
        });
        async function searchSKU(qrCode) {
            // 从二维码中提取SKU
            let sku = qrCode;
            let expiryDateFromQR = null;

            console.log('扫码内容:', qrCode);

            // 格式1: 星巴克URL格式
            // https://artwork.starbucks.com.cn/mobile/gtin/xxx/cii1/00+SKU+生产日期&生产日期&到期日期
            if (qrCode.includes('artwork.starbucks.com.cn')) {
                try {
                    const url = new URL(qrCode);
                    const pathParts = url.pathname.split('/');
                    const ciiIndex = pathParts.indexOf('cii1');

                    if (ciiIndex !== -1 && ciiIndex + 1 < pathParts.length) {
                        let ciiData = pathParts[ciiIndex + 1]; // 00+SKU+生产日期&生产日期&到期日期

                        // 分离所有&后的部分（可能有多个日期）
                        const ampParts = ciiData.split('&');
                        ciiData = ampParts[0]; // 第一部分：00+SKU+生产日期

                        // 提取最后一个日期（到期日期）
                        const lastPart = ampParts[ampParts.length - 1];
                        if (lastPart.length === 8 && /^\d+$/.test(lastPart)) {
                            const year = lastPart.substring(0, 4);
                            const month = lastPart.substring(4, 6);
                            const day = lastPart.substring(6, 8);
                            expiryDateFromQR = `${year}-${month}-${day}`;
                        }

                        // 去掉00前缀
                        if (ciiData.startsWith('00')) {
                            ciiData = ciiData.substring(2);
                        }

                        // 提取SKU（前8位）
                        if (ciiData.length >= 8) {
                            sku = ciiData.substring(0, 8);
                        }

                        console.log('星巴克URL解析:', { sku, expiryDate: expiryDateFromQR });
                    }
                } catch (e) {
                    console.error('解析星巴克URL失败:', e);
                }
            }
            // 格式2: 纯数字格式
            // 00 + SKU(8位) + 生产日期(8位) # 生产日期 # 到期日期
            else if (qrCode.includes('#')) {
                const parts = qrCode.split('#');
                if (parts.length >= 3) {
                    let part1 = parts[0]; // 00 + SKU + 生产日期

                    // 去掉前缀 "00"
                    if (part1.startsWith('00')) {
                        part1 = part1.substring(2);
                    }

                    // 提取SKU（前8位）
                    if (part1.length >= 8) {
                        sku = part1.substring(0, 8);
                    }

                    // 解析到期日期（第三部分）
                    let expiryDatePart = parts[2];
                    if (expiryDatePart.length === 8 && /^\d+$/.test(expiryDatePart)) {
                        const year = expiryDatePart.substring(0, 4);
                        const month = expiryDatePart.substring(4, 6);
                        const day = expiryDatePart.substring(6, 8);
                        expiryDateFromQR = `${year}-${month}-${day}`;
                    }

                    console.log('纯数字格式解析:', { sku, expiryDate: expiryDateFromQR });
                }
            }
            // 格式3: 纯SKU（没有日期）
            else {
                sku = qrCode.trim();
                console.log('纯SKU格式:', { sku });
            }

            // 查询商品信息
            const res = await fetch('index.php?api=get_product&sku='+encodeURIComponent(sku));
            const d = await res.json();
            document.getElementById('productForm').reset();
            document.getElementById('batchesContainer').innerHTML='';
            document.getElementById('sku').value = sku; // 显示提取后的纯SKU
            const fields = ['categoryId','productName','removalBuffer'];

            if(d.exists) {
                document.getElementById('productName').value=d.product.name;
                document.getElementById('categoryId').value=d.product.category_id;
                document.getElementById('removalBuffer').value=d.product.removal_buffer;
                fields.forEach(f => {
                    document.getElementById(f).readOnly=true;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=true;
                });
            } else {
                fields.forEach(f => {
                    document.getElementById(f).readOnly=false;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=false;
                });
            }
            addBatchRow(expiryDateFromQR);
            new bootstrap.Modal(document.getElementById('entryModal')).show();
        }
        function addBatchRow(defaultExpiryDate = null) {
            const row = document.createElement('div');
            row.className = 'batch-row input-group input-group-sm mb-2';
            row.innerHTML = `
                <span class="input-group-text">效期</span>
                <input type="date" class="form-control e-in" ${defaultExpiryDate ? `value="${defaultExpiryDate}"` : ''} required>
                <span class="input-group-text">数</span>
                <input type="number" class="form-control q-in" placeholder="数量" required>
                <button class="btn btn-outline-danger" onclick="this.parentElement.remove()">×</button>
            `;
            document.getElementById('batchesContainer').appendChild(row);
        }
        async function loadCats() {
            const res = await fetch('api.php?endpoint=categories');
            const d = await res.json();
            const sel = document.getElementById('categoryId');
            sel.innerHTML = '<option value="0">无分类</option>';
            d.categories.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
        async function manualSearch() {
            const q = (document.getElementById('manualSearchInput')?.value || '').trim();
            const box = document.getElementById('manualSearchResults');
            if (!box) return;
            box.innerHTML = '';
            if (!q) {
                showAlert('请输入SKU片段或品名关键词', 'warning');
                return;
            }

            // 如果用户粘贴了整段二维码（包含#），直接走录入流程
            if (q.includes('#')) {
                searchSKU(q);
                return;
            }

            const res = await fetch('index.php?api=search_products&q=' + encodeURIComponent(q));
            const d = await res.json();
            if (!d.success) {
                showAlert(d.message || '搜索失败', 'danger');
                return;
            }
            if (!d.data || d.data.length === 0) {
                showAlert('没搜到匹配项', 'warning');
                return;
            }

            const list = document.createElement('div');
            list.className = 'list-group mt-2';
            d.data.forEach((item) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'list-group-item list-group-item-action';
                btn.innerHTML = `<div class="fw-bold">${item.name || '(未命名)'}</div><div class="small text-muted">${item.sku}</div>`;
                btn.addEventListener('click', () => searchSKU(item.sku));
                list.appendChild(btn);
            });
            box.appendChild(list);
        }

        function updatePendingList() {
            const div = document.getElementById('pendingList');
            const btn = document.getElementById('submitSessionBtn');
            div.innerHTML = '';
            if(pendingData.length === 0) {
                btn.disabled = true;
                return;
            }
            btn.disabled = false;
            pendingData.forEach((item, idx) => {
                const el = document.createElement('div');
                el.className = 'pending-item';
                el.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${item.sku}</strong> ${item.name}
                            <br><small class="text-muted">${item.batches.length} 个批次</small>
                        </div>
                        <button class="btn btn-sm btn-outline-danger" onclick="pendingData.splice(${idx},1);updatePendingList()">×</button>
                    </div>
                `;
                div.appendChild(el);
            });
        }
        async function loadPast() {
            const res = await fetch('index.php?api=get_past_sessions');
            const d = await res.json();
            const div = document.getElementById('sessionList');
            div.innerHTML = '';
            d.data.forEach(s => {
                const card = document.createElement('div');
                card.className = 'custom-card';
                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>单号: ${s.session_key}</strong>
                            <br><small class="text-muted">${s.created_at}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${s.item_count} 件</span>
                        </div>
                    </div>
                `;
                card.style.cursor = 'pointer';
                card.addEventListener('click', async() => {
                    const res = await fetch(`index.php?api=get_session_details&session_id=${s.session_key}`);
                    const d = await res.json();
                    const tbody = document.getElementById('inventoryDetailBody');
                    tbody.innerHTML = '';
                    d.data.forEach(item => {
                        tbody.innerHTML += `<tr><td>${item.sku}</td><td>${item.expiry_date}</td><td>${item.quantity}</td></tr>`;
                    });
                    new bootstrap.Modal(document.getElementById('detailModal')).show();
                });
                div.appendChild(card);
            });
        }
        async function refreshHealth() {
            const res = await fetch('api.php?endpoint=summary');
            const d = await res.json();
            document.getElementById('val-expired').innerText = d.summary.expired;
            document.getElementById('val-urgent').innerText = d.summary.urgent;
            document.getElementById('val-healthy').innerText = d.summary.healthy;
            const total = d.summary.expired + d.summary.urgent + d.summary.healthy || 1;
            document.getElementById('bar-expired').style.width = (d.summary.expired/total*100)+'%';
            document.getElementById('bar-urgent').style.width = (d.summary.urgent/total*100)+'%';
            document.getElementById('bar-healthy').style.width = (d.summary.healthy/total*100)+'%';
        }
function editSession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件
            
            try {
                const res = await fetch(`index.php?api=get_editable_session&session_id=${sessionId}`);
                const d = await res.json();
                
                if (d.success) {
                    displayEditSession(d.data);
                    const modal = new bootstrap.Modal(document.getElementById('editModal'));
                    modal.show();
                } else {
                    showAlert('❌ ' + (d.message || '获取盘点单详情失败'), 'danger');
                }
            } catch (error) {
                console.error('获取盘点单详情失败:', error);
                showAlert('❌ 获取盘点单详情失败，请稍后重试', 'danger');
            }
        }
        
        function displayEditSession(data) {
            // 保存当前正在编辑的盘点单数据
            window.currentEditSession = {
                session_id: data.session_id || data.session_key,
                session_key: data.session_id || data.session_key, // 保持一致性
                items: data.items,
                item_count: data.item_count
            };
            
            // 显示盘点单信息
            const infoDiv = document.getElementById('editSessionInfo');
            infoDiv.innerHTML = `
                <div class="custom-card">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>单号: ${data.session_key}</strong>
                            <br><small class="text-muted">${data.created_at}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${data.item_count} 件</span>
                        </div>
                    </div>
                </div>
            `;
            
            // 显示商品列表
            const tbody = document.getElementById('editSessionBody');
            tbody.innerHTML = '';
            
            data.items.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'edit-item-row';
                row.dataset.batchId = item.batch_id;
                row.innerHTML = `
                    <td>${item.sku}</td>
                    <td>${item.name}</td>
                    <td><input type="date" class="form-control form-control-sm expiry-input" value="${item.expiry_date}" data-batch-id="${item.batch_id}"></td>
                    <td><input type="number" class="form-control form-control-sm quantity-input" value="${item.quantity}" min="1" data-batch-id="${item.batch_id}"></td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger delete-batch-btn" onclick="deleteBatch(${item.batch_id})" data-batch-id="${item.batch_id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        
        async function deleteBatch(batchId) {
            if (!confirm('确定要删除这个批次吗？')) {
                return;
            }
            
            try {
                const res = await fetch('index.php?api=delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ batch_id: batchId })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 批次删除成功', 'success');
                    // 重新加载编辑数据
                    editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除批次失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }
        
        function removeBatchRow(button) {
            const row = button.closest('.batch-row');
            if (document.querySelectorAll('#addProductBatchesContainer .batch-row').length > 1) {
                row.remove();
            } else {
                showAlert('至少需要保留一个批次', 'warning');
            }
        }
        
        function showAddProductModal() {
            // 创建添加商品模态框（如果不存在）
            let modal = document.getElementById('editAddProductModal');
            if (!modal) {
                const modalHtml = `
                    <div class="modal fade" id="editAddProductModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">添加商品到盘点单</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <!-- SKU输入区域 -->
                                    <div class="mb-3">
                                        <label class="form-label">商品SKU</label>
                                        <div class="input-group">
                                            <input type="text" class="form-control" id="editAddSkuInput" placeholder="输入SKU或扫码">
                                            <button class="btn btn-outline-secondary" type="button" onclick="startEditScan()">
                                                <i class="bi bi-qr-code-scan"></i> 扫一扫
                                            </button>
                                        </div>
                                        <div id="editAddSkuSuggestions" class="list-group mt-2" style="display:none; max-height: 200px; overflow-y: auto;"></div>
                                    </div>

                                    <!-- 商品信息显示 -->
                                    <div id="editAddProductInfo" class="mb-3" style="display:none;">
                                        <div class="card">
                                            <div class="card-body">
                                                <h6 class="card-title" id="editAddProductName"></h6>
                                                <p class="card-text mb-0">
                                                    <strong>SKU:</strong> <span id="editAddProductSku"></span>
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 批次信息 -->
                                    <div id="editAddBatchContainer" style="display:none;">
                                        <label class="form-label">批次信息</label>
                                        <div class="batch-row mb-2">
                                            <div class="mb-2">
                                                <label class="form-label small">到期日期</label>
                                                <input type="date" class="form-control form-control-sm" id="editAddExpiryDate">
                                            </div>
                                            <div class="mb-2">
                                                <label class="form-label small">数量</label>
                                                <input type="number" class="form-control form-control-sm" id="editAddQuantity" min="1" value="1">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="button" class="btn btn-primary" onclick="confirmEditAddProduct()">确定添加</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHtml);

                // 绑定SKU输入框事件
                const skuInput = document.getElementById('editAddSkuInput');
                skuInput.addEventListener('input', function() {
                    const q = this.value.trim();
                    if (q.length >= 1) { // 减少搜索触发条件
                        searchEditProductSku(q);
                    } else {
                        document.getElementById('editAddSkuSuggestions').style.display = 'none';
                    }
                });
            }

            // 显示模态框
            const bsModal = new bootstrap.Modal(document.getElementById('editAddProductModal'));
            bsModal.show();

            // 重置表单
            document.getElementById('editAddSkuInput').value = '';
            document.getElementById('editAddProductInfo').style.display = 'none';
            document.getElementById('editAddBatchContainer').style.display = 'block'; // 默认为显示
            document.getElementById('editAddSkuSuggestions').style.display = 'none';
            document.getElementById('editAddExpiryDate').value = '';
            document.getElementById('editAddQuantity').value = '1';
        }

        /**
         * 模糊搜索商品（支持SKU和商品名称）
         */
        async function searchEditProductSku(q) {
            try {
                const res = await fetch(`index.php?api=search_products&q=${encodeURIComponent(q)}`);
                const d = await res.json();

                const suggestionsDiv = document.getElementById('editAddSkuSuggestions');
                suggestionsDiv.innerHTML = '';

                if (d.success && d.data && d.data.length > 0) {
                    d.data.forEach(product => {
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <strong>${product.sku}</strong>
                                <small>${product.name}</small>
                            </div>
                        `;
                        item.onclick = (e) => {
                            e.preventDefault();
                            selectEditProduct(product.sku, product.name);
                        };
                        suggestionsDiv.appendChild(item);
                    });
                    suggestionsDiv.style.display = 'block';
                } else {
                    suggestionsDiv.style.display = 'none';
                }
            } catch (error) {
                console.error('搜索失败:', error);
            }
        }

        /**
         * 选择商品
         */
        function selectEditProduct(sku, name) {
            document.getElementById('editAddSkuInput').value = sku;
            document.getElementById('editAddSkuSuggestions').style.display = 'none';

            // 显示商品信息
            document.getElementById('editAddProductName').textContent = name;
            document.getElementById('editAddProductSku').textContent = sku;
            document.getElementById('editAddProductInfo').style.display = 'block';

            // 显示批次输入框
            document.getElementById('editAddBatchContainer').style.display = 'block';
        }

        /**
         * 启动扫描
         */
        function startEditScan() {
            // 设置标志
            window.isEditingAddProduct = true;

            // 隐藏模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('editAddProductModal'));
            if (modal) {
                modal.hide();
            }

            // 显示扫描界面
            const scanOverlay = document.getElementById('scanOverlay');
            if (scanOverlay) {
                scanOverlay.style.display = 'flex';
                if (typeof startScan === 'function') {
                    startScan();
                }
            }
        }

        /**
         * 确认添加商品
         */
        async function confirmEditAddProduct() {
            const sku = document.getElementById('editAddSkuInput').value.trim();
            const expiryDate = document.getElementById('editAddExpiryDate').value;
            const quantity = parseInt(document.getElementById('editAddQuantity').value);

            if (!sku) {
                showAlert('❌ 请输入商品SKU', 'danger');
                return;
            }

            if (!expiryDate) {
                showAlert('❌ 请选择到期日期', 'danger');
                return;
            }

            if (quantity <= 0) {
                showAlert('❌ 数量必须大于0', 'danger');
                return;
            }

            if (!window.currentEditSession || !window.currentEditSession.session_id) {
                showAlert('❌ 编辑会话丢失，请重新进入编辑模式', 'danger');
                return;
            }

            try {
                const requestData = {
                    session_id: window.currentEditSession.session_id,
                    sku: sku,
                    batches: [{
                        expiry_date: expiryDate,
                        quantity: quantity
                    }]
                };

                console.log('发送请求:', requestData);

                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });

                const d = await res.json();

                console.log('API响应:', d);

                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');

                    // 关闭模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editAddProductModal'));
                    if (modal) {
                        modal.hide();
                    }

                    // 重新加载编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加失败，请稍后重试', 'danger');
            }
        }
        
        async function confirmAddProduct() {
            const sku = document.getElementById('addProductSku').value.trim();
            const batchesContainer = document.getElementById('addProductBatchesContainer');
            const batches = [];
            
            const batchRows = batchesContainer.querySelectorAll('.batch-row');
            batchRows.forEach(row => {
                const expiryDate = row.querySelector('input[type="date"]').value;
                const quantity = parseInt(row.querySelector('.quantity-input').value);
                
                if (expiryDate && quantity > 0) {
                    batches.push({ expiry_date: expiryDate, quantity: quantity });
                }
            });
            
            if (!sku || batches.length === 0) {
                showAlert('❌ 请填写完整的商品信息和至少一个批次', 'danger');
                return;
            }
            
            try {
                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: window.currentEditSession.session_key,
                        sku: sku,
                        batches: batches
                    })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');
                    // 关闭模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
                    if (modal) modal.hide();
                    
                    // 重新加载编辑数据
                    editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加商品失败，请稍后重试', 'danger');
            }
        }
        
        async function saveEditSession() {
            // 获取所有修改后的行
            const rows = document.querySelectorAll('#editSessionBody tr.edit-item-row');
            const updates = [];
            
            rows.forEach(row => {
                const batchId = row.dataset.batchId;
                const expiryDate = row.querySelector('.expiry-input').value;
                const quantity = parseInt(row.querySelector('.quantity-input').value);
                
                // 获取原始数据
                const originalItem = window.currentEditSession.items.find(item => item.batch_id == batchId);
                
                if (originalItem.expiry_date !== expiryDate || originalItem.quantity !== quantity) {
                    updates.push({ batch_id: batchId, expiry_date: expiryDate, quantity: quantity });
                }
            });
            
            if (updates.length === 0) {
                showAlert('✅ 没有需要保存的修改', 'success');
                return;
            }
            
            // 保存所有修改
            let allSuccess = true;
            let errors = [];
            
            for (const update of updates) {
                try {
                    const res = await fetch('index.php?api=update_batch', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(update)
                    });
                    
                    const d = await res.json();
                    
                    if (!d.success) {
                        allSuccess = false;
                        errors.push(`批次 ${update.batch_id} 保存失败: ${d.message}`);
                    }
                } catch (error) {
                    allSuccess = false;
                    errors.push(`批次 ${update.batch_id} 保存失败: ${error.message}`);
                }
            }
            
            if (allSuccess) {
                showAlert('✅ 所有修改已成功保存', 'success');
                // 重新加载编辑数据
                editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
            } else {
                showAlert('❌ 部分修改保存失败，请检查错误信息', 'danger');
                console.error('保存失败:', errors);
            }
        }
        
        async function deleteInventorySession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件
            
            if (!confirm('确定要删除这个盘点单吗？删除后无法恢复！')) {
                return;
            }
            
            try {
                const res = await fetch('index.php?api=delete_inventory_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 盘点单删除成功', 'success');
                    loadPast(); // 重新加载列表
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除盘点单失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }
        document.addEventListener('DOMContentLoaded', () => {
            // 加载草稿数据
            loadDraft();
            
            if(document.getElementById('portalView')) { refreshHealth(); loadCats(); checkUpgrade(); }
            document.getElementById('loginForm')?.addEventListener('submit', async(e)=>{ 
                e.preventDefault(); 
                const res = await fetch('index.php?api=login',{
                    method:'POST', 
                    body:JSON.stringify({
                        username:document.getElementById('loginUser').value, 
                        password:document.getElementById('loginPass').value
                    })
                }); 
                if((await res.json()).success) location.reload(); 
                else showAlert('账号或密码错误','danger'); 
            });
            document.getElementById('logoutBtn')?.addEventListener('click', async () => { 
                await fetch('index.php?api=logout'); 
                location.reload(); 
            });
            document.getElementById('startScanBtn')?.addEventListener('click', ()=>{ 
                document.getElementById('scanOverlay').style.display='flex'; 
                if(!html5QrCode) html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start(
                    {facingMode:"environment"},
                    {fps:10, qrbox:{width:250, height:250}},
                    (text)=>{
                        html5QrCode.stop();
                        document.getElementById('scanOverlay').style.display='none';
                        searchSKU(text);
                    }
                ); 
            });
            document.getElementById('stopScanBtn')?.addEventListener('click', ()=>{ 
                if(html5QrCode) html5QrCode.stop(); 
                document.getElementById('scanOverlay').style.display='none'; 
            });
            document.getElementById('addBatchBtn')?.addEventListener('click', ()=>addBatchRow());

            // 手动输入 / 模糊搜索
            document.getElementById('manualSearchBtn')?.addEventListener('click', ()=>manualSearch());
            document.getElementById('manualSearchInput')?.addEventListener('keydown', (e)=>{
                if (e.key === 'Enter') {
                    e.preventDefault();
                    manualSearch();
                }
            });
            
            // 添加商品到盘点单模态框事件
            document.getElementById('addProductBatchBtn')?.addEventListener('click', ()=>{
                const container = document.getElementById('addProductBatchesContainer');
                const batchCount = container.querySelectorAll('.batch-row').length;
                const newBatchRow = document.createElement('div');
                newBatchRow.className = 'batch-row mb-2';
                newBatchRow.innerHTML = `
                    <input type="date" class="form-control form-control-sm mb-1" id="addProductExpiry${batchCount+1}" required>
                    <input type="number" class="form-control form-control-sm quantity-input" id="addProductQuantity${batchCount+1}" placeholder="数量" min="1" required>
                    <button type="button" class="btn btn-outline-danger btn-sm mt-1 remove-batch-btn" onclick="removeBatchRow(this)">
                        - 批次
                    </button>
                `;
                container.appendChild(newBatchRow);
            });
            
            document.getElementById('confirmAddProductBtn')?.addEventListener('click', confirmAddProduct);

            // 草稿操作按钮
            document.getElementById('saveDraftBtn')?.addEventListener('click', () => {
                saveDraft();
            });
            
            document.getElementById('clearDraftBtn')?.addEventListener('click', () => {
                if (confirm('确定要清空所有草稿数据吗？此操作不可恢复！')) {
                    pendingData = [];
                    clearDraft();
                    updatePendingList();
                    showAlert('🗑️ 草稿已清空', 'info');
                }
            });

            document.getElementById('confirmEntryBtn')?.addEventListener('click', ()=>{
                const batches = []; 
                document.querySelectorAll('.batch-row').forEach(r=>{ 
                    batches.push({
                        expiry_date:r.querySelector('.e-in').value, 
                        quantity:r.querySelector('.q-in').value
                    }); 
                });
                pendingData.push({
                    sku:document.getElementById('sku').value, 
                    name:document.getElementById('productName').value, 
                    category_id:document.getElementById('categoryId').value, 
                    removal_buffer:document.getElementById('removalBuffer').value, 
                    batches, 
                    session_id:currentSessionId
                });
                updatePendingList();
                saveDraft();  // 自动保存草稿
                bootstrap.Modal.getInstance(document.getElementById('entryModal')).hide();
            });
            document.getElementById('submitSessionBtn')?.addEventListener('click', async()=>{
                for(let item of pendingData) {
                    await fetch('index.php?api=save_product',{
                        method:'POST', 
                        body:JSON.stringify(item)
                    });
                }
                await fetch('index.php?api=submit_session',{
                    method:'POST', 
                    body:JSON.stringify({session_id:currentSessionId})
                });
                showAlert('提交成功','success'); 
                pendingData=[]; 
                currentSessionId='S'+Date.now(); 
                clearDraft();  // 清空草稿
                updatePendingList(); 
                switchView('portal'); 
                refreshHealth();
            });
        });
        async function searchSKU(qrCode) {
            // 清空搜索框和搜索结果（无论从哪里调用都清空）
            const searchInput = document.getElementById('manualSearchInput');
            if (searchInput) searchInput.value = '';
            
            const searchResults = document.getElementById('manualSearchResults');
            if (searchResults) searchResults.innerHTML = '';
            
            // 从二维码中提取SKU
            let sku = qrCode;
            let expiryDateFromQR = null;

            console.log('扫码内容:', qrCode);

            // 格式1: 星巴克URL格式
            // https://artwork.starbucks.com.cn/mobile/gtin/xxx/cii1/00+SKU+生产日期&生产日期&到期日期
            if (qrCode.includes('artwork.starbucks.com.cn')) {
                try {
                    const url = new URL(qrCode);
                    const pathParts = url.pathname.split('/');
                    const ciiIndex = pathParts.indexOf('cii1');

                    if (ciiIndex !== -1 && ciiIndex + 1 < pathParts.length) {
                        let ciiData = pathParts[ciiIndex + 1]; // 00+SKU+生产日期&生产日期&到期日期

                        // 分离所有&后的部分（可能有多个日期）
                        const ampParts = ciiData.split('&');
                        ciiData = ampParts[0]; // 第一部分：00+SKU+生产日期

                        // 提取最后一个日期（到期日期）
                        const lastPart = ampParts[ampParts.length - 1];
                        if (lastPart.length === 8 && /^\d+$/.test(lastPart)) {
                            const year = lastPart.substring(0, 4);
                            const month = lastPart.substring(4, 6);
                            const day = lastPart.substring(6, 8);
                            expiryDateFromQR = `${year}-${month}-${day}`;
                        }

                        // 去掉00前缀
                        if (ciiData.startsWith('00')) {
                            ciiData = ciiData.substring(2);
                        }

                        // 提取SKU（前8位）
                        if (ciiData.length >= 8) {
                            sku = ciiData.substring(0, 8);
                        }

                        console.log('星巴克URL解析:', { sku, expiryDate: expiryDateFromQR });
                    }
                } catch (e) {
                    console.error('解析星巴克URL失败:', e);
                }
            }
            // 格式2: 纯数字格式
            // 00 + SKU(8位) + 生产日期(8位) # 生产日期 # 到期日期
            else if (qrCode.includes('#')) {
                const parts = qrCode.split('#');
                if (parts.length >= 3) {
                    let part1 = parts[0]; // 00 + SKU + 生产日期

                    // 去掉前缀 "00"
                    if (part1.startsWith('00')) {
                        part1 = part1.substring(2);
                    }

                    // 提取SKU（前8位）
                    if (part1.length >= 8) {
                        sku = part1.substring(0, 8);
                    }

                    // 解析到期日期（第三部分）
                    let expiryDatePart = parts[2];
                    if (expiryDatePart.length === 8 && /^\d+$/.test(expiryDatePart)) {
                        const year = expiryDatePart.substring(0, 4);
                        const month = expiryDatePart.substring(4, 6);
                        const day = expiryDatePart.substring(6, 8);
                        expiryDateFromQR = `${year}-${month}-${day}`;
                    }

                    console.log('纯数字格式解析:', { sku, expiryDate: expiryDateFromQR });
                }
            }
            // 格式3: 纯SKU（没有日期）
            else {
                sku = qrCode.trim();
                console.log('纯SKU格式:', { sku });
            }

            // 查询商品信息
            const res = await fetch('index.php?api=get_product&sku='+encodeURIComponent(sku));
            const d = await res.json();
            document.getElementById('productForm').reset();
            document.getElementById('batchesContainer').innerHTML='';
            document.getElementById('sku').value = sku; // 显示提取后的纯SKU
            const fields = ['categoryId','productName','removalBuffer'];

            if(d.exists) {
                document.getElementById('productName').value=d.product.name;
                document.getElementById('categoryId').value=d.product.category_id;
                document.getElementById('removalBuffer').value=d.product.removal_buffer;
                fields.forEach(f => {
                    document.getElementById(f).readOnly=true;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=true;
                });
            } else {
                fields.forEach(f => {
                    document.getElementById(f).readOnly=false;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=false;
                });
            }
            addBatchRow(expiryDateFromQR);
            new bootstrap.Modal(document.getElementById('entryModal')).show();
        }
        function addBatchRow(defaultExpiryDate = null) {
            const row = document.createElement('div');
            row.className = 'batch-row input-group input-group-sm mb-2';
            row.innerHTML = `
                <span class="input-group-text">效期</span>
                <input type="date" class="form-control e-in" ${defaultExpiryDate ? `value="${defaultExpiryDate}"` : ''} required>
                <span class="input-group-text">数</span>
                <input type="number" class="form-control q-in" placeholder="数量" required>
                <button class="btn btn-outline-danger" onclick="this.parentElement.remove()">×</button>
            `;
            document.getElementById('batchesContainer').appendChild(row);
        }
        async function loadCats() {
            const res = await fetch('api.php?endpoint=categories');
            const d = await res.json();
            const sel = document.getElementById('categoryId');
            sel.innerHTML = '<option value="0">无分类</option>';
            d.categories.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
        async function manualSearch() {
            const q = (document.getElementById('manualSearchInput')?.value || '').trim();
            const box = document.getElementById('manualSearchResults');
            if (!box) return;
            box.innerHTML = '';
            if (!q) {
                showAlert('请输入SKU片段或品名关键词', 'warning');
                return;
            }

            // 如果用户粘贴了整段二维码（包含#），直接走录入流程
            if (q.includes('#')) {
                // 清空搜索框和结果
                const searchInput = document.getElementById('manualSearchInput');
                if (searchInput) searchInput.value = '';
                box.innerHTML = '';
                
                searchSKU(q);
                return;
            }

            const res = await fetch('index.php?api=search_products&q=' + encodeURIComponent(q));
            const d = await res.json();
            if (!d.success) {
                showAlert(d.message || '搜索失败', 'danger');
                return;
            }
            if (!d.data || d.data.length === 0) {
                showAlert('没搜到匹配项', 'warning');
                return;
            }

            const list = document.createElement('div');
            list.className = 'list-group mt-2';
            d.data.forEach((item) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'list-group-item list-group-item-action';
                btn.innerHTML = `<div class="fw-bold">${item.name || '(未命名)'}</div><div class="small text-muted">${item.sku}</div>`;
                btn.addEventListener('click', () => {
                    // 清空搜索框
                    const searchInput = document.getElementById('manualSearchInput');
                    if (searchInput) searchInput.value = '';
                    
                    // 清空搜索结果
                    const searchResults = document.getElementById('manualSearchResults');
                    if (searchResults) searchResults.innerHTML = '';
                    
                    // 执行商品搜索
                    searchSKU(item.sku);
                });
                list.appendChild(btn);
            });
            box.appendChild(list);
        }

        function updatePendingList() {
            const div = document.getElementById('pendingList');
            const btn = document.getElementById('submitSessionBtn');
            div.innerHTML = '';
            if(pendingData.length === 0) {
                btn.disabled = true;
                return;
            }
            btn.disabled = false;
            pendingData.forEach((item, idx) => {
                const el = document.createElement('div');
                el.className = 'pending-item';
                el.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${item.sku}</strong> ${item.name}
                            <br><small class="text-muted">${item.batches.length} 个批次</small>
                        </div>
                        <button class="btn btn-sm btn-outline-danger" onclick="pendingData.splice(${idx},1);updatePendingList()">×</button>
                    </div>
                `;
                div.appendChild(el);
            });
        }
        async function loadPast() {
            const res = await fetch('index.php?api=get_past_sessions');
            const d = await res.json();
            const div = document.getElementById('sessionList');
            div.innerHTML = '';
            d.data.forEach(s => {
                const card = document.createElement('div');
                card.className = 'custom-card';
                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>单号: ${s.session_key}</strong>
                            <br><small class="text-muted">${s.created_at}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${s.item_count} 件</span>
                            <button class="btn btn-sm btn-outline-primary ms-2" onclick="editSession('${s.session_key}', event)" title="编辑盘点单">
                                <i class="bi bi-pencil"></i> 编辑
                            </button>
                            <button class="btn btn-sm btn-outline-danger ms-1" onclick="deleteInventorySession('${s.session_key}', event)" title="删除盘点单">
                                <i class="bi bi-trash"></i> 删除
                            </button>
                        </div>
                    </div>
                `;
                card.style.cursor = 'pointer';
                card.addEventListener('click', async() => {
                    const res = await fetch(`index.php?api=get_session_details&session_id=${s.session_key}`);
                    const d = await res.json();
                    
                    // 保存当前盘点单数据
                    currentInventoryData = {
                        session_id: s.session_key,
                        session_title: s.session_title || `盘点单 ${s.created_at}`,
                        items: d.data,
                        created_at: s.created_at
                    };
                    
                    const tbody = document.getElementById('inventoryDetailBody');
                    tbody.innerHTML = '';
                    d.data.forEach(item => {
                        tbody.innerHTML += `<tr><td>${item.sku}</td><td>${item.expiry_date}</td><td>${item.quantity}</td></tr>`;
                    });
                    new bootstrap.Modal(document.getElementById('detailModal')).show();
                });
                div.appendChild(card);
            });
        }

        // ========================================
        // 编辑盘点单功能
        // ========================================

        /**
         * 进入编辑模式
         */
        async function editSession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件

            try {
                const res = await fetch(`index.php?api=get_editable_session&session_id=${sessionId}`);
                const d = await res.json();

                if (!d.success) {
                    showAlert('❌ ' + (d.message || '加载失败'), 'danger');
                    return;
                }

                // 保存当前编辑的盘点单数据
                window.currentEditSession = {
                    session_id: d.data.session_id,
                    session_key: d.data.session_id, // 保持一致性
                    items: d.data.items,
                    item_count: d.data.item_count
                };

                // 显示编辑界面
                showEditInterface(d.data);

            } catch (error) {
                console.error('加载编辑数据失败:', error);
                showAlert('❌ 加载失败，请稍后重试', 'danger');
            }
        }

        /**
         * 显示编辑界面
         */
        function showEditInterface(data) {
            // 隐藏其他视图，显示编辑视图
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            let editView = document.getElementById('editView');
            if (!editView) {
                // 如果编辑视图不存在，创建它
                createEditView();
                editView = document.getElementById('editView');
            }

            editView.classList.add('active');

            // 填充数据
            const tbody = document.getElementById('editTableBody');
            tbody.innerHTML = '';

            data.items.forEach((item, index) => {
                const row = document.createElement('tr');
                row.dataset.batchId = item.batch_id;
                row.innerHTML = `
                    <td>
                        <strong>${item.name || ''}</strong><br>
                        <small class="text-muted">${item.sku || ''}</small>
                    </td>
                    <td>
                        <input type="date" class="form-control form-control-sm" value="${item.expiry_date || ''}" id="edit-expiry-${index}">
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm" value="${item.quantity || 0}" min="1" id="edit-qty-${index}">
                    </td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="saveBatchEdit(${item.batch_id}, ${index})">
                            <i class="bi bi-check"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteBatchItem(${item.batch_id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // 更新商品数量显示
            document.getElementById('editItemCount').innerText = data.item_count;
            document.getElementById('editSessionId').innerText = data.session_id;
        }

        /**
         * 创建编辑视图HTML（首次使用时创建）
         */
        function createEditView() {
            const editHtml = `
                <div id="editView" class="view-section">
                    <div class="app-header">
                        <div class="container">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-pencil-square me-2"></i>编辑盘点单
                                </h5>
                                <button class="btn btn-outline-secondary btn-sm" onclick="cancelEdit()">
                                    <i class="bi bi-arrow-left me-1"></i>返回
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="container mt-4">
                        <div class="custom-card">
                            <h6 class="mb-3">盘点单信息</h6>
                            <p class="mb-1">
                                <strong>单号:</strong> <span id="editSessionId"></span>
                            </p>
                            <p class="mb-0">
                                <strong>商品数量:</strong> <span id="editItemCount">0</span> 件
                            </p>
                        </div>

                        <div class="custom-card">
                            <h6 class="mb-3">商品列表</h6>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>商品</th>
                                            <th>有效期</th>
                                            <th>数量</th>
                                            <th>操作</th>
                                        </tr>
                                    </thead>
                                    <tbody id="editTableBody"></tbody>
                                </table>
                            </div>

                            <div class="mt-3">
                                <button class="btn btn-success w-100" onclick="showAddProductModal()">
                                    <i class="bi bi-plus-circle me-1"></i>添加商品
                                </button>
                            </div>
                        </div>

                        <div class="custom-card">
                            <button class="btn btn-primary w-100" onclick="finishEdit()">
                                <i class="bi bi-check-circle me-1"></i>完成编辑
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // 插入到主内容区域
            const mainContent = document.querySelector('body');
            if (mainContent) {
                const editDiv = document.createElement('div');
                editDiv.innerHTML = editHtml;
                mainContent.appendChild(editDiv.firstElementChild);
            }
        }

        /**
         * 保存批次编辑
         */
        async function saveBatchEdit(batchId, index) {
            const expiryDate = document.getElementById(`edit-expiry-${index}`).value;
            const quantity = parseInt(document.getElementById(`edit-qty-${index}`).value);

            if (!expiryDate) {
                showAlert('❌ 请选择有效期', 'danger');
                return;
            }

            if (quantity <= 0 || !Number.isInteger(quantity)) {
                showAlert('❌ 数量必须大于0的整数', 'danger');
                return;
            }

            try {
                const res = await fetch('index.php?api=update_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        batch_id: batchId,
                        expiry_date: expiryDate,
                        quantity: quantity
                    })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 保存成功', 'success');
                    // 重新加载当前编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '保存失败'), 'danger');
                }
            } catch (error) {
                console.error('保存失败:', error);
                showAlert('❌ 保存失败，请稍后重试', 'danger');
            }
        }

        /**
         * 删除批次
         */
        async function deleteBatchItem(batchId) {
            if (!confirm('确定要删除这个商品吗？')) {
                return;
            }

            try {
                const res = await fetch('index.php?api=delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ batch_id: batchId })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 删除成功', 'success');
                    // 重新加载当前编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }

        /**
         * 显示添加商品模态框
         */

        /**
         * 取消编辑，返回往期盘点列表
         */
        function cancelEdit() {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            const portalView = document.getElementById('portalView');
            if (portalView) {
                portalView.classList.add('active');
            }
            loadPast(); // 重新加载列表
        }

        /**
         * 完成编辑
         */
        function finishEdit() {
            showAlert('✅ 编辑完成！', 'success');
            cancelEdit();
        }

        /**
         * 在编辑模式下，将扫描的商品添加到盘点单
         */
        async function addProductToSession(sku, expiryDate, quantity) {
            if (!window.currentEditSession) {
                showAlert('❌ 编辑会话丢失，请重新进入编辑模式', 'danger');
                return;
            }

            try {
                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: window.currentEditSession.session_id,
                        sku: sku,
                        batches: [{
                            expiry_date: expiryDate,
                            quantity: quantity
                        }]
                    })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');
                    // 重新加载编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加失败，请稍后重试', 'danger');
            }
        }

        async function refreshHealth() {
            const res = await fetch('api.php?endpoint=summary');
            const d = await res.json();
            document.getElementById('val-expired').innerText = d.summary.expired;
            document.getElementById('val-urgent').innerText = d.summary.urgent;
            document.getElementById('val-healthy').innerText = d.summary.healthy;
            const total = d.summary.expired + d.summary.urgent + d.summary.healthy || 1;
            document.getElementById('bar-expired').style.width = (d.summary.expired/total*100)+'%';
            document.getElementById('bar-urgent').style.width = (d.summary.urgent/total*100)+'%';
            document.getElementById('bar-healthy').style.width = (d.summary.healthy/total*100)+'%';
        }
        async function checkUpgrade() {
            const res = await fetch('index.php?api=check_upgrade');
            const d = await res.json();
            if(d.has_update) {
                showAlert('发现新版本: '+d.latest, 'info');
            }
        }
    

function sendInventoryEmail() {
            if (!currentInventoryData || !currentInventoryData.items || currentInventoryData.items.length === 0) {
                showAlert('❌ 没有可发送的数据', 'danger');
                return;
            }
            
            const btn = document.getElementById('sendEmailBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>AI分析中...';
            
            try {
                // 调用AI分析接口
                const analysisRes = await fetch('index.php?api=analyze_inventory', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentInventoryData.session_key
                    })
                });
                
                const analysisData = await analysisRes.json();
                
                if (!analysisData.success) {
                    throw new Error(analysisData.message || 'AI分析失败');
                }
                
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>发送邮件中...';
                
                // 发送邮件
                const res = await fetch('index.php?api=send_inventory_email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentInventoryData.session_key,
                        subject: `AI分析报告 - 盘点单汇总 ${currentInventoryData.session_title}`,
                        analysis: analysisData.analysis,
                        table_html: analysisData.table_html
                    })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ AI分析报告发送成功！', 'success');
                    // 关闭弹窗
                    const modal = bootstrap.Modal.getInstance(document.getElementById('detailModal'));
                    if (modal) modal.hide();
                } else {
                    // 显示详细的错误信息
                    let errorMsg = d.message || '发送失败';
                    if (errorMsg.includes('未设置默认收件邮箱')) {
                        errorMsg += '\n\n请在后台管理 → AI配置 → 盘点单邮件设置 中配置收件邮箱';
                    } else if (errorMsg.includes('邮件功能尚未配置')) {
                        errorMsg += '\n\n请在后台管理 → 邮箱配置 中添加邮箱账户';
                    } else if (errorMsg.includes('AI配置')) {
                        errorMsg += '\n\n请在后台管理 → AI配置 中设置API地址和密钥';
                    }
                    showAlert('❌ ' + errorMsg, 'danger');
                }
            } catch (error) {
                console.error('发送邮件失败:', error);
                let errorMsg = '发送失败，请稍后重试';
                if (error.message) {
                    if (error.message.includes('AI分析')) {
                        errorMsg = error.message + '\n\n请在后台管理 → AI配置 中设置API地址和密钥';
                    } else if (error.message.includes('网络')) {
                        errorMsg = '网络连接失败，请检查网络后重试';
                    }
                }
                showAlert('❌ ' + errorMsg, 'danger');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="bi bi-envelope me-1"></i>AI分析并发送';
            }
        }
        
        async function editSession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件
            
            try {
                const res = await fetch(`index.php?api=get_editable_session&session_id=${sessionId}`);
                const d = await res.json();
                
                if (d.success) {
                    displayEditSession(d.data);
                    const modal = new bootstrap.Modal(document.getElementById('editModal'));
                    modal.show();
                } else {
                    showAlert('❌ ' + (d.message || '获取盘点单详情失败'), 'danger');
                }
            } catch (error) {
                console.error('获取盘点单详情失败:', error);
                showAlert('❌ 获取盘点单详情失败，请稍后重试', 'danger');
            }
        }
        
        function displayEditSession(data) {
            // 保存当前正在编辑的盘点单数据
            window.currentEditSession = {
                session_id: data.session_id || data.session_key,
                session_key: data.session_id || data.session_key, // 保持一致性
                items: data.items,
                item_count: data.item_count
            };
            
            // 显示盘点单信息
            const infoDiv = document.getElementById('editSessionInfo');
            infoDiv.innerHTML = `
                <div class="custom-card">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>单号: ${data.session_key}</strong>
                            <br><small class="text-muted">${data.created_at}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${data.item_count} 件</span>
                        </div>
                    </div>
                </div>
            `;
            
            // 显示商品列表
            const tbody = document.getElementById('editSessionBody');
            tbody.innerHTML = '';
            
            data.items.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'edit-item-row';
                row.dataset.batchId = item.batch_id;
                row.innerHTML = `
                    <td>${item.sku}</td>
                    <td>${item.name}</td>
                    <td><input type="date" class="form-control form-control-sm expiry-input" value="${item.expiry_date}" data-batch-id="${item.batch_id}"></td>
                    <td><input type="number" class="form-control form-control-sm quantity-input" value="${item.quantity}" min="1" data-batch-id="${item.batch_id}"></td>
                    <td>
                        <button class="btn btn-sm btn-outline-danger delete-batch-btn" onclick="deleteBatch(${item.batch_id})" data-batch-id="${item.batch_id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
        
        async function deleteBatch(batchId) {
            if (!confirm('确定要删除这个批次吗？')) {
                return;
            }
            
            try {
                const res = await fetch('index.php?api=delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ batch_id: batchId })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 批次删除成功', 'success');
                    // 重新加载编辑数据
                    editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除批次失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }
        
        function removeBatchRow(button) {
            const row = button.closest('.batch-row');
            if (document.querySelectorAll('#addProductBatchesContainer .batch-row').length > 1) {
                row.remove();
            } else {
                showAlert('至少需要保留一个批次', 'warning');
            }
        }
        
        function showAddProductModal() {
            // 创建添加商品模态框（如果不存在）
            let modal = document.getElementById('editAddProductModal');
            if (!modal) {
                const modalHtml = `
                    <div class="modal fade" id="editAddProductModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">添加商品到盘点单</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <!-- SKU输入区域 -->
                                    <div class="mb-3">
                                        <label class="form-label">商品SKU</label>
                                        <div class="input-group">
                                            <input type="text" class="form-control" id="editAddSkuInput" placeholder="输入SKU或扫码">
                                            <button class="btn btn-outline-secondary" type="button" onclick="startEditScan()">
                                                <i class="bi bi-qr-code-scan"></i> 扫一扫
                                            </button>
                                        </div>
                                        <div id="editAddSkuSuggestions" class="list-group mt-2" style="display:none; max-height: 200px; overflow-y: auto;"></div>
                                    </div>

                                    <!-- 商品信息显示 -->
                                    <div id="editAddProductInfo" class="mb-3" style="display:none;">
                                        <div class="card">
                                            <div class="card-body">
                                                <h6 class="card-title" id="editAddProductName"></h6>
                                                <p class="card-text mb-0">
                                                    <strong>SKU:</strong> <span id="editAddProductSku"></span>
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- 批次信息 -->
                                    <div id="editAddBatchContainer" style="display:none;">
                                        <label class="form-label">批次信息</label>
                                        <div class="batch-row mb-2">
                                            <div class="mb-2">
                                                <label class="form-label small">到期日期</label>
                                                <input type="date" class="form-control form-control-sm" id="editAddExpiryDate">
                                            </div>
                                            <div class="mb-2">
                                                <label class="form-label small">数量</label>
                                                <input type="number" class="form-control form-control-sm" id="editAddQuantity" min="1" value="1">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="button" class="btn btn-primary" onclick="confirmEditAddProduct()">确定添加</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                document.body.insertAdjacentHTML('beforeend', modalHtml);

                // 绑定SKU输入框事件
                const skuInput = document.getElementById('editAddSkuInput');
                skuInput.addEventListener('input', function() {
                    const q = this.value.trim();
                    if (q.length >= 1) { // 减少搜索触发条件
                        searchEditProductSku(q);
                    } else {
                        document.getElementById('editAddSkuSuggestions').style.display = 'none';
                    }
                });
            }

            // 显示模态框
            const bsModal = new bootstrap.Modal(document.getElementById('editAddProductModal'));
            bsModal.show();

            // 重置表单
            document.getElementById('editAddSkuInput').value = '';
            document.getElementById('editAddProductInfo').style.display = 'none';
            document.getElementById('editAddBatchContainer').style.display = 'block'; // 默认为显示
            document.getElementById('editAddSkuSuggestions').style.display = 'none';
            document.getElementById('editAddExpiryDate').value = '';
            document.getElementById('editAddQuantity').value = '1';
        }

        /**
         * 模糊搜索商品（支持SKU和商品名称）
         */
        async function searchEditProductSku(q) {
            try {
                const res = await fetch(`index.php?api=search_products&q=${encodeURIComponent(q)}`);
                const d = await res.json();

                const suggestionsDiv = document.getElementById('editAddSkuSuggestions');
                suggestionsDiv.innerHTML = '';

                if (d.success && d.data && d.data.length > 0) {
                    d.data.forEach(product => {
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.innerHTML = `
                            <div class="d-flex w-100 justify-content-between">
                                <strong>${product.sku}</strong>
                                <small>${product.name}</small>
                            </div>
                        `;
                        item.onclick = (e) => {
                            e.preventDefault();
                            selectEditProduct(product.sku, product.name);
                        };
                        suggestionsDiv.appendChild(item);
                    });
                    suggestionsDiv.style.display = 'block';
                } else {
                    suggestionsDiv.style.display = 'none';
                }
            } catch (error) {
                console.error('搜索失败:', error);
            }
        }

        /**
         * 选择商品
         */
        function selectEditProduct(sku, name) {
            document.getElementById('editAddSkuInput').value = sku;
            document.getElementById('editAddSkuSuggestions').style.display = 'none';

            // 显示商品信息
            document.getElementById('editAddProductName').textContent = name;
            document.getElementById('editAddProductSku').textContent = sku;
            document.getElementById('editAddProductInfo').style.display = 'block';

            // 显示批次输入框
            document.getElementById('editAddBatchContainer').style.display = 'block';
        }

        /**
         * 启动扫描
         */
        function startEditScan() {
            // 设置标志
            window.isEditingAddProduct = true;

            // 隐藏模态框
            const modal = bootstrap.Modal.getInstance(document.getElementById('editAddProductModal'));
            if (modal) {
                modal.hide();
            }

            // 显示扫描界面
            const scanOverlay = document.getElementById('scanOverlay');
            if (scanOverlay) {
                scanOverlay.style.display = 'flex';
                if (typeof startScan === 'function') {
                    startScan();
                }
            }
        }

        /**
         * 确认添加商品
         */
        async function confirmEditAddProduct() {
            const sku = document.getElementById('editAddSkuInput').value.trim();
            const expiryDate = document.getElementById('editAddExpiryDate').value;
            const quantity = parseInt(document.getElementById('editAddQuantity').value);

            if (!sku) {
                showAlert('❌ 请输入商品SKU', 'danger');
                return;
            }

            if (!expiryDate) {
                showAlert('❌ 请选择到期日期', 'danger');
                return;
            }

            if (quantity <= 0) {
                showAlert('❌ 数量必须大于0', 'danger');
                return;
            }

            if (!window.currentEditSession || !window.currentEditSession.session_id) {
                showAlert('❌ 编辑会话丢失，请重新进入编辑模式', 'danger');
                return;
            }

            try {
                const requestData = {
                    session_id: window.currentEditSession.session_id,
                    sku: sku,
                    batches: [{
                        expiry_date: expiryDate,
                        quantity: quantity
                    }]
                };

                console.log('发送请求:', requestData);

                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });

                const d = await res.json();

                console.log('API响应:', d);

                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');

                    // 关闭模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editAddProductModal'));
                    if (modal) {
                        modal.hide();
                    }

                    // 重新加载编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加失败，请稍后重试', 'danger');
            }
        }
        
        async function confirmAddProduct() {
            const sku = document.getElementById('addProductSku').value.trim();
            const batchesContainer = document.getElementById('addProductBatchesContainer');
            const batches = [];
            
            const batchRows = batchesContainer.querySelectorAll('.batch-row');
            batchRows.forEach(row => {
                const expiryDate = row.querySelector('input[type="date"]').value;
                const quantity = parseInt(row.querySelector('.quantity-input').value);
                
                if (expiryDate && quantity > 0) {
                    batches.push({ expiry_date: expiryDate, quantity: quantity });
                }
            });
            
            if (!sku || batches.length === 0) {
                showAlert('❌ 请填写完整的商品信息和至少一个批次', 'danger');
                return;
            }
            
            try {
                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: window.currentEditSession.session_key,
                        sku: sku,
                        batches: batches
                    })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');
                    // 关闭模态框
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addProductModal'));
                    if (modal) modal.hide();
                    
                    // 重新加载编辑数据
                    editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加商品失败，请稍后重试', 'danger');
            }
        }
        
        async function saveEditSession() {
            // 获取所有修改后的行
            const rows = document.querySelectorAll('#editSessionBody tr.edit-item-row');
            const updates = [];
            
            rows.forEach(row => {
                const batchId = row.dataset.batchId;
                const expiryDate = row.querySelector('.expiry-input').value;
                const quantity = parseInt(row.querySelector('.quantity-input').value);
                
                // 获取原始数据
                const originalItem = window.currentEditSession.items.find(item => item.batch_id == batchId);
                
                if (originalItem.expiry_date !== expiryDate || originalItem.quantity !== quantity) {
                    updates.push({ batch_id: batchId, expiry_date: expiryDate, quantity: quantity });
                }
            });
            
            if (updates.length === 0) {
                showAlert('✅ 没有需要保存的修改', 'success');
                return;
            }
            
            // 保存所有修改
            let allSuccess = true;
            let errors = [];
            
            for (const update of updates) {
                try {
                    const res = await fetch('index.php?api=update_batch', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(update)
                    });
                    
                    const d = await res.json();
                    
                    if (!d.success) {
                        allSuccess = false;
                        errors.push(`批次 ${update.batch_id} 保存失败: ${d.message}`);
                    }
                } catch (error) {
                    allSuccess = false;
                    errors.push(`批次 ${update.batch_id} 保存失败: ${error.message}`);
                }
            }
            
            if (allSuccess) {
                showAlert('✅ 所有修改已成功保存', 'success');
                // 重新加载编辑数据
                editSession(window.currentEditSession.session_key, { stopPropagation: () => {} });
            } else {
                showAlert('❌ 部分修改保存失败，请检查错误信息', 'danger');
                console.error('保存失败:', errors);
            }
        }
        
        async function deleteInventorySession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件
            
            if (!confirm('确定要删除这个盘点单吗？删除后无法恢复！')) {
                return;
            }
            
            try {
                const res = await fetch('index.php?api=delete_inventory_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: sessionId })
                });
                
                const d = await res.json();
                
                if (d.success) {
                    showAlert('✅ 盘点单删除成功', 'success');
                    loadPast(); // 重新加载列表
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除盘点单失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }
        document.addEventListener('DOMContentLoaded', () => {
            // 加载草稿数据
            loadDraft();
            
            if(document.getElementById('portalView')) { refreshHealth(); loadCats(); checkUpgrade(); }
            document.getElementById('loginForm')?.addEventListener('submit', async(e)=>{ 
                e.preventDefault(); 
                const res = await fetch('index.php?api=login',{
                    method:'POST', 
                    body:JSON.stringify({
                        username:document.getElementById('loginUser').value, 
                        password:document.getElementById('loginPass').value
                    })
                }); 
                if((await res.json()).success) location.reload(); 
                else showAlert('账号或密码错误','danger'); 
            });
            document.getElementById('logoutBtn')?.addEventListener('click', async () => { 
                await fetch('index.php?api=logout'); 
                location.reload(); 
            });
            document.getElementById('startScanBtn')?.addEventListener('click', ()=>{ 
                document.getElementById('scanOverlay').style.display='flex'; 
                if(!html5QrCode) html5QrCode = new Html5Qrcode("reader");
                html5QrCode.start(
                    {facingMode:"environment"},
                    {fps:10, qrbox:{width:250, height:250}},
                    (text)=>{
                        html5QrCode.stop();
                        document.getElementById('scanOverlay').style.display='none';
                        searchSKU(text);
                    }
                ); 
            });
            document.getElementById('stopScanBtn')?.addEventListener('click', ()=>{ 
                if(html5QrCode) html5QrCode.stop(); 
                document.getElementById('scanOverlay').style.display='none'; 
            });
            document.getElementById('addBatchBtn')?.addEventListener('click', ()=>addBatchRow());

            // 手动输入 / 模糊搜索
            document.getElementById('manualSearchBtn')?.addEventListener('click', ()=>manualSearch());
            document.getElementById('manualSearchInput')?.addEventListener('keydown', (e)=>{
                if (e.key === 'Enter') {
                    e.preventDefault();
                    manualSearch();
                }
            });
            
            // 添加商品到盘点单模态框事件
            document.getElementById('addProductBatchBtn')?.addEventListener('click', ()=>{
                const container = document.getElementById('addProductBatchesContainer');
                const batchCount = container.querySelectorAll('.batch-row').length;
                const newBatchRow = document.createElement('div');
                newBatchRow.className = 'batch-row mb-2';
                newBatchRow.innerHTML = `
                    <input type="date" class="form-control form-control-sm mb-1" id="addProductExpiry${batchCount+1}" required>
                    <input type="number" class="form-control form-control-sm quantity-input" id="addProductQuantity${batchCount+1}" placeholder="数量" min="1" required>
                    <button type="button" class="btn btn-outline-danger btn-sm mt-1 remove-batch-btn" onclick="removeBatchRow(this)">
                        - 批次
                    </button>
                `;
                container.appendChild(newBatchRow);
            });
            
            document.getElementById('confirmAddProductBtn')?.addEventListener('click', confirmAddProduct);

            // 草稿操作按钮
            document.getElementById('saveDraftBtn')?.addEventListener('click', () => {
                saveDraft();
            });
            
            document.getElementById('clearDraftBtn')?.addEventListener('click', () => {
                if (confirm('确定要清空所有草稿数据吗？此操作不可恢复！')) {
                    pendingData = [];
                    clearDraft();
                    updatePendingList();
                    showAlert('🗑️ 草稿已清空', 'info');
                }
            });

            document.getElementById('confirmEntryBtn')?.addEventListener('click', ()=>{
                const batches = []; 
                document.querySelectorAll('.batch-row').forEach(r=>{ 
                    batches.push({
                        expiry_date:r.querySelector('.e-in').value, 
                        quantity:r.querySelector('.q-in').value
                    }); 
                });
                pendingData.push({
                    sku:document.getElementById('sku').value, 
                    name:document.getElementById('productName').value, 
                    category_id:document.getElementById('categoryId').value, 
                    removal_buffer:document.getElementById('removalBuffer').value, 
                    batches, 
                    session_id:currentSessionId
                });
                updatePendingList();
                saveDraft();  // 自动保存草稿
                bootstrap.Modal.getInstance(document.getElementById('entryModal')).hide();
            });
            document.getElementById('submitSessionBtn')?.addEventListener('click', async()=>{
                for(let item of pendingData) {
                    await fetch('index.php?api=save_product',{
                        method:'POST', 
                        body:JSON.stringify(item)
                    });
                }
                await fetch('index.php?api=submit_session',{
                    method:'POST', 
                    body:JSON.stringify({session_id:currentSessionId})
                });
                showAlert('提交成功','success'); 
                pendingData=[]; 
                currentSessionId='S'+Date.now(); 
                clearDraft();  // 清空草稿
                updatePendingList(); 
                switchView('portal'); 
                refreshHealth();
            });
        });
        async function searchSKU(qrCode) {
            // 清空搜索框和搜索结果（无论从哪里调用都清空）
            const searchInput = document.getElementById('manualSearchInput');
            if (searchInput) searchInput.value = '';
            
            const searchResults = document.getElementById('manualSearchResults');
            if (searchResults) searchResults.innerHTML = '';
            
            // 从二维码中提取SKU
            let sku = qrCode;
            let expiryDateFromQR = null;

            console.log('扫码内容:', qrCode);

            // 格式1: 星巴克URL格式
            // https://artwork.starbucks.com.cn/mobile/gtin/xxx/cii1/00+SKU+生产日期&生产日期&到期日期
            if (qrCode.includes('artwork.starbucks.com.cn')) {
                try {
                    const url = new URL(qrCode);
                    const pathParts = url.pathname.split('/');
                    const ciiIndex = pathParts.indexOf('cii1');

                    if (ciiIndex !== -1 && ciiIndex + 1 < pathParts.length) {
                        let ciiData = pathParts[ciiIndex + 1]; // 00+SKU+生产日期&生产日期&到期日期

                        // 分离所有&后的部分（可能有多个日期）
                        const ampParts = ciiData.split('&');
                        ciiData = ampParts[0]; // 第一部分：00+SKU+生产日期

                        // 提取最后一个日期（到期日期）
                        const lastPart = ampParts[ampParts.length - 1];
                        if (lastPart.length === 8 && /^\d+$/.test(lastPart)) {
                            const year = lastPart.substring(0, 4);
                            const month = lastPart.substring(4, 6);
                            const day = lastPart.substring(6, 8);
                            expiryDateFromQR = `${year}-${month}-${day}`;
                        }

                        // 去掉00前缀
                        if (ciiData.startsWith('00')) {
                            ciiData = ciiData.substring(2);
                        }

                        // 提取SKU（前8位）
                        if (ciiData.length >= 8) {
                            sku = ciiData.substring(0, 8);
                        }

                        console.log('星巴克URL解析:', { sku, expiryDate: expiryDateFromQR });
                    }
                } catch (e) {
                    console.error('解析星巴克URL失败:', e);
                }
            }
            // 格式2: 纯数字格式
            // 00 + SKU(8位) + 生产日期(8位) # 生产日期 # 到期日期
            else if (qrCode.includes('#')) {
                const parts = qrCode.split('#');
                if (parts.length >= 3) {
                    let part1 = parts[0]; // 00 + SKU + 生产日期

                    // 去掉前缀 "00"
                    if (part1.startsWith('00')) {
                        part1 = part1.substring(2);
                    }

                    // 提取SKU（前8位）
                    if (part1.length >= 8) {
                        sku = part1.substring(0, 8);
                    }

                    // 解析到期日期（第三部分）
                    let expiryDatePart = parts[2];
                    if (expiryDatePart.length === 8 && /^\d+$/.test(expiryDatePart)) {
                        const year = expiryDatePart.substring(0, 4);
                        const month = expiryDatePart.substring(4, 6);
                        const day = expiryDatePart.substring(6, 8);
                        expiryDateFromQR = `${year}-${month}-${day}`;
                    }

                    console.log('纯数字格式解析:', { sku, expiryDate: expiryDateFromQR });
                }
            }
            // 格式3: 纯SKU（没有日期）
            else {
                sku = qrCode.trim();
                console.log('纯SKU格式:', { sku });
            }

            // 查询商品信息
            const res = await fetch('index.php?api=get_product&sku='+encodeURIComponent(sku));
            const d = await res.json();
            document.getElementById('productForm').reset();
            document.getElementById('batchesContainer').innerHTML='';
            document.getElementById('sku').value = sku; // 显示提取后的纯SKU
            const fields = ['categoryId','productName','removalBuffer'];

            if(d.exists) {
                document.getElementById('productName').value=d.product.name;
                document.getElementById('categoryId').value=d.product.category_id;
                document.getElementById('removalBuffer').value=d.product.removal_buffer;
                fields.forEach(f => {
                    document.getElementById(f).readOnly=true;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=true;
                });
            } else {
                fields.forEach(f => {
                    document.getElementById(f).readOnly=false;
                    if(document.getElementById(f).tagName==='SELECT')
                        document.getElementById(f).disabled=false;
                });
            }
            addBatchRow(expiryDateFromQR);
            new bootstrap.Modal(document.getElementById('entryModal')).show();
        }
        function addBatchRow(defaultExpiryDate = null) {
            const row = document.createElement('div');
            row.className = 'batch-row input-group input-group-sm mb-2';
            row.innerHTML = `
                <span class="input-group-text">效期</span>
                <input type="date" class="form-control e-in" ${defaultExpiryDate ? `value="${defaultExpiryDate}"` : ''} required>
                <span class="input-group-text">数</span>
                <input type="number" class="form-control q-in" placeholder="数量" required>
                <button class="btn btn-outline-danger" onclick="this.parentElement.remove()">×</button>
            `;
            document.getElementById('batchesContainer').appendChild(row);
        }
        async function loadCats() {
            const res = await fetch('api.php?endpoint=categories');
            const d = await res.json();
            const sel = document.getElementById('categoryId');
            sel.innerHTML = '<option value="0">无分类</option>';
            d.categories.forEach(c => {
                sel.innerHTML += `<option value="${c.id}">${c.name}</option>`;
            });
        }
        async function manualSearch() {
            const q = (document.getElementById('manualSearchInput')?.value || '').trim();
            const box = document.getElementById('manualSearchResults');
            if (!box) return;
            box.innerHTML = '';
            if (!q) {
                showAlert('请输入SKU片段或品名关键词', 'warning');
                return;
            }

            // 如果用户粘贴了整段二维码（包含#），直接走录入流程
            if (q.includes('#')) {
                // 清空搜索框和结果
                const searchInput = document.getElementById('manualSearchInput');
                if (searchInput) searchInput.value = '';
                box.innerHTML = '';
                
                searchSKU(q);
                return;
            }

            const res = await fetch('index.php?api=search_products&q=' + encodeURIComponent(q));
            const d = await res.json();
            if (!d.success) {
                showAlert(d.message || '搜索失败', 'danger');
                return;
            }
            if (!d.data || d.data.length === 0) {
                showAlert('没搜到匹配项', 'warning');
                return;
            }

            const list = document.createElement('div');
            list.className = 'list-group mt-2';
            d.data.forEach((item) => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'list-group-item list-group-item-action';
                btn.innerHTML = `<div class="fw-bold">${item.name || '(未命名)'}</div><div class="small text-muted">${item.sku}</div>`;
                btn.addEventListener('click', () => {
                    // 清空搜索框
                    const searchInput = document.getElementById('manualSearchInput');
                    if (searchInput) searchInput.value = '';
                    
                    // 清空搜索结果
                    const searchResults = document.getElementById('manualSearchResults');
                    if (searchResults) searchResults.innerHTML = '';
                    
                    // 执行商品搜索
                    searchSKU(item.sku);
                });
                list.appendChild(btn);
            });
            box.appendChild(list);
        }

        function updatePendingList() {
            const div = document.getElementById('pendingList');
            const btn = document.getElementById('submitSessionBtn');
            div.innerHTML = '';
            if(pendingData.length === 0) {
                btn.disabled = true;
                return;
            }
            btn.disabled = false;
            pendingData.forEach((item, idx) => {
                const el = document.createElement('div');
                el.className = 'pending-item';
                el.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${item.sku}</strong> ${item.name}
                            <br><small class="text-muted">${item.batches.length} 个批次</small>
                        </div>
                        <button class="btn btn-sm btn-outline-danger" onclick="pendingData.splice(${idx},1);updatePendingList()">×</button>
                    </div>
                `;
                div.appendChild(el);
            });
        }
        async function loadPast() {
            const res = await fetch('index.php?api=get_past_sessions');
            const d = await res.json();
            const div = document.getElementById('sessionList');
            div.innerHTML = '';
            d.data.forEach(s => {
                const card = document.createElement('div');
                card.className = 'custom-card';
                card.innerHTML = `
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>单号: ${s.session_key}</strong>
                            <br><small class="text-muted">${s.created_at}</small>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-primary">${s.item_count} 件</span>
                            <button class="btn btn-sm btn-outline-primary ms-2" onclick="editSession('${s.session_key}', event)" title="编辑盘点单">
                                <i class="bi bi-pencil"></i> 编辑
                            </button>
                            <button class="btn btn-sm btn-outline-danger ms-1" onclick="deleteInventorySession('${s.session_key}', event)" title="删除盘点单">
                                <i class="bi bi-trash"></i> 删除
                            </button>
                        </div>
                    </div>
                `;
                card.style.cursor = 'pointer';
                card.addEventListener('click', async() => {
                    const res = await fetch(`index.php?api=get_session_details&session_id=${s.session_key}`);
                    const d = await res.json();
                    
                    // 保存当前盘点单数据
                    currentInventoryData = {
                        session_id: s.session_key,
                        session_title: s.session_title || `盘点单 ${s.created_at}`,
                        items: d.data,
                        created_at: s.created_at
                    };
                    
                    const tbody = document.getElementById('inventoryDetailBody');
                    tbody.innerHTML = '';
                    d.data.forEach(item => {
                        tbody.innerHTML += `<tr><td>${item.sku}</td><td>${item.expiry_date}</td><td>${item.quantity}</td></tr>`;
                    });
                    new bootstrap.Modal(document.getElementById('detailModal')).show();
                });
                div.appendChild(card);
            });
        }

        // ========================================
        // 编辑盘点单功能
        // ========================================

        /**
         * 进入编辑模式
         */
        async function editSession(sessionId, event) {
            event.stopPropagation(); // 阻止触发卡片点击事件

            try {
                const res = await fetch(`index.php?api=get_editable_session&session_id=${sessionId}`);
                const d = await res.json();

                if (!d.success) {
                    showAlert('❌ ' + (d.message || '加载失败'), 'danger');
                    return;
                }

                // 保存当前编辑的盘点单数据
                window.currentEditSession = {
                    session_id: d.data.session_id,
                    session_key: d.data.session_id, // 保持一致性
                    items: d.data.items,
                    item_count: d.data.item_count
                };

                // 显示编辑界面
                showEditInterface(d.data);

            } catch (error) {
                console.error('加载编辑数据失败:', error);
                showAlert('❌ 加载失败，请稍后重试', 'danger');
            }
        }

        /**
         * 显示编辑界面
         */
        function showEditInterface(data) {
            // 隐藏其他视图，显示编辑视图
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            let editView = document.getElementById('editView');
            if (!editView) {
                // 如果编辑视图不存在，创建它
                createEditView();
                editView = document.getElementById('editView');
            }

            editView.classList.add('active');

            // 填充数据
            const tbody = document.getElementById('editTableBody');
            tbody.innerHTML = '';

            data.items.forEach((item, index) => {
                const row = document.createElement('tr');
                row.dataset.batchId = item.batch_id;
                row.innerHTML = `
                    <td>
                        <strong>${item.name || ''}</strong><br>
                        <small class="text-muted">${item.sku || ''}</small>
                    </td>
                    <td>
                        <input type="date" class="form-control form-control-sm" value="${item.expiry_date || ''}" id="edit-expiry-${index}">
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm" value="${item.quantity || 0}" min="1" id="edit-qty-${index}">
                    </td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="saveBatchEdit(${item.batch_id}, ${index})">
                            <i class="bi bi-check"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteBatchItem(${item.batch_id})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });

            // 更新商品数量显示
            document.getElementById('editItemCount').innerText = data.item_count;
            document.getElementById('editSessionId').innerText = data.session_id;
        }

        /**
         * 创建编辑视图HTML（首次使用时创建）
         */
        function createEditView() {
            const editHtml = `
                <div id="editView" class="view-section">
                    <div class="app-header">
                        <div class="container">
                            <div class="d-flex justify-content-between align-items-center">
                                <h5 class="mb-0">
                                    <i class="bi bi-pencil-square me-2"></i>编辑盘点单
                                </h5>
                                <button class="btn btn-outline-secondary btn-sm" onclick="cancelEdit()">
                                    <i class="bi bi-arrow-left me-1"></i>返回
                                </button>
                            </div>
                        </div>
                    </div>

                    <div class="container mt-4">
                        <div class="custom-card">
                            <h6 class="mb-3">盘点单信息</h6>
                            <p class="mb-1">
                                <strong>单号:</strong> <span id="editSessionId"></span>
                            </p>
                            <p class="mb-0">
                                <strong>商品数量:</strong> <span id="editItemCount">0</span> 件
                            </p>
                        </div>

                        <div class="custom-card">
                            <h6 class="mb-3">商品列表</h6>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>商品</th>
                                            <th>有效期</th>
                                            <th>数量</th>
                                            <th>操作</th>
                                        </tr>
                                    </thead>
                                    <tbody id="editTableBody"></tbody>
                                </table>
                            </div>

                            <div class="mt-3">
                                <button class="btn btn-success w-100" onclick="showAddProductModal()">
                                    <i class="bi bi-plus-circle me-1"></i>添加商品
                                </button>
                            </div>
                        </div>

                        <div class="custom-card">
                            <button class="btn btn-primary w-100" onclick="finishEdit()">
                                <i class="bi bi-check-circle me-1"></i>完成编辑
                            </button>
                        </div>
                    </div>
                </div>
            `;

            // 插入到主内容区域
            const mainContent = document.querySelector('body');
            if (mainContent) {
                const editDiv = document.createElement('div');
                editDiv.innerHTML = editHtml;
                mainContent.appendChild(editDiv.firstElementChild);
            }
        }

        /**
         * 保存批次编辑
         */
        async function saveBatchEdit(batchId, index) {
            const expiryDate = document.getElementById(`edit-expiry-${index}`).value;
            const quantity = parseInt(document.getElementById(`edit-qty-${index}`).value);

            if (!expiryDate) {
                showAlert('❌ 请选择有效期', 'danger');
                return;
            }

            if (quantity <= 0 || !Number.isInteger(quantity)) {
                showAlert('❌ 数量必须大于0的整数', 'danger');
                return;
            }

            try {
                const res = await fetch('index.php?api=update_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        batch_id: batchId,
                        expiry_date: expiryDate,
                        quantity: quantity
                    })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 保存成功', 'success');
                    // 重新加载当前编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '保存失败'), 'danger');
                }
            } catch (error) {
                console.error('保存失败:', error);
                showAlert('❌ 保存失败，请稍后重试', 'danger');
            }
        }

        /**
         * 删除批次
         */
        async function deleteBatchItem(batchId) {
            if (!confirm('确定要删除这个商品吗？')) {
                return;
            }

            try {
                const res = await fetch('index.php?api=delete_batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ batch_id: batchId })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 删除成功', 'success');
                    // 重新加载当前编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '删除失败'), 'danger');
                }
            } catch (error) {
                console.error('删除失败:', error);
                showAlert('❌ 删除失败，请稍后重试', 'danger');
            }
        }

        /**
         * 显示添加商品模态框
         */

        /**
         * 取消编辑，返回往期盘点列表
         */
        function cancelEdit() {
            document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
            const portalView = document.getElementById('portalView');
            if (portalView) {
                portalView.classList.add('active');
            }
            loadPast(); // 重新加载列表
        }

        /**
         * 完成编辑
         */
        function finishEdit() {
            showAlert('✅ 编辑完成！', 'success');
            cancelEdit();
        }

        /**
         * 在编辑模式下，将扫描的商品添加到盘点单
         */
        async function addProductToSession(sku, expiryDate, quantity) {
            if (!window.currentEditSession) {
                showAlert('❌ 编辑会话丢失，请重新进入编辑模式', 'danger');
                return;
            }

            try {
                const res = await fetch('index.php?api=add_to_session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: window.currentEditSession.session_id,
                        sku: sku,
                        batches: [{
                            expiry_date: expiryDate,
                            quantity: quantity
                        }]
                    })
                });

                const d = await res.json();

                if (d.success) {
                    showAlert('✅ 商品添加成功', 'success');
                    // 重新加载编辑界面
                    const sessionId = window.currentEditSession.session_id;
                    editSession(sessionId, { stopPropagation: () => {} });
                } else {
                    showAlert('❌ ' + (d.message || '添加失败'), 'danger');
                }
            } catch (error) {
                console.error('添加商品失败:', error);
                showAlert('❌ 添加失败，请稍后重试', 'danger');
            }
        }

        async function refreshHealth() {
            const res = await fetch('api.php?endpoint=summary');
            const d = await res.json();
            document.getElementById('val-expired').innerText = d.summary.expired;
            document.getElementById('val-urgent').innerText = d.summary.urgent;
            document.getElementById('val-healthy').innerText = d.summary.healthy;
            const total = d.summary.expired + d.summary.urgent + d.summary.healthy || 1;
            document.getElementById('bar-expired').style.width = (d.summary.expired/total*100)+'%';
            document.getElementById('bar-urgent').style.width = (d.summary.urgent/total*100)+'%';
            document.getElementById('bar-healthy').style.width = (d.summary.healthy/total*100)+'%';
        }
        async function checkUpgrade() {
            const res = await fetch('index.php?api=check_upgrade');
            const d = await res.json();
            if(d.has_update) {
                showAlert('发现新版本: '+d.latest, 'info');
            }
        }
    

        async function checkUpgrade() {
            const res = await fetch('index.php?api=check_upgrade');
            const d = await res.json();
            if(d.has_update) {
                showAlert('发现新版本: '+d.latest, 'info');
            }
        }
    </script>
        <?php endif; ?>
</body>
</html>
