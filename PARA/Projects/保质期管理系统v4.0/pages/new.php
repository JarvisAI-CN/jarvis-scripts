<?php
/**
 * 保质期管理系统 - v4.0.0 新增盘点页面
 * 二维码扫描和商品录入
 */

define('APP_NAME', '保质期管理系统');
define('DEBUG_MODE', true);
session_start();

require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/check_auth.php';

// 检查是否已登录
if (!checkAuth()) {
    header('Location: /');
    exit;
}

// 设置页面信息
$pageTitle = '新增盘点 - 保质期管理系统';
$pageName = 'new';
?>

<?php require_once __DIR__ . '/../includes/header.php'; ?>

<div class="container">
    <div class="row g-4">
        <!-- 页面导航 -->
        <div class="col-12">
            <div class="d-flex align-items-center justify-content-between mb-4">
                <div>
                    <h1 class="h5 fw-bold mb-0">新增盘点</h1>
                    <p class="text-muted small">扫描商品二维码，快速录入保质期信息</p>
                </div>
                <button type="button" class="btn btn-outline-primary" onclick="location.reload()">
                    <i class="bi bi-arrow-clockwise"></i>
                    刷新页面
                </button>
            </div>
        </div>
        
        <!-- 扫描区域 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-qr-code-scan text-success"></i>
                            二维码扫描
                        </h5>
                        <span class="badge bg-success-subtle text-success">支持多种格式</span>
                    </div>
                    
                    <!-- 扫描区域 -->
                    <div id="scanArea" class="text-center py-4">
                        <div id="reader" style="width: 100%; height: 300px; background: #f5f5f5; border: 2px dashed #dee2e6; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                            <div class="text-center">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">加载中...</span>
                                </div>
                                <p class="mt-2 text-muted">初始化扫描器...</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- 扫描控制按钮 -->
                    <div class="d-grid gap-2 mt-3">
                        <button id="startScanBtn" class="btn btn-primary btn-lg">
                            <i class="bi bi-play"></i>
                            开始扫描
                        </button>
                        
                        <button id="stopScanBtn" class="btn btn-outline-danger btn-lg d-none">
                            <i class="bi bi-stop"></i>
                            停止扫描
                        </button>
                        
                        <button id="resetScanBtn" class="btn btn-outline-secondary btn-sm">
                            <i class="bi bi-arrow-clockwise"></i>
                            重置扫描器
                        </button>
                    </div>
                    
                    <!-- 扫描结果 -->
                    <div id="scanResults" class="mt-3"></div>
                </div>
            </div>
        </div>
        
        <!-- 商品信息卡片 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-box text-info"></i>
                            商品信息
                        </h5>
                        <span class="badge bg-info-subtle text-info" id="productCount">0 个商品</span>
                    </div>
                    
                    <!-- 手动输入区域 -->
                    <div class="mb-3">
                        <label class="form-label">📝 手动输入 SKU</label>
                        <div class="input-group">
                            <input type="text" id="manualSKU" class="form-control" placeholder="输入商品 SKU">
                            <button class="btn btn-outline-primary" id="addManualBtn">
                                <i class="bi bi-plus-circle"></i>
                                添加
                            </button>
                        </div>
                    </div>
                    
                    <!-- 待处理商品列表 -->
                    <div id="pendingList" class="d-grid gap-2 mb-3">
                        <div class="text-center py-3 text-muted">
                            <i class="bi bi-box"></i>
                            <p class="mb-0">暂无扫描商品</p>
                            <p class="small">开始扫描或手动添加商品</p>
                        </div>
                    </div>
                    
                    <!-- 提交按钮 -->
                    <div class="d-grid gap-2">
                        <button id="saveDraftBtn" class="btn btn-outline-success">
                            <i class="bi bi-save"></i>
                            保存草稿
                        </button>
                        
                        <button id="submitInventoryBtn" class="btn btn-primary btn-lg">
                            <i class="bi bi-upload"></i>
                            提交盘点
                        </button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 商品详细信息 -->
        <div class="col-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-table text-warning"></i>
                            商品详细信息
                        </h5>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-secondary btn-sm" id="clearAllBtn">
                                <i class="bi bi-trash"></i>
                                清空所有
                            </button>
                            <span class="badge bg-warning-subtle text-warning" id="totalCount">0 个商品</span>
                        </div>
                    </div>
                    
                    <!-- 商品表格 -->
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th width="50">#</th>
                                    <th>SKU</th>
                                    <th>商品名称</th>
                                    <th>分类</th>
                                    <th>批次</th>
                                    <th>数量</th>
                                    <th>过期日期</th>
                                    <th>状态</th>
                                    <th width="100">操作</th>
                                </tr>
                            </thead>
                            <tbody id="productTableBody">
                                <tr>
                                    <td colspan="9" class="text-center text-muted py-3">
                                        <i class="bi bi-table"></i>
                                        <p class="mb-0">暂无商品数据</p>
                                        <p class="small">扫描二维码或手动添加商品</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
    
    // 添加事件监听器
    setupEventListeners();
});

