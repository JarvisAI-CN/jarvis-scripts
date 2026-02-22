<?php
/**
 * 保质期管理系统 - v4.0.0 首页/门户页面
 * 功能导航和系统概览
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
$pageTitle = '首页 - 保质期管理系统';
$pageName = 'index';
?>

<?php require_once __DIR__ . '/../includes/header.php'; ?>

<div class="container">
    <div class="row g-4">
        <!-- 系统概览卡片 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-graph-up-arrow text-primary"></i>
                            系统概览
                        </h5>
                        <span class="badge bg-primary-subtle text-primary"><?php echo date('Y年m月d日'); ?></span>
                    </div>
                    
                    <div id="systemOverview" class="d-grid gap-3">
                        <!-- 实时统计将通过API获取 -->
                        <div class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-2 text-muted">正在加载系统数据...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 快速操作卡片 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-lightning text-warning"></i>
                            快速操作
                        </h5>
                        <span class="badge bg-warning-subtle text-warning">常用功能</span>
                    </div>
                    
                    <div class="d-grid gap-3">
                        <a href="/new.php" class="btn btn-primary btn-lg text-start">
                            <i class="bi bi-qr-code-scan"></i>
                            新增盘点
                        </a>
                        
                        <a href="/past.php" class="btn btn-outline-primary btn-lg text-start">
                            <i class="bi bi-clock-history"></i>
                            历史盘点
                        </a>
                        
                        <?php if (isAdmin()): ?>
                            <a href="/settings.php" class="btn btn-outline-secondary btn-lg text-start">
                                <i class="bi bi-gear"></i>
                                系统设置
                            </a>
                        <?php endif; ?>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 待处理任务卡片 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-bell text-danger"></i>
                            待处理任务
                        </h5>
                        <span class="badge bg-danger-subtle text-danger" id="pendingTasksCount">0</span>
                    </div>
                    
                    <div id="pendingTasks" class="d-grid gap-3">
                        <div class="text-center py-4">
                            <div class="spinner-border text-danger" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-2 text-muted">正在加载待处理任务...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 最近活动卡片 -->
        <div class="col-lg-6">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-clock-history text-success"></i>
                            最近活动
                        </h5>
                        <span class="badge bg-success-subtle text-success">最近5条</span>
                    </div>
                    
                    <div id="recentActivity" class="d-grid gap-3">
                        <div class="text-center py-4">
                            <div class="spinner-border text-success" role="status">
                                <span class="visually-hidden">加载中...</span>
                            </div>
                            <p class="mt-2 text-muted">正在加载最近活动...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 通知卡片 -->
        <div class="col-lg-12">
            <div class="card shadow-sm border-0 rounded-4">
                <div class="card-body">
                    <div class="d-flex align-items-center justify-content-between mb-4">
                        <h5 class="card-title fw-bold mb-0">
                            <i class="bi bi-info-circle text-info"></i>
                            系统通知
                        </h5>
                        <span class="badge bg-info-subtle text-info">公告</span>
                    </div>
                    
                    <div id="systemNotifications" class="d-grid gap-3">
                        <div class="alert alert-primary" role="alert">
                            <i class="bi bi-info-circle"></i>
                            <strong>系统公告</strong> v4.0.0 版本已正式上线！
                        </div>
                        
                        <div class="alert alert-success" role="alert">
                            <i class="bi bi-check-circle"></i>
                            <strong>欢迎使用</strong> 保质期管理系统专业版。
                        </div>
                        
                        <div class="alert alert-warning" role="alert">
                            <i class="bi bi-exclamation-triangle"></i>
                            <strong>重要提示</strong> 请定期备份您的数据，以防丢失。
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // 页面加载完成后初始化
    loadSystemOverview();
    loadPendingTasks();
    loadRecentActivity();
    
    // 设置自动刷新
    setInterval(loadSystemOverview, 30000); // 30秒刷新一次
});

async function loadSystemOverview() {
    try {
        const response = await fetch('/api/overview.php');
        const data = await response.json();
        
        if (data.success) {
            const overview = document.getElementById('systemOverview');
            overview.innerHTML = `
                <div class="row g-3">
                    <div class="col-6">
                        <div class="d-flex align-items-center justify-content-between">
                            <span class="text-muted">总商品数:</span>
                            <span class="fw-bold text-primary">${data.data.totalProducts}</span>
                        </div>
                    </div>
                    
                    <div class="col-6">
                        <div class="d-flex align-items-center justify-content-between">
                            <span class="text-muted">总盘点数:</span>
                            <span class="fw-bold text-primary">${data.data.totalInventories}</span>
                        </div>
                    </div>
                    
                    <div class="col-6">
                        <div class="d-flex align-items-center justify-content-between">
                            <span class="text-muted">已过期商品:</span>
                            <span class="fw-bold text-danger">${data.data.expiredProducts}</span>
                        </div>
                    </div>
                    
                    <div class="col-6">
                        <div class="d-flex align-items-center justify-content-between">
                            <span class="text-muted">库存金额:</span>
                            <span class="fw-bold text-success">¥${data.data.totalValue.toFixed(2)}</span>
                        </div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载系统概览失败:', error);
    }
}

async function loadPendingTasks() {
    try {
        const response = await fetch('/api/pending-tasks.php');
        const data = await response.json();
        
        if (data.success) {
            const pendingTasks = document.getElementById('pendingTasks');
            const countBadge = document.getElementById('pendingTasksCount');
            
            if (data.data.length === 0) {
                pendingTasks.innerHTML = `
                    <div class="alert alert-info text-center">
                        <i class="bi bi-check-circle"></i>
                        <strong>暂无待处理任务</strong><br>
                        系统运行正常
                    </div>
                `;
                countBadge.textContent = '0';
            } else {
                countBadge.textContent = data.data.length;
                
                pendingTasks.innerHTML = data.data.map(task => `
                    <div class="card border-0 shadow-sm bg-light rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center justify-content-between">
                                <div class="d-flex align-items-center gap-2">
                                    <i class="bi bi-exclamation-triangle text-danger"></i>
                                    <strong>${task.title}</strong>
                                </div>
                                <span class="badge ${task.priority === 'high' ? 'bg-danger' : 'bg-warning'}">
                                    ${task.priority === 'high' ? '高' : '中'}
                                </span>
                            </div>
                            <div class="mt-2 text-muted small">${task.description}</div>
                            <div class="mt-3 d-flex justify-content-between align-items-center">
                                <small class="text-muted">${task.time}</small>
                                <a href="${task.url}" class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-arrow-right"></i>
                                    处理
                                </a>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('加载待处理任务失败:', error);
    }
}

async function loadRecentActivity() {
    try {
        const response = await fetch('/api/recent-activity.php');
        const data = await response.json();
        
        if (data.success) {
            const recentActivity = document.getElementById('recentActivity');
            
            if (data.data.length === 0) {
                recentActivity.innerHTML = `
                    <div class="alert alert-info text-center">
                        <i class="bi bi-clock-history"></i>
                        <strong>暂无活动记录</strong><br>
                        开始使用系统吧！
                    </div>
                `;
            } else {
                recentActivity.innerHTML = data.data.map(activity => `
                    <div class="card border-0 shadow-sm bg-light rounded-3">
                        <div class="card-body">
                            <div class="d-flex align-items-center gap-3">
                                <div class="d-inline-flex align-items-center justify-content-center" style="width: 40px; height: 40px; background: ${activity.color}; color: white; border-radius: 50%;">
                                    <i class="bi ${activity.icon}"></i>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="fw-bold">${activity.title}</div>
                                    <div class="text-muted small">${activity.description}</div>
                                </div>
                                <div class="text-muted small">${activity.time}</div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('加载最近活动失败:', error);
    }
}

// 响应式调整
window.addEventListener('resize', function() {
    // 页面大小改变时重新布局
    const container = document.querySelector('.container');
    if (container) {
        container.classList.add('zoom-in');
        setTimeout(() => container.classList.remove('zoom-in'), 300);
    }
});

// 性能优化：使用 Intersection Observer 实现懒加载
const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            // 这里可以添加图片懒加载逻辑
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// 为卡片添加动画效果
document.querySelectorAll('.card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    
    observer.observe(card);
});
</script>

<?php require_once __DIR__ . '/../includes/footer.php'; ?>
