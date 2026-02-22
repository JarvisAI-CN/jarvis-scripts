<?php
/**
 * ========================================
 * 保质期管理系统 - 盘点页面
 * 版本: v3.0.0
 * 创建日期: 2026-02-22
 * ========================================
 */

define('APP_LOADED', true);
session_start();
require_once 'includes/db.php';
require_once 'includes/check_login.php';

// 获取所有分类
$conn = getDBConnection();
$categories = $conn->query("SELECT * FROM categories ORDER BY name");

$page_title = '新增盘点';
include 'includes/header.php';
?>

<!-- 返回首页按钮 -->
<div class="mb-3">
    <a href="index.php" class="btn btn-link text-decoration-none">
        <i class="bi bi-chevron-left"></i> 返回首页
    </a>
</div>

<!-- 扫码区域 -->
<div class="scan-trigger-area mb-3 shadow-sm"
     id="startScanBtn"
     style="padding: 40px 20px;
            background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
            border-radius: 20px;
            text-align: center;
            color: #007AFF;
            cursor: pointer;">
    <i class="bi bi-qr-code-scan d-block h1"></i>
    <span class="fw-bold fs-5">点击添加 (扫一扫)</span>
</div>

<!-- 手动输入区 -->
<div class="custom-card mb-3">
    <div class="fw-bold mb-2">📝 手动输入 / 粘贴二维码</div>

    <!-- 快速粘贴区 -->
    <div class="mb-3">
        <label class="form-label small">微信扫码后粘贴URL：</label>
        <input id="qrPasteInput"
               class="form-control"
               placeholder="支持星巴克URL、纯数字码、SKU">
        <button id="qrPasteBtn" class="btn btn-success btn-sm w-100 mt-2">
            ✅ 解析粘贴的内容
        </button>
    </div>

    <hr class="my-3">

    <!-- 搜索区 -->
    <div class="mb-2">
        <label class="form-label small">或搜索商品：</label>
        <div class="input-group">
            <input id="manualSearchInput" class="form-control" placeholder="输入SKU片段或品名关键词…">
            <button id="manualSearchBtn" class="btn btn-outline-primary" type="button">🔍 搜索</button>
        </div>
    </div>
    <div id="manualSearchResults" class="mt-2"></div>
</div>

<!-- 待提交列表 -->
<div id="pendingListContainer" class="custom-card" style="display: none;">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0">📦 待提交商品 (<span id="pendingCount">0</span>)</h5>
        <button class="btn btn-sm btn-outline-danger" id="clearAllBtn">
            <i class="bi bi-trash me-1"></i>清空
        </button>
    </div>
    <div id="pendingList"></div>
</div>

<!-- 草稿操作 -->
<div class="row g-2 mb-3">
    <div class="col-6">
        <button id="saveDraftBtn" class="btn btn-outline-success w-100">
            💾 保存草稿
        </button>
    </div>
    <div class="col-6">
        <button id="loadDraftBtn" class="btn btn-outline-info w-100">
            📂 加载草稿
        </button>
    </div>
</div>

<!-- 提交按钮 -->
<div class="d-grid">
    <button class="btn btn-primary btn-lg shadow fw-bold"
            id="submitSessionBtn"
            disabled
            style="border-radius: 16px;">
        提交盘点单
    </button>
</div>

<!-- 扫码覆盖层 -->
<div id="scanOverlay">
    <div class="p-3 d-flex justify-content-between text-white">
        <button class="btn btn-dark rounded-pill" id="stopScanBtn">
            <i class="bi bi-x-lg"></i>
        </button>
        <div class="fw-bold">扫一扫</div>
        <button class="btn btn-dark rounded-pill" id="torchBtn">
            <i class="bi bi-lightbulb"></i>
        </button>
    </div>
    <div id="reader"></div>
</div>

<!-- 录入详情模态框 -->
<div class="modal fade" id="entryModal" data-bs-backdrop="static">
    <div class="modal-dialog">
        <div class="modal-content" style="border-radius: 16px; border: none;">
            <div class="modal-header border-bottom-0">
                <h5 class="fw-bold">录入商品信息</h5>
                <button class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body bg-light">
                <form id="productForm">
                    <div class="custom-card mb-2">
                        <label class="form-label small fw-bold">SKU（条码）</label>
                        <input type="text" class="form-control mb-2" id="sku" readonly>

                        <label class="form-label small fw-bold">分类</label>
                        <select class="form-select mb-2" id="categoryId">
                            <option value="0">选择分类</option>
                            <?php while ($cat = $categories->fetch_assoc()): ?>
                                <option value="<?= $cat['id'] ?>"><?= htmlspecialchars($cat['name']) ?></option>
                            <?php endwhile; ?>
                        </select>

                        <label class="form-label small fw-bold">商品名称</label>
                        <input type="text" class="form-control mb-2" id="productName" placeholder="输入商品名称">

                        <label class="form-label small fw-bold">缓冲天数（可选）</label>
                        <input type="number" class="form-control" id="removalBuffer" placeholder="默认0天">
                    </div>

                    <div class="mb-2">
                        <label class="form-label small fw-bold">批次信息</label>
                        <div id="batchesContainer"></div>
                        <button type="button" class="btn btn-outline-success btn-sm w-100" id="addBatchBtn">
                            <i class="bi bi-plus-circle me-1"></i>添加批次
                        </button>
                    </div>
                </form>
            </div>
            <div class="modal-footer border-top-0 d-grid">
                <button class="btn btn-primary" id="confirmEntryBtn">
                    <i class="bi bi-check-lg me-1"></i>确定添加
                </button>
            </div>
        </div>
    </div>
