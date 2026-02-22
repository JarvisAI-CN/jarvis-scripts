<?php
/**
 * 保质期管理系统 - v4.0.0 历史盘点页面
 * 盘点记录查看和管理
 */

define('APP_NAME', '保质期管理系统');
define('DEBUG_MODE', true);
session_start();

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 检查是否已登录
if (!checkAuth()) {
    header('Location: /');
    exit;
}

// 设置页面信息
$pageTitle = '历史盘点 - 保质期管理系统';
$pageName = 'past';
?>

<?php require_once __DIR__ . '/../includes/header.php'; ?>

<div class="container">
    <div class="row g-4">
        <!-- 页面导航 -->
        <div class="col-12">
            <div class="d-flex align-items-center justify-content-between mb-4">
                <div>
                    <h1 class="h5 fw-bold mb-0">历史盘点</h1>
                    <p class="text-muted small">查看和管理所有盘点记录</p>
                </div>
                <div class="d-flex gap-2">
                    <a href="/new.php" class="btn btn-primary">
                        <i class="bi bi-plus-circle"></i>
                        新增盘点
                    </a>
                    <button type="button" class="btn btn-outline-primary" id="refreshBtn">
                        <i class="bi bi-arrow-clockwise"></i>
                        刷新
                    </button>
                </div>
            </div>
        </div>
        
        <!-- 筛选区域 -->
        <div class="col-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="row g-3">
                        <div class="col-md-3">
                            <label class="form-label">日期范围</label>
                            <input type="date" id="startDate" class="form-control">
                        </div>
                        
                        <div class="col-md-3">
                            <label class="form-label">至</label>
                            <input type="date" id="endDate" class="form-control">
                        </div>
                        
                        <div class="col-md-3">
                            <label class="form-label">状态</label>
                            <select id="statusFilter" class="form-select">
                                <option value="">全部</option>
                                <option value="draft">草稿</option>
                                <option value="submitted">已提交</option>
                                <option value="completed">已完成</option>
                            </select>
                        </div>
                        
                        <div class="col-md-3">
                            <label class="form-label">操作</label>
                            <div class="d-flex gap-2">
                                <button id="searchBtn" class="btn btn-primary flex-grow-1">
                                    <i class="bi bi-search"></i>
                                    搜索
                                </button>
                                <button id="resetBtn" class="btn btn-outline-secondary">
                                    <i class="bi bi-arrow-counterclockwise"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 统计概览 -->
        <div class="col-12">
            <div class="row g-3">
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <div>
                                    <p class="text-muted small mb-1">总盘点数</p>
                                    <h4 class="mb-0 fw-bold text-primary" id="totalCount">0</h4>
                                </div>
                                <div class="d-inline-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #e7f1ff; border-radius: 50%;">
                                    <i class="bi bi-files text-primary h4 mb-0"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <div>
                                    <p class="text-muted small mb-1">商品总数</p>
                                    <h4 class="mb-0 fw-bold text-success" id="totalProducts">0</h4>
                                </div>
                                <div class="d-inline-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #d1e7dd; border-radius: 50%;">
                                    <i class="bi bi-box text-success h4 mb-0"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <div>
                                    <p class="text-muted small mb-1">已过期</p>
                                    <h4 class="mb-0 fw-bold text-danger" id="expiredCount">0</h4>
                                </div>
                                <div class="d-inline-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #f8d7da; border-radius: 50%;">
                                    <i class="bi bi-exclamation-triangle text-danger h4 mb-0"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-3">
                    <div class="card border-0 shadow-sm rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <div>
                                    <p class="text-muted small mb-1">本周盘点</p>
                                    <h4 class="mb-0 fw-bold text-info" id="weeklyCount">0</h4>
                                </div>
                                <div class="d-inline-flex align-items-center justify-content-center" style="width: 50px; height: 50px; background: #cff4fc; border-radius: 50%;">
                                    <i class="bi bi-calendar-week text-info h4 mb-0"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 盘点列表 -->
        <div class="col-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-table text-primary"></i>
                            盘点列表
                        </h5>
                        <div class="d-flex gap-2">
                            <button class="btn btn-outline-success btn-sm" id="exportBtn">
                                <i class="bi bi-download"></i>
                                导出
                            </button>
                            <span class="badge bg-primary-subtle text-primary" id="listCount">0 条记录</span>
                        </div>
                    </div>
                    
                    <!-- 盘点表格 -->
                    <div class="table-responsive">
                        <table class="table table-hover align-middle">
                            <thead class="table-light">
                                <tr>
                                    <th width="50">#</th>
                                    <th>盘点单号</th>
                                    <th>盘点时间</th>
                                    <th>商品数量</th>
                                    <th>状态</th>
                                    <th>操作员</th>
                                    <th>备注</th>
                                    <th width="150">操作</th>
                                </tr>
                            </thead>
                            <tbody id="inventoryTableBody">
                                <tr>
                                    <td colspan="8" class="text-center text-muted py-4">
                                        <i class="bi bi-inbox h2"></i>
                                        <p class="mb-0">暂无盘点记录</p>
                                        <p class="small">开始新的盘点吧！</p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- 分页 -->
                    <nav id="pagination" class="d-none">
                        <ul class="pagination justify-content-center">
                            <li class="page-item disabled">
                                <a class="page-link" href="#" tabindex="-1">上一页</a>
                            </li>
                            <li class="page-item active">
                                <a class="page-link" href="#">1</a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="#">2</a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="#">3</a>
                            </li>
                            <li class="page-item">
                                <a class="page-link" href="#">下一页</a>
                            </li>
                        </ul>
                    </nav>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- 盘点详情模态框 -->