function initializePage() {
    // 初始化扫描器
    initializeScanner();
    
    // 检查是否有草稿数据
    loadDraft();
    
    // 设置页面标题
    document.title = '新增盘点 - 保质期管理系统';
}

function setupEventListeners() {
    // 扫描控制按钮
    document.getElementById('startScanBtn').addEventListener('click', startScanning);
    document.getElementById('stopScanBtn').addEventListener('click', stopScanning);
    document.getElementById('resetScanBtn').addEventListener('click', resetScanner);
    
    // 手动输入区域
    document.getElementById('addManualBtn').addEventListener('click', addManualProduct);
    document.getElementById('manualSKU').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addManualProduct();
        }
    });
    
    // 操作按钮
    document.getElementById('saveDraftBtn').addEventListener('click', saveDraft);
    document.getElementById('submitInventoryBtn').addEventListener('click', submitInventory);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllProducts);
}

function initializeScanner() {
    const reader = document.getElementById('reader');
    
    if (!reader) {
        console.error('扫描器容器未找到');
        return;
    }
    
    // 初始化扫描器（简单实现）
    reader.innerHTML = `
        <div class="text-center py-4">
            <i class="bi bi-qr-code-scan h1 text-primary mb-2"></i>
            <p class="mb-0">点击开始扫描</p>
            <p class="text-muted small">支持多种二维码格式</p>
        </div>
    `;
    
    // 模拟扫描功能
    window.mockScanner = null;
}

