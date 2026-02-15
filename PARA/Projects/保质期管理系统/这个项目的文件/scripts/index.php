<?php
/**
 * ========================================
 * 保质期管理系统 - 主页面（完整版）
 * 文件名: index.php
 * 版本: v1.1.0
 * 创建日期: 2026-02-15
 * ========================================
 * 功能说明：
 * 1. 扫码录入商品批次信息 (含成功提示音)
 * 2. 动态添加/删除批次
 * 3. 商品查询和回显
 * 4. 批次到期状态提醒
 * 5. 数据统计和导出 (AI 整理排序)
 * 6. 在线一键升级功能
 * ========================================
 */

// 升级配置
define('APP_VERSION', '1.1.0');
define('UPDATE_URL', 'https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/main/');

// 启动 Session
session_start();

// 引入数据库连接文件
require_once 'db.php';

// ========================================
// PHP 后端 API 处理
// ========================================

// 处理 AJAX 请求
if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    $action = $_GET['api'];
    
    // 获取数据库连接
    $conn = getDBConnection();
    if (!$conn) {
        echo json_encode([
            'success' => false,
            'message' => '数据库连接失败，请联系管理员'
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // ========================================
    // API 1: 根据 SKU 查询商品信息
    // ========================================
    if ($action === 'get_product') {
        $sku = isset($_GET['sku']) ? trim($_GET['sku']) : '';
        
        if (empty($sku)) {
            echo json_encode([
                'success' => false,
                'message' => 'SKU 不能为空'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 使用预处理语句防止 SQL 注入
        $stmt = $conn->prepare("SELECT id, sku, name, created_at FROM products WHERE sku = ? LIMIT 1");
        $stmt->bind_param("s", $sku);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            $product = $result->fetch_assoc();
            $productId = $product['id'];
            
            // 查询该商品的所有批次
            $stmt_batch = $conn->prepare("
                SELECT id, expiry_date, quantity, created_at 
                FROM batches 
                WHERE product_id = ? 
                ORDER BY expiry_date ASC
            ");
            $stmt_batch->bind_param("i", $productId);
            $stmt_batch->execute();
            $batch_result = $stmt_batch->get_result();
            
            $batches = [];
            while ($batch = $batch_result->fetch_assoc()) {
                // 计算到期天数
                $expiryDate = $batch['expiry_date'];
                $today = date('Y-m-d');
                $daysToExpiry = (strtotime($expiryDate) - strtotime($today)) / 86400;
                
                $batches[] = [
                    'id' => $batch['id'],
                    'expiry_date' => $expiryDate,
                    'quantity' => (int)$batch['quantity'],
                    'days_to_expiry' => (int)$daysToExpiry,
                    'status' => $daysToExpiry < 0 ? 'expired' : ($daysToExpiry <= 30 ? 'warning' : 'normal')
                ];
            }
            
            echo json_encode([
                'success' => true,
                'exists' => true,
                'product' => [
                    'id' => $product['id'],
                    'sku' => $product['sku'],
                    'name' => $product['name']
                ],
                'batches' => $batches,
                'message' => '查询成功'
            ], JSON_UNESCAPED_UNICODE);
        } else {
            // 商品不存在
            echo json_encode([
                'success' => true,
                'exists' => false,
                'message' => '新商品，请输入商品名称'
            ], JSON_UNESCAPED_UNICODE);
        }
        exit;
    }
    
    // ========================================
    // API 2: 保存商品和批次信息
    // ========================================
    if ($action === 'save_product') {
        // 只接受 POST 请求
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            echo json_encode([
                'success' => false,
                'message' => '请求方法错误'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 获取 JSON 数据
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        
        $sku = isset($data['sku']) ? trim($data['sku']) : '';
        $name = isset($data['name']) ? trim($data['name']) : '';
        $batches = isset($data['batches']) ? $data['batches'] : [];
        
        // 数据验证
        if (empty($sku)) {
            echo json_encode([
                'success' => false,
                'message' => 'SKU 不能为空'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        if (empty($name)) {
            echo json_encode([
                'success' => false,
                'message' => '商品名称不能为空'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        if (empty($batches) || !is_array($batches)) {
            echo json_encode([
                'success' => false,
                'message' => '至少需要添加一个批次'
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 验证批次数据
        foreach ($batches as $index => $batch) {
            if (empty($batch['expiry_date'])) {
                echo json_encode([
                    'success' => false,
                    'message' => "第 " . ($index + 1) . " 个批次的到期日期不能为空"
                ], JSON_UNESCAPED_UNICODE);
                exit;
            }
            
            if (!isset($batch['quantity']) || $batch['quantity'] < 0) {
                echo json_encode([
                    'success' => false,
                    'message' => "第 " . ($index + 1) . " 个批次的数量无效"
                ], JSON_UNESCAPED_UNICODE);
                exit;
            }
        }
        
        // 开始事务（确保数据一致性）
        $conn->begin_transaction();
        
        try {
            // 检查商品是否已存在
            $stmt_check = $conn->prepare("SELECT id FROM products WHERE sku = ? LIMIT 1");
            $stmt_check->bind_param("s", $sku);
            $stmt_check->execute();
            $check_result = $stmt_check->get_result();
            
            $productId = null;
            
            if ($check_result->num_rows > 0) {
                // 商品已存在，更新名称
                $row = $check_result->fetch_assoc();
                $productId = $row['id'];
                
                $stmt_update = $conn->prepare("UPDATE products SET name = ? WHERE id = ?");
                $stmt_update->bind_param("si", $name, $productId);
                $stmt_update->execute();
                
                // 删除旧批次（根据业务需求，也可以选择保留历史批次）
                $stmt_delete = $conn->prepare("DELETE FROM batches WHERE product_id = ?");
                $stmt_delete->bind_param("i", $productId);
                $stmt_delete->execute();
            } else {
                // 新商品，插入记录
                $stmt_insert = $conn->prepare("INSERT INTO products (sku, name) VALUES (?, ?)");
                $stmt_insert->bind_param("ss", $sku, $name);
                $stmt_insert->execute();
                $productId = $conn->insert_id;
            }
            
            // 批量插入批次数据
            $stmt_batch = $conn->prepare("INSERT INTO batches (product_id, expiry_date, quantity) VALUES (?, ?, ?)");
            
            foreach ($batches as $batch) {
                $expiryDate = $batch['expiry_date'];
                $quantity = (int)$batch['quantity'];
                
                $stmt_batch->bind_param("isi", $productId, $expiryDate, $quantity);
                $stmt_batch->execute();
            }
            
            // 提交事务
            $conn->commit();
            
            // 记录日志
            logError("商品保存成功", [
                'sku' => $sku,
                'name' => $name,
                'batches_count' => count($batches)
            ]);
            
            echo json_encode([
                'success' => true,
                'message' => '保存成功！',
                'product_id' => $productId,
                'batches_added' => count($batches)
            ], JSON_UNESCAPED_UNICODE);
            
        } catch (Exception $e) {
            // 回滚事务
            $conn->rollback();
            
            logError("商品保存失败: " . $e->getMessage(), [
                'sku' => $sku,
                'name' => $name
            ]);
            
            echo json_encode([
                'success' => false,
                'message' => '保存失败：' . $e->getMessage()
            ], JSON_UNESCAPED_UNICODE);
        }
        exit;
    }
    
    // ========================================
    // API 3: 获取统计数据
    // ========================================
    if ($action === 'get_statistics') {
        // 统计商品总数
        $result_products = $conn->query("SELECT COUNT(*) as total FROM products");
        $total_products = $result_products->fetch_assoc()['total'];
        
        // 统计批次总数
        $result_batches = $conn->query("SELECT COUNT(*) as total FROM batches");
        $total_batches = $result_batches->fetch_assoc()['total'];
        
        // 统计即将过期的批次（30天内）
        $stmt_expiry_soon = $conn->prepare("
            SELECT COUNT(*) as total 
            FROM batches 
            WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ");
        $stmt_expiry_soon->execute();
        $expiry_soon = $stmt_expiry_soon->get_result()->fetch_assoc()['total'];
        
        // 统计已过期的批次
        $stmt_expired = $conn->prepare("
            SELECT COUNT(*) as total 
            FROM batches 
            WHERE expiry_date < CURDATE()
        ");
        $stmt_expired->execute();
        $expired = $stmt_expired->get_result()->fetch_assoc()['total'];
        
        echo json_encode([
            'success' => true,
            'statistics' => [
                'total_products' => (int)$total_products,
                'total_batches' => (int)$total_batches,
                'expiry_soon' => (int)$expiry_soon,
                'expired' => (int)$expired
            ]
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // ========================================
    // API 4: 导出盘点表 (CSV 格式)
    // ========================================
    if ($action === 'export_inventory') {
        // 设置 HTTP 头部，触发下载
        $filename = "盘点表_" . date('Ymd_His') . ".csv";
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        
        // 输出 UTF-8 BOM，确保 Excel 打开不乱码
        echo "\xEF\xBB\xBF";
        
        $output = fopen('php://output', 'w');
        
        // 写入表头
        fputcsv($output, ['SKU/条形码', '商品名称', '到期日期', '当前数量', '状态/AI建议']);
        
        // 查询所有商品及其批次，核心：按到期日期升序排列 (AI 整理逻辑)
        // 找到期的放在前面，后到期的放在后面
        $query = "
            SELECT p.sku, p.name, b.expiry_date, b.quantity 
            FROM products p 
            JOIN batches b ON p.id = b.product_id 
            ORDER BY b.expiry_date ASC
        ";
        $result = $conn->query($query);
        
        while ($row = $result->fetch_assoc()) {
            $today = date('Y-m-d');
            $diffDays = (strtotime($row['expiry_date']) - strtotime($today)) / 86400;
            
            // AI 状态整理逻辑
            $ai_status = "";
            if ($diffDays < 0) {
                $ai_status = "🔴 已过期 (请立即下架)";
            } elseif ($diffDays <= 30) {
                $ai_status = "🟡 临期预警 (" . floor($diffDays) . "天内到期)";
            } else {
                $ai_status = "🟢 正常 (" . floor($diffDays) . "天后到期)";
            }
            
            fputcsv($output, [
                $row['sku'],
                $row['name'],
                $row['expiry_date'],
                $row['quantity'],
                $ai_status
            ]);
        }
        
        fclose($output);
        exit;
    }
    
    // ========================================
    // API 5: 检查更新
    // ========================================
    if ($action === 'check_upgrade') {
        $latest_version_url = UPDATE_URL . 'VERSION.txt';
        $latest_version = @file_get_contents($latest_version_url);
        
        if ($latest_version === false) {
            echo json_encode(['success' => false, 'message' => '无法连接到更新服务器']);
        } else {
            $latest_version = trim($latest_version);
            $has_update = version_compare($latest_version, APP_VERSION, '>');
            echo json_encode([
                'success' => true,
                'current' => APP_VERSION,
                'latest' => $latest_version,
                'has_update' => $has_update
            ]);
        }
        exit;
    }

    // ========================================
    // API 6: 执行升级
    // ========================================
    if ($action === 'execute_upgrade') {
        $files = ['index.php', 'db.php', 'install.php'];
        $errors = [];
        
        foreach ($files as $file) {
            $remote_content = @file_get_contents(UPDATE_URL . $file);
            if ($remote_content !== false) {
                if (!@file_put_contents(__DIR__ . '/' . $file, $remote_content)) {
                    $errors[] = "无法写入 $file";
                }
            } else {
                $errors[] = "无法下载 $file";
            }
        }
        
        if (empty($errors)) {
            echo json_encode(['success' => true, 'message' => '升级成功！正在刷新页面...']);
        } else {
            echo json_encode(['success' => false, 'message' => implode(", ", $errors)]);
        }
        exit;
    }

    // 未知的 API 请求
    echo json_encode([
        'success' => false,
        'message' => '未知的 API 请求'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>保质期管理系统 v2.0</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    <!-- html5-qrcode 扫码库 -->
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    
    <style>
        /* ========================================
           全局样式
           ======================================== */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        }
        
        /* ========================================
           头部样式
           ======================================== */
        .app-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        
        .app-header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }
        
        .app-header .subtitle {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }
        
        /* ========================================
           卡片样式
           ======================================== */
        .custom-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: none;
        }
        
        .custom-card .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .custom-card .card-title i {
            color: var(--primary-color);
        }
        
        /* ========================================
           扫码区域样式
           ======================================== */
        #reader {
            width: 100%;
            border-radius: 10px;
            overflow: hidden;
            background: #000;
            min-height: 250px;
        }
        
        #reader video {
            object-fit: cover;
            border-radius: 10px;
        }
        
        .scan-buttons {
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }
        
        .scan-buttons button {
            flex: 1;
            height: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 10px;
        }
        
        .btn-scan {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            color: white;
            transition: all 0.3s ease;
        }
        
        .btn-scan:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            color: white;
        }
        
        /* ========================================
           批次行样式
           ======================================== */
        .batch-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid var(--primary-color);
            transition: all 0.3s ease;
        }
        
        .batch-item:hover {
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transform: translateX(5px);
        }
        
        .batch-item.expired {
            border-left-color: var(--danger-color);
            background: #ffeaea;
        }
        
        .batch-item.warning {
            border-left-color: var(--warning-color);
            background: #fff9e6;
        }
        
        .batch-item .form-label {
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
        }
        
        .batch-item .remove-batch-btn {
            height: 38px;
            margin-top: 0;
        }
        
        /* ========================================
           状态标签样式
           ======================================== */
        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        
        .status-badge.normal {
            background: #d4edda;
            color: #155724;
        }
        
        .status-badge.warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .status-badge.expired {
            background: #f8d7da;
            color: #721c24;
        }
        
        /* ========================================
           统计卡片样式
           ======================================== */
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
        }
        
        .stat-card .stat-label {
            font-size: 0.9rem;
            color: #666;
            margin-top: 5px;
        }
        
        /* ========================================
           提示消息样式
           ======================================== */
        .alert-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            max-width: 400px;
        }
        
        .alert-container .alert {
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
        }
        
        /* ========================================
           响应式设计
           ======================================== */
        @media (max-width: 768px) {
            .app-header h1 {
                font-size: 1.5rem;
            }
            
            .custom-card {
                padding: 15px;
            }
            
            .batch-item {
                padding: 12px;
            }
            
            .stat-card .stat-value {
                font-size: 1.5rem;
            }
        }
        
        @media (max-width: 576px) {
            .app-header {
                padding: 15px 0;
            }
            
            .app-header h1 {
                font-size: 1.3rem;
            }
            
            .custom-card {
                border-radius: 10px;
                padding: 12px;
            }
            
            .scan-buttons button {
                height: 45px;
                font-size: 1rem;
            }
        }
        
        /* ========================================
           动画效果
           ======================================== */
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.05);
            }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <!-- 头部 -->
    <div class="app-header">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1><i class="bi bi-box-seam"></i> 保质期管理系统</h1>
                    <div class="subtitle">
                        扫码录入 · 批次管理 · 临期提醒 
                        <span class="badge bg-white text-primary ms-2" id="versionTag">v<?php echo APP_VERSION; ?></span>
                    </div>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-info btn-sm text-white d-none" id="upgradeBtn">
                        <i class="bi bi-cloud-arrow-up"></i> 发现新版本
                    </button>
                    <button class="btn btn-warning btn-sm" id="exportBtn">
                        <i class="bi bi-file-earmark-spreadsheet"></i> 下载盘点表
                    </button>
                    <button class="btn btn-light btn-sm" id="refreshStatsBtn">
                        <i class="bi bi-arrow-clockwise"></i> 刷新统计
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <!-- 统计卡片 -->
        <div class="row mb-4">
            <div class="col-6 col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-value" id="statProducts">-</div>
                    <div class="stat-label">商品总数</div>
                </div>
            </div>
            <div class="col-6 col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-value" id="statBatches">-</div>
                    <div class="stat-label">批次总数</div>
                </div>
            </div>
            <div class="col-6 col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-value text-warning" id="statExpirySoon">-</div>
                    <div class="stat-label">即将过期</div>
                </div>
            </div>
            <div class="col-6 col-md-3 mb-3">
                <div class="stat-card">
                    <div class="stat-value text-danger" id="statExpired">-</div>
                    <div class="stat-label">已过期</div>
                </div>
            </div>
        </div>

        <!-- 扫码区域 -->
        <div class="custom-card">
            <div class="card-title">
                <i class="bi bi-qr-code-scan"></i>
                步骤 1: 扫描条形码
            </div>
            <div id="reader"></div>
            <div class="scan-buttons">
                <button type="button" class="btn btn-scan" id="startScanBtn">
                    <i class="bi bi-camera"></i> 启动摄像头
                </button>
                <button type="button" class="btn btn-outline-secondary d-none" id="stopScanBtn">
                    <i class="bi bi-stop-circle"></i> 停止扫描
                </button>
            </div>
            
            <!-- 手动输入 -->
            <div class="mt-3">
                <label class="form-label text-muted small">
                    <i class="bi bi-keyboard"></i> 或手动输入 SKU：
                </label>
                <div class="input-group">
                    <input type="text" class="form-control" id="manualSku" 
                           placeholder="输入商品SKU或条形码">
                    <button class="btn btn-outline-primary" type="button" id="manualSearchBtn">
                        <i class="bi bi-search"></i> 查询
                    </button>
                </div>
            </div>
        </div>

        <!-- 商品信息表单 -->
        <div class="custom-card">
            <div class="card-title">
                <i class="bi bi-pencil-square"></i>
                步骤 2: 商品信息与批次录入
            </div>
            
            <form id="productForm">
                <!-- SKU 输入 -->
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="sku" name="sku" 
                           placeholder="SKU/条形码" required>
                    <label for="sku">
                        <i class="bi bi-upc-scan"></i> SKU / 条形码
                    </label>
                </div>
                
                <!-- 商品名称输入 -->
                <div class="form-floating mb-3">
                    <input type="text" class="form-control" id="productName" name="productName" 
                           placeholder="商品名称" required>
                    <label for="productName">
                        <i class="bi bi-tag"></i> 商品名称
                    </label>
                </div>
                
                <!-- 批次列表 -->
                <div class="mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <label class="form-label fw-bold mb-0">
                            <i class="bi bi-layers"></i> 批次信息
                        </label>
                        <button type="button" class="btn btn-success btn-sm" id="addBatchBtn">
                            <i class="bi bi-plus-circle"></i> 添加批次
                        </button>
                    </div>
                    
                    <div id="batchesContainer">
                        <!-- 批次行动态添加到这里 -->
                    </div>
                </div>
                
                <!-- 提交按钮 -->
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="bi bi-save"></i> 保存商品信息
                    </button>
                    <button type="button" class="btn btn-outline-secondary" id="resetFormBtn">
                        <i class="bi bi-arrow-counterclockwise"></i> 重置表单
                    </button>
                </div>
            </form>
        </div>

        <!-- 使用说明 -->
        <div class="custom-card">
            <div class="card-title">
                <i class="bi bi-info-circle"></i>
                使用说明
            </div>
            <ol class="mb-0 text-muted small">
                <li class="mb-2">点击"启动摄像头"按钮，允许浏览器访问摄像头权限</li>
                <li class="mb-2">将条形码/二维码对准扫描框，系统会自动识别并填充 SKU</li>
                <li class="mb-2">如果是新商品，请手动输入商品名称</li>
                <li class="mb-2">点击"添加批次"可录入多个批次（到期日期 + 数量）</li>
                <li class="mb-2">点击"保存商品信息"完成数据录入</li>
            </ol>
        </div>
    </div>

    <!-- 提示消息容器 -->
    <div class="alert-container" id="alertContainer"></div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // ========================================
        // 全局变量
        // ========================================
        let html5QrCode = null;
        let isScanning = false;
        
        // ========================================
        // 工具函数
        // ========================================
        
        /**
         * 显示提示消息
         * @param {string} message - 消息内容
         * @param {string} type - 消息类型 (success/danger/warning/info)
         */
        function showAlert(message, type = 'info') {
            const container = document.getElementById('alertContainer');
            
            // 图标映射
            const icons = {
                success: 'bi-check-circle',
                danger: 'bi-exclamation-triangle',
                warning: 'bi-exclamation-circle',
                info: 'bi-info-circle'
            };
            
            const alertHtml = `
                <div class="alert alert-${type} alert-dismissible fade show fade-in" role="alert">
                    <i class="bi ${icons[type]}"></i> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', alertHtml);
            
            // 3秒后自动消失
            setTimeout(() => {
                const alerts = container.querySelectorAll('.alert');
                if (alerts.length > 0) {
                    alerts[0].remove();
                }
            }, 3000);
        }
        
        /**
         * 计算到期状态
         * @param {string} expiryDate - 到期日期 (YYYY-MM-DD)
         * @returns {object} - { status: 'expired'|'warning'|'normal', text: string, days: number }
         */
        function getExpiryStatus(expiryDate) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const expiry = new Date(expiryDate);
            expiry.setHours(0, 0, 0, 0);
            
            const diffTime = expiry - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays < 0) {
                return {
                    status: 'expired',
                    text: `已过期 ${Math.abs(diffDays)} 天`,
                    class: 'expired',
                    badgeClass: 'expired'
                };
            } else if (diffDays <= 30) {
                return {
                    status: 'warning',
                    text: `${diffDays} 天后到期`,
                    class: 'warning',
                    badgeClass: 'warning'
                };
            } else {
                return {
                    status: 'normal',
                    text: `${diffDays} 天后到期`,
                    class: '',
                    badgeClass: 'normal'
                };
            }
        }
        
        /**
         * 格式化日期显示
         * @param {string} dateStr - 日期字符串 (YYYY-MM-DD)
         * @returns {string} - 格式化后的日期 (YYYY年MM月DD日)
         */
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
        }
        
        // ========================================
        // 统计功能
        // ========================================
        
        /**
         * 加载统计数据
         */
        async function loadStatistics() {
            try {
                const response = await fetch('index.php?api=get_statistics');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.statistics;
                    document.getElementById('statProducts').textContent = stats.total_products;
                    document.getElementById('statBatches').textContent = stats.total_batches;
                    document.getElementById('statExpirySoon').textContent = stats.expiry_soon;
                    document.getElementById('statExpired').textContent = stats.expired;
                }
            } catch (error) {
                console.error('加载统计数据失败:', error);
            }
        }
        
        // 页面加载时获取统计数据
        document.addEventListener('DOMContentLoaded', function() {
            loadStatistics();
            
            // 刷新统计按钮
            document.getElementById('refreshStatsBtn').addEventListener('click', function() {
                loadStatistics();
                showAlert('统计数据已刷新', 'success');
            });

            // 导出盘点表按钮
            document.getElementById('exportBtn').addEventListener('click', function() {
                window.location.href = 'index.php?api=export_inventory';
                showAlert('正在生成 AI 整理的盘点表...', 'info');
            });
        });
        
        // ========================================
        // 扫码功能
        // ========================================
        
        /**
         * 启动摄像头扫描
         */
        document.getElementById('startScanBtn').addEventListener('click', async function() {
            if (isScanning) return;
            
            const startBtn = document.getElementById('startScanBtn');
            const stopBtn = document.getElementById('stopScanBtn');
            
            try {
                html5QrCode = new Html5Qrcode("reader");
                
                const config = {
                    fps: 10,
                    qrbox: { width: 250, height: 250 },
                    aspectRatio: 1.0
                };
                
                await html5QrCode.start(
                    { facingMode: "environment" },
                    config,
                    onScanSuccess,
                    onScanError
                );
                
                startBtn.classList.add('d-none');
                stopBtn.classList.remove('d-none');
                isScanning = true;
                
                showAlert('摄像头已启动，请对准条形码', 'info');
                
            } catch (err) {
                showAlert('无法启动摄像头: ' + err, 'danger');
                stopScanning();
            }
        });
        
        /**
         * 停止摄像头扫描
         */
        document.getElementById('stopScanBtn').addEventListener('click', stopScanning);
        
        function stopScanning() {
            if (html5QrCode && isScanning) {
                html5QrCode.stop().then(() => {
                    document.getElementById('startScanBtn').classList.remove('d-none');
                    document.getElementById('stopScanBtn').classList.add('d-none');
                    isScanning = false;
                }).catch(err => {
                    console.error('停止扫描失败:', err);
                });
            }
        }
        
        /**
         * 扫码成功回调
         */
        function onScanSuccess(decodedText, decodedResult) {
            // 填充 SKU
            document.getElementById('sku').value = decodedText;
            
            // 停止扫描
            stopScanning();
            
            // 自动查询商品
            searchProduct(decodedText);
            
            showAlert(`扫码成功: ${decodedText}`, 'success');
            
            // 播放提示音（可选）
            playBeep();
        }
        
        /**
         * 扫码错误回调（静默处理）
         */
        function onScanError(error) {
            // 静默处理，避免控制台刷屏
        }
        
        /**
         * 播放提示音 (叮~)
         */
        function playBeep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                // 第一个频率：短促清脆
                const osc1 = audioCtx.createOscillator();
                const gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(1200, audioCtx.currentTime);
                gain1.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                
                osc1.start();
                osc1.stop(audioCtx.currentTime + 0.1);

                // 第二个频率：略高的尾音
                setTimeout(() => {
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(1600, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                    
                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);
                    
                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.2);
                }, 50);

            } catch (e) {
                console.warn('播放音效失败:', e);
            }
        }
        
        // ========================================
        // 升级功能
        // ========================================
        
        /**
         * 检查更新
         */
        async function checkUpgrade() {
            try {
                const response = await fetch('index.php?api=check_upgrade');
                const data = await response.json();
                
                if (data.success && data.has_update) {
                    const upgradeBtn = document.getElementById('upgradeBtn');
                    upgradeBtn.classList.remove('d-none');
                    upgradeBtn.innerHTML = `<i class="bi bi-cloud-arrow-up"></i> 升级到 ${data.latest}`;
                    
                    upgradeBtn.onclick = async () => {
                        if (confirm(`确定要从 ${data.current} 升级到 ${data.latest} 吗？\n系统将自动从 GitHub 下载最新代码覆盖本地文件。`)) {
                            upgradeBtn.disabled = true;
                            upgradeBtn.innerHTML = `<i class="bi bi-hourglass-split"></i> 升级中...`;
                            
                            const execResp = await fetch('index.php?api=execute_upgrade');
                            const execData = await execResp.json();
                            
                            if (execData.success) {
                                showAlert(execData.message, 'success');
                                setTimeout(() => window.location.reload(), 1500);
                            } else {
                                showAlert('升级失败: ' + execData.message, 'danger');
                                upgradeBtn.disabled = false;
                            }
                        }
                    };
                }
            } catch (error) {
                console.log('检查更新失败，这可能是网络问题。');
            }
        }

        // ========================================
        // 商品查询功能
        // ========================================
        
        /**
         * 手动查询按钮
         */
        document.getElementById('manualSearchBtn').addEventListener('click', function() {
            const sku = document.getElementById('manualSku').value.trim();
            if (sku) {
                document.getElementById('sku').value = sku;
                searchProduct(sku);
            } else {
                showAlert('请输入 SKU', 'warning');
            }
        });
        
        /**
         * 根据 SKU 查询商品信息
         * @param {string} sku - 商品 SKU
         */
        async function searchProduct(sku) {
            sku = sku || document.getElementById('sku').value.trim();
            
            if (!sku) {
                showAlert('请输入或扫描 SKU', 'warning');
                return;
            }
            
            try {
                showAlert('正在查询...', 'info');
                
                const response = await fetch(`index.php?api=get_product&sku=${encodeURIComponent(sku)}`);
                const data = await response.json();
                
                if (data.success) {
                    if (data.exists) {
                        // 商品存在，回显信息
                        document.getElementById('productName').value = data.product.name;
                        
                        // 显示已有批次
                        displayBatches(data.batches);
                        
                        showAlert(`已加载商品: ${data.product.name}`, 'success');
                    } else {
                        // 商品不存在，准备新建
                        document.getElementById('productName').value = '';
                        clearBatches();
                        addBatchRow();
                        
                        showAlert('新商品，请输入商品名称', 'info');
                    }
                } else {
                    showAlert(data.message || '查询失败', 'danger');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'danger');
            }
        }
        
        // ========================================
        // 批次管理功能
        // ========================================
        
        /**
         * 添加批次按钮
         */
        document.getElementById('addBatchBtn').addEventListener('click', function() {
            addBatchRow();
            showAlert('已添加新批次行', 'info');
        });
        
        /**
         * 添加批次行
         * @param {object} batchData - 批次数据 { id, expiry_date, quantity, status }
         */
        function addBatchRow(batchData = null) {
            const container = document.getElementById('batchesContainer');
            const batchIndex = container.children.length + 1;
            
            // 今天的日期作为默认值
            const today = new Date().toISOString().split('T')[0];
            
            const expiryDate = batchData ? batchData.expiry_date : today;
            const quantity = batchData ? batchData.quantity : '';
            
            // 计算到期状态
            const expiryStatus = batchData ? getExpiryStatus(expiryDate) : getExpiryStatus(today);
            const statusClass = batchData ? expiryStatus.class : '';
            const statusText = batchData ? expiryStatus.text : '新批次';
            
            const batchHtml = `
                <div class="batch-item ${statusClass} fade-in" data-batch-id="${batchData ? batchData.id : ''}">
                    <div class="row g-2">
                        <div class="col-12 col-md-6">
                            <label class="form-label small">
                                <i class="bi bi-calendar-event"></i> 到期时间
                            </label>
                            <input type="date" class="form-control expiry-date-input" 
                                   value="${expiryDate}" required>
                        </div>
                        <div class="col-12 col-md-4">
                            <label class="form-label small">
                                <i class="bi bi-box"></i> 数量
                            </label>
                            <input type="number" class="form-control quantity-input" 
                                   value="${quantity}" min="0" placeholder="0" required>
                        </div>
                        <div class="col-12 col-md-2">
                            <label class="form-label small">&nbsp;</label>
                            <button type="button" class="btn btn-danger w-100 remove-batch-btn">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    ${batchData ? `
                    <div class="mt-2 small text-muted">
                        <span class="status-badge ${expiryStatus.badgeClass}">${statusText}</span>
                    </div>
                    ` : ''}
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', batchHtml);
            
            // 绑定删除按钮事件
            const newBatch = container.lastElementChild;
            const removeBtn = newBatch.querySelector('.remove-batch-btn');
            removeBtn.addEventListener('click', function() {
                if (container.children.length > 1) {
                    newBatch.remove();
                    showAlert('批次已删除', 'info');
                } else {
                    showAlert('至少保留一个批次', 'warning');
                }
            });
            
            // 绑定日期变更事件（更新状态显示）
            const dateInput = newBatch.querySelector('.expiry-date-input');
            dateInput.addEventListener('change', function() {
                updateBatchStatus(newBatch, this.value);
            });
        }
        
        /**
         * 更新批次状态显示
         * @param {HTMLElement} batchElement - 批次行元素
         * @param {string} expiryDate - 到期日期
         */
        function updateBatchStatus(batchElement, expiryDate) {
            const status = getExpiryStatus(expiryDate);
            
            // 移除旧的状态类
            batchElement.classList.remove('expired', 'warning');
            
            // 添加新的状态类
            if (status.class) {
                batchElement.classList.add(status.class);
            }
            
            // 更新或添加状态标签
            let statusDiv = batchElement.querySelector('.mt-2.small.text-muted');
            if (!statusDiv) {
                statusDiv = document.createElement('div');
                statusDiv.className = 'mt-2 small text-muted';
                batchElement.appendChild(statusDiv);
            }
            
            statusDiv.innerHTML = `<span class="status-badge ${status.badgeClass}">${status.text}</span>`;
        }
        
        /**
         * 显示批次列表
         * @param {array} batches - 批次数组
         */
        function displayBatches(batches) {
            const container = document.getElementById('batchesContainer');
            container.innerHTML = '';
            
            if (batches && batches.length > 0) {
                batches.forEach(batch => {
                    addBatchRow(batch);
                });
                showAlert(`已加载 ${batches.length} 个批次`, 'info');
            } else {
                addBatchRow();
            }
        }
        
        /**
         * 清空批次列表
         */
        function clearBatches() {
            document.getElementById('batchesContainer').innerHTML = '';
        }
        
        // ========================================
        // 表单提交功能
        // ========================================
        
        /**
         * 表单提交事件
         */
        document.getElementById('productForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const sku = document.getElementById('sku').value.trim();
            const name = document.getElementById('productName').value.trim();
            
            // 收集批次数据
            const batches = [];
            const batchItems = document.querySelectorAll('.batch-item');
            
            batchItems.forEach(item => {
                const expiryDate = item.querySelector('.expiry-date-input').value;
                const quantity = parseInt(item.querySelector('.quantity-input').value) || 0;
                
                if (expiryDate && quantity >= 0) {
                    batches.push({
                        expiry_date: expiryDate,
                        quantity: quantity
                    });
                }
            });
            
            if (batches.length === 0) {
                showAlert('请至少添加一个有效批次', 'warning');
                return;
            }
            
            // 禁用提交按钮
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 保存中...';
            
            try {
                const response = await fetch('index.php?api=save_product', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        sku: sku,
                        name: name,
                        batches: batches
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showAlert(`保存成功！新增 ${data.batches_added} 个批次`, 'success');
                    
                    // 刷新统计数据
                    loadStatistics();
                    
                    // 重新查询商品（显示更新后的批次）
                    searchProduct(sku);
                } else {
                    showAlert(data.message || '保存失败', 'danger');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'danger');
            } finally {
                // 恢复提交按钮
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
        
        // ========================================
        // 重置表单功能
        // ========================================
        
        /**
         * 重置表单按钮
         */
        document.getElementById('resetFormBtn').addEventListener('click', function() {
            document.getElementById('productForm').reset();
            clearBatches();
            addBatchRow();
            showAlert('表单已重置', 'info');
        });
        
        // ========================================
        // 页面初始化
        // ========================================
        
        document.addEventListener('DOMContentLoaded', function() {
            // 检查版本更新
            checkUpgrade();

            // 默认添加一个批次行
            addBatchRow();
            
            // SKU 输入框回车查询
            document.getElementById('sku').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchProduct();
                }
            });
            
            // 手动 SKU 输入框回车查询
            document.getElementById('manualSku').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    document.getElementById('manualSearchBtn').click();
                }
            });
            
            // 欢迎提示
            setTimeout(() => {
                showAlert('欢迎使用保质期管理系统！点击"启动摄像头"开始扫码录入。', 'info');
            }, 500);
        });
    </script>
</body>
</html>