</div>

<script>
// 全局变量
let html5QrCode = null;
let currentSessionId = 'S' + Date.now();
let pendingData = [];
const STORAGE_KEY = 'inventory_draft_' + '<?= $_SESSION['user_id'] ?>';

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 自动加载草稿
    loadDraft();

    // 绑定事件
    setupEventListeners();
});

// 设置事件监听
function setupEventListeners() {
    // 扫码按钮
    document.getElementById('startScanBtn').addEventListener('click', startScan);
    document.getElementById('stopScanBtn').addEventListener('click', stopScan);
    document.getElementById('torchBtn').addEventListener('click', toggleTorch);

    // 粘贴解析
    document.getElementById('qrPasteBtn').addEventListener('click', parsePastedContent);

    // 搜索
    document.getElementById('manualSearchBtn').addEventListener('click', manualSearch);
    document.getElementById('manualSearchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') manualSearch();
    });

    // 批次管理
    document.getElementById('addBatchBtn').addEventListener('click', addBatchField);
    document.getElementById('confirmEntryBtn').addEventListener('click', confirmEntry);

    // 草稿操作
    document.getElementById('saveDraftBtn').addEventListener('click', saveDraft);
    document.getElementById('loadDraftBtn').addEventListener('click', loadDraft);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllPending);

    // 提交
    document.getElementById('submitSessionBtn').addEventListener('click', submitSession);
}

// ===== 扫码功能 =====
function startScan() {
    document.getElementById('scanOverlay').style.display = 'flex';

    html5QrCode = new Html5Qrcode("reader");
    const config = { fps: 10, qrbox: { width: 250, height: 250 } };

    html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanFailure
    ).catch(err => {
        alert('无法启动摄像头：' + err);
        stopScan();
    });
}

function stopScan() {
    if (html5QrCode) {
        html5QrCode.stop().then(() => {
            document.getElementById('scanOverlay').style.display = 'none';
        }).catch(err => console.error('停止扫码失败:', err));
    }
}

let torchEnabled = false;
function toggleTorch() {
    if (html5QrCode) {
        html5QrCode.applyVideoConstraints({
            advanced: [{ torch: !torchEnabled }]
        }).then(() => {
            torchEnabled = !torchEnabled;
            const btn = document.getElementById('torchBtn');
            btn.classList.toggle('btn-warning', torchEnabled);
            btn.classList.toggle('btn-dark', !torchEnabled);
        }).catch(err => {
            alert('手电筒功能不支持');
        });
    }
}

function onScanSuccess(decodedText, decodedResult) {
    stopScan();
    handleScannedData(decodedText);
}

function onScanFailure(error) {
    // 扫码失败是正常的，忽略
}

// ===== 数据处理 =====
function handleScannedData(data) {
    // 显示录入对话框
    showEntryModal(data);
}

function parsePastedContent() {
    const input = document.getElementById('qrPasteInput').value.trim();
    if (!input) {
        alert('请先粘贴内容');
        return;
    }

    handleScannedData(input);
    document.getElementById('qrPasteInput').value = '';
}

function manualSearch() {
    const keyword = document.getElementById('manualSearchInput').value.trim();
    if (!keyword) {
        alert('请输入搜索关键词');
        return;
    }

    fetch(`api.php?api=search_products&keyword=${encodeURIComponent(keyword)}`)
        .then(res => res.json())
        .then(data => {
            if (data.success && data.results.length > 0) {
                displaySearchResults(data.results);
            } else {
                alert('未找到匹配的商品');
            }
        })
        .catch(err => {
            console.error('搜索失败:', err);
            alert('搜索失败，请重试');
        });
}

function displaySearchResults(products) {
    const container = document.getElementById('manualSearchResults');
    let html = '<div class="list-group">';
    products.forEach(p => {
        html += `
            <a href="#" class="list-group-item list-group-item-action" onclick="selectProduct(${p.id}); return false;">
                <div class="fw-bold">${p.sku}</div>
                <div class="small text-muted">${p.name}</div>
            </a>
        `;
    });
    html += '</div>';
    container.innerHTML = html;
}