<div class="modal fade" id="detailModal" data-bs-backdrop="static" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title fw-bold">
                    <i class="bi bi-file-text"></i>
                    盘点详情
                </h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            
            <div class="modal-body">
                <div id="detailContent">
                    <div class="text-center py-4">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">加载中...</span>
                        </div>
                        <p class="mt-2">正在加载盘点详情...</p>
                    </div>
                </div>
            </div>
            
            <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                    <i class="bi bi-x-lg"></i>
                    关闭
                </button>
                <button type="button" class="btn btn-primary" id="exportDetailBtn">
                    <i class="bi bi-download"></i>
                    导出
                </button>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
    
    // 设置事件监听器
    setupEventListeners();
    
    // 加载初始数据
    loadInventories();
});

function initializePage() {
    // 设置默认日期范围（最近30天）
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 30);
    
    document.getElementById('endDate').valueAsDate = endDate;
    document.getElementById('startDate').valueAsDate = startDate;
    
    // 设置页面标题
    document.title = '历史盘点 - 保质期管理系统';
}

function setupEventListeners() {
    // 搜索按钮
    document.getElementById('searchBtn').addEventListener('click', loadInventories);
    
    // 重置按钮
    document.getElementById('resetBtn').addEventListener('click', function() {
        document.getElementById('startDate').valueAsDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
        document.getElementById('endDate').valueAsDate = new Date();
        document.getElementById('statusFilter').value = '';
        loadInventories();
    });
    
    // 刷新按钮
    document.getElementById('refreshBtn').addEventListener('click', loadInventories);
    
    // 导出按钮
    document.getElementById('exportBtn').addEventListener('click', exportInventories);
}

async function loadInventories() {
    try {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const status = document.getElementById('statusFilter').value;
        
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (status) params.append('status', status);
        
        const response = await fetch(`/api/get-inventories.php?${params.toString()}`);
        const data = await response.json();
        
        if (data.success) {
            updateStatistics(data.statistics);
            updateInventoryTable(data.inventories);
        } else {
            showAlert(`加载失败: ${data.message}`, 'danger');
        }
    } catch (error) {
        console.error('加载盘点记录失败:', error);
        showAlert('网络错误，请稍后再试', 'danger');
    }
}

function updateStatistics(stats) {
    document.getElementById('totalCount').textContent = stats.total_count || 0;
    document.getElementById('totalProducts').textContent = stats.total_products || 0;
    document.getElementById('expiredCount').textContent = stats.expired_count || 0;
    document.getElementById('weeklyCount').textContent = stats.weekly_count || 0;
}