function startScanning() {
    // 模拟扫描器启动
    const reader = document.getElementById('reader');
    
    reader.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">扫描中...</span>
            </div>
            <p class="mt-2">扫描器正在运行</p>
            <p class="text-muted small">请将二维码对准扫描区域</p>
        </div>
    `;
    
    // 切换按钮状态
    document.getElementById('startScanBtn').classList.add('d-none');
    document.getElementById('stopScanBtn').classList.remove('d-none');
    
    // 模拟扫描过程
    window.mockScanner = setInterval(() => {
        if (Math.random() > 0.9) {
            const mockSKU = 'SKU' + Math.floor(Math.random() * 10000);
            const mockName = '商品' + Math.floor(Math.random() * 100);
            handleScanResult(mockSKU, mockName);
        }
    }, 3000);
}

function stopScanning() {
    // 停止模拟扫描器
    if (window.mockScanner) {
        clearInterval(window.mockScanner);
        window.mockScanner = null;
    }
    
    // 恢复扫描器界面
    const reader = document.getElementById('reader');
    reader.innerHTML = `
        <div class="text-center py-4">
            <i class="bi bi-qr-code-scan h1 text-primary mb-2"></i>
            <p class="mb-0">扫描器已停止</p>
            <p class="text-muted small">点击开始扫描继续</p>
        </div>
    `;
    
    // 切换按钮状态
    document.getElementById('startScanBtn').classList.remove('d-none');
    document.getElementById('stopScanBtn').classList.add('d-none');
}

function resetScanner() {
    // 重置扫描器
    stopScanning();
    document.getElementById('scanResults').innerHTML = '';
    document.getElementById('pendingList').innerHTML = `
        <div class="text-center py-3 text-muted">
            <i class="bi bi-box"></i>
            <p class="mb-0">暂无扫描商品</p>
            <p class="small">开始扫描或手动添加商品</p>
        </div>
    `;
}

function handleScanResult(qrCode) {
    console.log('扫码结果:', qrCode);
    
    // 解析二维码数据
    let sku = '';
    let expiryDateFromQR = null;

    // 格式1: 星巴克URL格式
    if (qrCode.includes('artwork.starbucks.com.cn')) {
        try {
            const url = new URL(qrCode);
            const pathParts = url.pathname.split('/');
            const ciiIndex = pathParts.indexOf('cii1');

            if (ciiIndex !== -1 && ciiIndex + 1 < pathParts.length) {
                let ciiData = pathParts[ciiIndex + 1];

                const ampParts = ciiData.split('&');
                ciiData = ampParts[0];

                const lastPart = ampParts[ampParts.length - 1];
                if (lastPart.length === 8 && /^\d+$/.test(lastPart)) {
                    const year = lastPart.substring(0, 4);
                    const month = lastPart.substring(4, 6);
                    const day = lastPart.substring(6, 8);
                    expiryDateFromQR = `${year}-${month}-${day}`;
                }

                if (ciiData.startsWith('00')) {
                    ciiData = ciiData.substring(2);
                }

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
    else if (qrCode.includes('#')) {
        const parts = qrCode.split('#');
        if (parts.length >= 3) {
            let part1 = parts[0];

            if (part1.startsWith('00')) {
                part1 = part1.substring(2);
            }

            if (part1.length >= 8) {
                sku = part1.substring(0, 8);
            }

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
    // 格式3: 纯SKU格式
    else {
        sku = qrCode.trim();
        console.log('纯SKU格式:', { sku });
    }
    
    // 查询商品信息
    fetch(`/api/get_product.php?sku=${encodeURIComponent(sku)}`)
        .then(response => response.json())
        .then(data => {
            if (data.exists) {
                // 商品存在，继续处理
                const productName = data.product.name;
                
                const pendingList = document.getElementById('pendingList');
                const existingItem = Array.from(pendingList.children).find(child => 
                    child.dataset.sku === sku
                );
                
                if (existingItem) {
                    // 如果商品已存在，增加数量
                    const quantityElement = existingItem.querySelector('.product-quantity');
                    const current = parseInt(quantityElement.textContent);
                    quantityElement.textContent = current + 1;
                    
                    showAlert('商品数量已更新', 'info');
                } else {
                    // 添加新商品
                    const newItem = createProductItem(sku, productName);
                    pendingList.appendChild(newItem);
                    
                    showAlert(`商品已添加: ${productName}`, 'success');
                }
                
                updateProductCount();
            } else {
                // 商品不存在，提示用户
                showAlert(`未找到商品: ${sku}`, 'warning');
            }
        })
        .catch(error => {
            console.error('查询商品信息失败:', error);
            showAlert('查询商品信息失败', 'error');
        });
}

function createProductItem(sku, productName) {
    const item = document.createElement('div');
    item.className = 'card border-0 shadow-sm bg-light rounded-3';
    item.dataset.sku = sku;
    
    item.innerHTML = `
        <div class="card-body p-2">
            <div class="d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center gap-2">
                    <i class="bi bi-box text-primary"></i>
                    <div>
                        <div class="fw-bold">${productName}</div>
                        <div class="text-muted small">${sku}</div>
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <span class="product-quantity badge bg-primary-subtle text-primary">1</span>
                    <button class="btn btn-outline-danger btn-sm" onclick="removeProduct('${sku}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return item;
}

function addManualProduct() {
    const skuInput = document.getElementById('manualSKU');
    const sku = skuInput.value.trim();
    
    if (!sku) {
        showAlert('请输入商品 SKU', 'warning');
        return;
    }
    
    // 模拟查询商品信息
    const productName = `手动录入商品 (${sku})`;
    
    handleScanResult(sku, productName);
    
    // 清空输入框
    skuInput.value = '';
    skuInput.focus();
}

function removeProduct(sku) {
    const pendingList = document.getElementById('pendingList');
    const item = Array.from(pendingList.children).find(child => 
        child.dataset.sku === sku
    );
    
    if (item) {
        item.classList.add('fade-out');
        setTimeout(() => {
            item.remove();
            updateProductCount();
            showAlert('商品已删除', 'info');
        }, 300);
    }
}