function selectProduct(productId) {
    // 从数据库加载商品信息
    fetch(`api.php?api=get_product&id=${productId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showEntryModal(JSON.stringify({sku: data.product.sku, name: data.product.name}));
            }
        });
}

// ===== 录入对话框 =====
function showEntryModal(scannedData) {
    let sku = '', name = '';

    // 尝试解析数据
    if (scannedData.includes('artwork.starbucks.com.cn')) {
        // 星巴克URL
        const match = scannedData.match(/\/(\d+)\//);
        if (match) sku = match[1];
    } else if (scannedData.includes('#')) {
        // 纯数字码
        const parts = scannedData.split('#');
        sku = parts[0];
    } else if (/^\d+$/.test(scannedData)) {
        // 纯SKU
        sku = scannedData;
    }

    document.getElementById('sku').value = sku;
    document.getElementById('productName').value = name;
    document.getElementById('batchesContainer').innerHTML = '';
    addBatchField(); // 默认添加一个批次

    const modal = new bootstrap.Modal(document.getElementById('entryModal'));
    modal.show();
}

function addBatchField() {
    const container = document.getElementById('batchesContainer');
    const index = container.children.length;

    const html = `
        <div class="input-group mb-2 batch-field">
            <input type="date" class="form-control" name="expiry_date_${index}" required>
            <input type="number" class="form-control" name="quantity_${index}" placeholder="数量" value="1" min="1" required>
            <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.remove()">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', html);
}

function confirmEntry() {
    const sku = document.getElementById('sku').value.trim();
    const name = document.getElementById('productName').value.trim();
    const categoryId = document.getElementById('categoryId').value;
    const removalBuffer = document.getElementById('removalBuffer').value || 0;

    if (!sku) {
        alert('请输入SKU');
        return;
    }

    // 收集批次信息
    const batches = [];
    document.querySelectorAll('.batch-field').forEach(field => {
        const date = field.querySelector('input[type="date"]').value;
        const qty = field.querySelector('input[type="number"]').value;
        if (date && qty) {
            batches.push({ expiry_date: date, quantity: parseInt(qty) });
        }
    });

    if (batches.length === 0) {
        alert('请至少添加一个批次');
        return;
    }

    // 添加到待提交列表
    pendingData.push({
        sku: sku,
        name: name || '未命名',
        category_id: categoryId,
        removal_buffer: removalBuffer,
        batches: batches
    });

    // 更新UI
    updatePendingList();

    // 关闭模态框
    bootstrap.Modal.getInstance(document.getElementById('entryModal')).hide();

    // 清空表单
    document.getElementById('productForm').reset();
    document.getElementById('batchesContainer').innerHTML = '';
}

// ===== 待提交列表 =====
function updatePendingList() {
    const container = document.getElementById('pendingList');
    const countEl = document.getElementById('pendingCount');
    const mainContainer = document.getElementById('pendingListContainer');

    countEl.textContent = pendingData.length;

    if (pendingData.length === 0) {
        mainContainer.style.display = 'none';
        document.getElementById('submitSessionBtn').disabled = true;
        return;
    }

    mainContainer.style.display = 'block';
    document.getElementById('submitSessionBtn').disabled = false;

    let html = '';
    pendingData.forEach((item, index) => {
        const totalQty = item.batches.reduce((sum, b) => sum + b.quantity, 0);
        html += `
            <div class="pending-item">
                <div class="d-flex justify-content-between">
                    <div class="fw-bold">${item.sku} - ${item.name}</div>
                    <button class="btn btn-sm btn-link text-danger p-0" onclick="removePending(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
                <small class="text-muted">
                    ${item.batches.length} 个批次，共 ${totalQty} 个
                </small>
            </div>
        `;
    });
    container.innerHTML = html;
}

function removePending(index) {
    pendingData.splice(index, 1);
    updatePendingList();
}

function clearAllPending() {
    if (confirm('确定要清空所有待提交商品吗？')) {
        pendingData = [];
        updatePendingList();
    }
}

// ===== 草稿功能 =====
function saveDraft() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(pendingData));
        alert('✅ 草稿已保存（' + pendingData.length + ' 条记录）');
    } catch (e) {
        console.error('保存草稿失败:', e);
        alert('保存失败');
    }
}

function loadDraft() {
    try {
        const data = localStorage.getItem(STORAGE_KEY);
        if (data) {
            pendingData = JSON.parse(data);
            updatePendingList();
            if (pendingData.length > 0) {
                alert('✅ 已加载草稿（' + pendingData.length + ' 条记录）');
            }
        }
    } catch (e) {
        console.error('加载草稿失败:', e);
    }
}

// ===== 提交 =====
function submitSession() {
    if (pendingData.length === 0) {
        alert('没有要提交的数据');
        return;
    }

    if (!confirm('确定要提交盘点单吗？提交后无法修改。')) {
        return;
    }

    const btn = document.getElementById('submitSessionBtn');
    btn.disabled = true;
    btn.textContent = '提交中...';

    fetch('api.php?api=submit_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: pendingData })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('✅ 提交成功！');
            pendingData = [];
            localStorage.removeItem(STORAGE_KEY);
            updatePendingList();
            window.location.href = 'history.php?view=' + data.session_id;
        } else {
            alert('提交失败：' + (data.message || '未知错误'));
            btn.disabled = false;
            btn.textContent = '提交盘点单';
        }
    })
    .catch(err => {
        console.error('提交失败:', err);
        alert('提交失败，请重试');
        btn.disabled = false;
        btn.textContent = '提交盘点单';
    });
}
</script>

<?php include 'includes/footer.php'; ?>
