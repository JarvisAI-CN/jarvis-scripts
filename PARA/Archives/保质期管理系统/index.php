<?php
/**
 * ========================================
 * 保质期管理系统 - 主页（仪表盘）
 * 版本: v3.0.0
 * 创建日期: 2026-02-22
 * ========================================
 */

define('APP_LOADED', true);
session_start();
require_once 'includes/db.php';
require_once 'includes/check_login.php';

// 获取统计数据
$conn = getDBConnection();
$user_id = $_SESSION['user_id'];

// 待处理商品（过期、临期）
$stats = [
    'expired' => 0,
    'urgent' => 0,
    'healthy' => 0,
    'total_products' => 0,
    'recent_sessions' => 0
];

// 统计过期商品
$result = $conn->query("SELECT COUNT(*) as count FROM products WHERE expiry_date < CURDATE()");
$stats['expired'] = $result->fetch_assoc()['count'];

// 统计临期商品（7天内过期）
$result = $conn->query("SELECT COUNT(*) as count FROM products WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)");
$stats['urgent'] = $result->fetch_assoc()['count'];

// 统计健康商品
$result = $conn->query("SELECT COUNT(*) as count FROM products WHERE expiry_date > DATE_ADD(CURDATE(), INTERVAL 7 DAY)");
$stats['healthy'] = $result->fetch_assoc()['count'];

// 总商品数
$stats['total_products'] = $stats['expired'] + $stats['urgent'] + $stats['healthy'];

// 最近的盘点单（最近5条）
$recent_sessions = $conn->query("
    SELECT s.*, u.username,
           (SELECT COUNT(*) FROM batches WHERE session_id = s.id) as item_count
    FROM inventory_sessions s
    LEFT JOIN users u ON s.user_id = u.id
    ORDER BY s.created_at DESC
    LIMIT 5
");

$page_title = '首页';
include 'includes/header.php';
?>

<!-- 欢迎卡片 -->
<div class="custom-card">
    <h4 class="mb-3">👋 你好，<?= htmlspecialchars($_SESSION['username']) ?>！</h4>
    <p class="text-muted mb-0">今天是 <?= date('Y年m月d日') ?>，以下是系统概览</p>
</div>

<!-- 统计概览 -->
<div class="custom-card">
    <h5 class="fw-bold mb-3">📊 商品状态统计</h5>

    <div class="progress mb-3" style="height: 25px;">
        <?php
        $total = $stats['total_products'] ?: 1; // 避免除零
        $expired_pct = round($stats['expired'] / $total * 100);
        $urgent_pct = round($stats['urgent'] / $total * 100);
        $healthy_pct = round($stats['healthy'] / $total * 100);
        ?>
        <div class="progress-bar bg-danger" style="width: <?= $expired_pct ?>%"
             title="已过期: <?= $stats['expired'] ?>个 (<?= $expired_pct ?>%)">
            <?= $stats['expired'] ?>
        </div>
        <div class="progress-bar bg-warning" style="width: <?= $urgent_pct ?>%"
             title="临期: <?= $stats['urgent'] ?>个 (<?= $urgent_pct ?>%)">
            <?= $stats['urgent'] ?>
        </div>
        <div class="progress-bar bg-success" style="width: <?= $healthy_pct ?>%"
             title="健康: <?= $stats['healthy'] ?>个 (<?= $healthy_pct ?>%)">
            <?= $stats['healthy'] ?>
        </div>
    </div>

    <div class="row text-center g-3">
        <div class="col-4">
            <div class="p-3 rounded bg-danger bg-opacity-10">
                <div class="h3 mb-1 text-danger"><?= $stats['expired'] ?></div>
                <small class="text-muted">已过期</small>
            </div>
        </div>
        <div class="col-4">
            <div class="p-3 rounded bg-warning bg-opacity-10">
                <div class="h3 mb-1 text-warning"><?= $stats['urgent'] ?></div>
                <small class="text-muted">临期7天</small>
            </div>
        </div>
        <div class="col-4">
            <div class="p-3 rounded bg-success bg-opacity-10">
                <div class="h3 mb-1 text-success"><?= $stats['healthy'] ?></div>
                <small class="text-muted">健康</small>
            </div>
        </div>
    </div>

    <div class="text-center mt-3">
        <span class="badge bg-primary">总计 <?= $stats['total_products'] ?> 个商品</span>
    </div>
</div>

<!-- 快速入口 -->
<div class="row g-3 mb-3">
    <div class="col-md-6">
        <a href="inventory.php" class="btn btn-primary w-100 py-4 text-start" style="border-radius: 16px;">
            <i class="bi bi-qr-code-scan fs-2 me-3"></i>
            <div>
                <div class="fw-bold fs-5">新增盘点</div>
                <small>扫码录入商品保质期</small>
            </div>
        </a>
    </div>
    <div class="col-md-6">
        <a href="history.php" class="btn btn-success w-100 py-4 text-start" style="border-radius: 16px;">
            <i class="bi bi-clock-history fs-2 me-3"></i>
            <div>
                <div class="fw-bold fs-5">历史记录</div>
                <small>查看过往盘点单</small>
            </div>
        </a>
    </div>
</div>

<!-- 最近盘点单 -->
<?php if ($recent_sessions && $recent_sessions->num_rows > 0): ?>
<div class="custom-card">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="fw-bold mb-0">📝 最近盘点</h5>
        <a href="history.php" class="btn btn-sm btn-light">查看全部</a>
    </div>

    <div class="list-group list-group-flush">
        <?php while ($session = $recent_sessions->fetch_assoc()): ?>
        <a href="history.php?view=<?= $session['id'] ?>"
           class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
            <div>
                <div class="fw-bold">
                    <?= formatDate($session['created_at']) ?>
                </div>
                <small class="text-muted">
                    <i class="bi bi-person me-1"></i><?= htmlspecialchars($session['username']) ?>
                    <span class="mx-2">•</span>
                    <i class="bi bi-box-seam me-1"></i><?= $session['item_count'] ?> 个商品
                </small>
            </div>
            <i class="bi bi-chevron-right text-muted"></i>
        </a>
        <?php endwhile; ?>
    </div>
</div>
<?php endif; ?>

<?php include 'includes/footer.php'; ?>