function updateProductCount() {
    const pendingList = document.getElementById('pendingList');
    const productCount = Array.from(pendingList.children).filter(child => 
        child.tagName === 'DIV' && child.classList.contains('card')
    ).length;
    
    document.getElementById('productCount').textContent = `${productCount} 个商品`;
    document.getElementById('totalCount').textContent = `${productCount} 个商品`;
}

function clearAllProducts() {
    if (confirm('确定要清空所有商品吗？')) {
        const pendingList = document.getElementById('pendingList');
        pendingList.innerHTML = `
            <div class="text-center py-3 text-muted">
                <i class="bi bi-box"></i>
                <p class="mb-0">暂无扫描商品</p>
                <p class="small">开始扫描或手动添加商品</p>
            </div>
        `;
        
        updateProductCount();
        showAlert('所有商品已清空', 'info');
    }
}

function saveDraft() {
    // 保存到本地存储
    const pendingList = document.getElementById('pendingList');
    const products = Array.from(pendingList.children)
        .filter(child => child.tagName === 'DIV' && child.classList.contains('card'))
        .map(child => ({
            sku: child.dataset.sku,
            productName: child.querySelector('.fw-bold').textContent,
            quantity: parseInt(child.querySelector('.product-quantity').textContent)
        }));
    
    localStorage.setItem('draftProducts', JSON.stringify(products));
    localStorage.setItem('draftTime', new Date().toISOString());
    
    showAlert('草稿已保存', 'success');
}

function loadDraft() {
    const draft = localStorage.getItem('draftProducts');
    const draftTime = localStorage.getItem('draftTime');
    
    if (draft) {
        const products = JSON.parse(draft);
        
        // 检查草稿是否过期（超过24小时）
        if (draftTime && new Date(draftTime).getTime() > Date.now() - 24 * 60 * 60 * 1000) {
            products.forEach(product => {
                handleScanResult(product.sku, product.productName);
            });
            
            showAlert(`已加载草稿数据 (${products.length}个商品)`, 'info');
        } else {
            localStorage.removeItem('draftProducts');
            localStorage.removeItem('draftTime');
        }
    }
}

async function submitInventory() {
    const pendingList = document.getElementById('pendingList');
    const products = Array.from(pendingList.children)
        .filter(child => child.tagName === 'DIV' && child.classList.contains('card'))
        .map(child => ({
            sku: child.dataset.sku,
            productName: child.querySelector('.fw-bold').textContent,
            quantity: parseInt(child.querySelector('.product-quantity').textContent)
        }));
    
    if (products.length === 0) {
        showAlert('请添加商品后再提交', 'warning');
        return;
    }
    
    if (!confirm(`确定要提交 ${products.length} 个商品吗？`)) {
        return;
    }
    
    try {
        // 发送数据到服务器
        const response = await fetch('/api/submit-inventory.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                products: products,
                notes: '手动盘点'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 提交成功，清空数据
            clearAllProducts();
            localStorage.removeItem('draftProducts');
            localStorage.removeItem('draftTime');
            
            showAlert('盘点已成功提交', 'success');
            
            // 延迟跳转到历史页面
            setTimeout(() => {
                window.location.href = '/past.php';
            }, 2000);
        } else {
            showAlert(`提交失败: ${data.message}`, 'danger');
        }
    } catch (error) {
        showAlert(`网络错误: ${error.message}`, 'danger');
    }
}

// 辅助函数
function showAlert(message, type) {
    // 创建通知
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    
    alertContainer.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span class="ms-2">${message}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // 显示通知
    const alertArea = document.getElementById('alert-container');
    alertArea.appendChild(alertContainer);
    
    // 3秒后自动关闭
    setTimeout(() => {
        alertContainer.classList.add('fade');
        setTimeout(() => {
            alertContainer.remove();
        }, 300);
    }, 3000);
}

// 性能优化
window.addEventListener('resize', function() {
    // 响应式调整
    const reader = document.getElementById('reader');
    if (reader) {
        reader.style.width = '100%';
        reader.style.height = Math.min(window.innerHeight - 300, 400) + 'px';
    }
});

// 页面可见性 API（当页面不可见时暂停扫描）
document.addEventListener('visibilitychange', function() {
    if (document.hidden && document.getElementById('stopScanBtn').classList.contains('d-none') === false) {
        stopScanning();
        showAlert('页面不可见，扫描已暂停', 'info');
    }
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