function updateInventoryTable(inventories) {
    const tbody = document.getElementById('inventoryTableBody');
    const countBadge = document.getElementById('listCount');
    
    if (!inventories || inventories.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-inbox h2"></i>
                    <p class="mb-0">暂无盘点记录</p>
                    <p class="small">开始新的盘点吧！</p>
                </td>
            </tr>
        `;
        countBadge.textContent = '0 条记录';
        return;
    }
    
    tbody.innerHTML = inventories.map((inv, index) => {
        const statusBadge = getStatusBadge(inv.status);
        const statusText = {
            'draft': '草稿',
            'submitted': '已提交',
            'completed': '已完成'
        }[inv.status] || inv.status;
        
        return `
            <tr>
                <td>${index + 1}</td>
                <td>
                    <code>${inv.session_key}</code>
                </td>
                <td>${formatDateTime(inv.created_at)}</td>
                <td>
                    <span class="badge bg-primary-subtle text-primary">${inv.item_count} 个</span>
                </td>
                <td>${statusBadge}</td>
                <td>${inv.username || '未知'}</td>
                <td class="text-muted small">${inv.notes || '-'}</td>
                <td>
                    <div class="btn-group" role="group">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewDetail('${inv.session_key}')">
                            <i class="bi bi-eye"></i>
                            查看
                        </button>
                        ${inv.status === 'draft' ? `
                            <button class="btn btn-sm btn-outline-success" onclick="continueInventory('${inv.session_key}')">
                                <i class="bi bi-pencil"></i>
                                继续
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteInventory('${inv.session_key}')">
                            <i class="bi bi-trash"></i>
                            删除
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
    
    countBadge.textContent = `${inventories.length} 条记录`;
}

function getStatusBadge(status) {
    const badges = {
        'draft': '<span class="badge bg-secondary">草稿</span>',
        'submitted': '<span class="badge bg-warning">已提交</span>',
        'completed': '<span class="badge bg-success">已完成</span>'
    };
    
    return badges[status] || '<span class="badge bg-secondary">未知</span>';
}

function formatDateTime(datetime) {
    if (!datetime) return '-';
    
    const date = new Date(datetime);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function viewDetail(sessionKey) {
    const modal = new bootstrap.Modal(document.getElementById('detailModal'));
    const detailContent = document.getElementById('detailContent');
    
    detailContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <p class="mt-2">正在加载盘点详情...</p>
        </div>
    `;
    
    modal.show();
    
    try {
        const response = await fetch(`/api/get-inventory-detail.php?session_key=${sessionKey}`);
        const data = await response.json();
        
        if (data.success) {
            detailContent.innerHTML = renderInventoryDetail(data.inventory);
        } else {
            detailContent.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i>
                    ${data.message}
                </div>
            `;
        }
    } catch (error) {
        console.error('加载盘点详情失败:', error);
        detailContent.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i>
                加载失败，请稍后再试
            </div>
        `;
    }
}

function renderInventoryDetail(inventory) {
    return `
        <div class="row g-3 mb-3">
            <div class="col-md-6">
                <div class="card border-0 shadow-sm bg-light rounded-3">
                    <div class="card-body">
                        <small class="text-muted">盘点单号</small>
                        <div class="fw-bold">${inventory.session_key}</div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card border-0 shadow-sm bg-light rounded-3">
                    <div class="card-body">
                        <small class="text-muted">盘点时间</small>
                        <div class="fw-bold">${formatDateTime(inventory.created_at)}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <h6 class="fw-bold mb-3">
            <i class="bi bi-box"></i>
            商品列表
        </h6>
        
        <div class="table-responsive">
            <table class="table table-sm table-hover">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>SKU</th>
                        <th>商品名称</th>
                        <th>数量</th>
                        <th>过期日期</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    ${inventory.entries.map((entry, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td><code>${entry.sku || '-'}</code></td>
                            <td>${entry.product_name || '未知商品'}</td>
                            <td>
                                <span class="badge bg-primary-subtle text-primary">${entry.quantity}</span>
                            </td>
                            <td>${entry.expiry_date ? formatDate(entry.expiry_date) : '-'}</td>
                            <td>${getExpiryStatus(entry.expiry_date)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="mt-3">
            <small class="text-muted">备注</small>
            <div>${inventory.notes || '无'}</div>
        </div>
    `;
}

function formatDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

function getExpiryStatus(expiryDate) {
    if (!expiryDate) return '<span class="badge bg-secondary">未知</span>';
    
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 0) {
        return '<span class="badge bg-danger">已过期</span>';
    } else if (diffDays <= 7) {
        return '<span class="badge bg-warning">临期</span>';
    } else {
        return '<span class="badge bg-success">正常</span>';
    }
}

function continueInventory(sessionKey) {
    if (confirm('确定要继续编辑这个盘点单吗？')) {
        window.location.href = `/new.php?session=${sessionKey}`;
    }
}

async function deleteInventory(sessionKey) {
    if (!confirm('确定要删除这个盘点单吗？此操作不可恢复。')) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete-inventory.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_key: sessionKey
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('盘点单已删除', 'success');
            loadInventories();
        } else {
            showAlert(`删除失败: ${data.message}`, 'danger');
        }
    } catch (error) {
        console.error('删除盘点单失败:', error);
        showAlert('网络错误，请稍后再试', 'danger');
    }
}

function exportInventories() {
    alert('导出功能开发中...');
}

// 辅助函数
function showAlert(message, type) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.setAttribute('role', 'alert');
    
    alertContainer.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span class="ms-2">${message}</span>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertArea = document.getElementById('alert-container');
    alertArea.appendChild(alertContainer);
    
    setTimeout(() => {
        alertContainer.classList.add('fade');
        setTimeout(() => {
            alertContainer.remove();
        }, 300);
    }, 3000);
}
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
