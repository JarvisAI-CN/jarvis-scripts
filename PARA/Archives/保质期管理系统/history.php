<?php
/**
 * ========================================
 * 保质期管理系统 - 历史盘点单页面
 * 版本: v3.0.0
 * 创建日期: 2026-02-22
 * ========================================
 */

define('APP_LOADED', true);
session_start();
require_once 'includes/db.php';
require_once 'includes/check_login.php';

$conn = getDBConnection();
$user_id = $_SESSION['user_id'];
$is_admin = $_SESSION['is_admin'] ?? false;

// 处理查看详情请求
$view_session_id = $_GET['view'] ?? null;
$edit_session_id = $_GET['edit'] ?? null;

// 如果要编辑，重定向到编辑页面
if ($edit_session_id) {
    header('Location: edit_inventory.php?id=' . $edit_session_id);
    exit;
}

$page_title = '历史盘点';
include 'includes/header.php';

// 如果指定了查看某个盘点单
if ($view_session_id) {
    // 获取盘点单详情
    $stmt = $conn->prepare("
        SELECT s.*, u.username,
               (SELECT COUNT(*) FROM batches WHERE session_id = s.id) as item_count
        FROM inventory_sessions s
        LEFT JOIN users u ON s.user_id = u.id
        WHERE s.id = ?
    ");
    $stmt->bind_param("i", $view_session_id);
    $stmt->execute();
    $session = $stmt->get_result()->fetch_assoc();

    if (!$session) {
        echo '<div class="alert alert-danger">盘点单不存在</div>';
        include 'includes/footer.php';
        exit;
    }

    // 获取批次详情
    $stmt = $conn->prepare("
        SELECT b.*, p.name as product_name, p.sku
        FROM batches b
        LEFT JOIN products p ON b.product_id = p.id
        WHERE b.session_id = ?
        ORDER BY p.name, b.expiry_date
    ");
    $stmt->bind_param("i", $view_session_id);
    $stmt->execute();
    $batches = $stmt->get_result();
?>

<!-- 返回列表 -->
<div class="mb-3">
    <a href="history.php" class="btn btn-link text-decoration-none">
        <i class="bi bi-chevron-left"></i> 返回列表
    </a>
</div>

<!-- 盘点单信息 -->
<div class="custom-card mb-3">
    <div class="row">
        <div class="col-md-8">
            <h5 class="fw-bold mb-2">盘点单 #<?= $session['id'] ?></h5>
            <div class="text-muted small">
                <div><i class="bi bi-person me-2"></i>盘点人：<?= htmlspecialchars($session['username']) ?></div>
                <div><i class="bi bi-calendar me-2"></i>时间：<?= formatDate($session['created_at']) ?></div>
                <div><i class="bi bi-box-seam me-2"></i>商品数：<?= $session['item_count'] ?> 个</div>
            </div>
        </div>
        <div class="col-md-4 text-end">
            <?php if ($session['user_id'] == $user_id || $is_admin): ?>
            <a href="edit_inventory.php?id=<?= $session['id'] ?>" class="btn btn-warning btn-sm mb-2">
                <i class="bi bi-pencil me-1"></i>编辑
            </a>
            <?php endif; ?>
            <button onclick="window.print()" class="btn btn-primary btn-sm">
                <i class="bi bi-printer me-1"></i>打印
            </button>
        </div>
    </div>
</div>

<!-- 商品明细 -->
<div class="custom-card">
    <h6 class="fw-bold mb-3">📦 商品明细</h6>

    <?php if ($batches->num_rows > 0): ?>
    <div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead>
                <tr>
                    <th>SKU</th>
                    <th>商品名称</th>
                    <th>有效期</th>
                    <th>剩余天数</th>
                    <th>状态</th>
                    <th>数量</th>
                </tr>
            </thead>
            <tbody>
                <?php
                $today = date('Y-m-d');
                while ($batch = $batches->fetch_assoc()):
                    $expiry = $batch['expiry_date'];
                    $days_left = (strtotime($expiry) - strtotime($today)) / 86400;

                    if ($days_left < 0) {
                        $status = '<span class="badge bg-danger">已过期</span>';
                    } elseif ($days_left <= 7) {
                        $status = '<span class="badge bg-warning">临期</span>';
                    } else {
                        $status = '<span class="badge bg-success">健康</span>';
                    }
                ?>
                <tr>
                    <td><code><?= htmlspecialchars($batch['sku']) ?></code></td>
                    <td><?= htmlspecialchars($batch['product_name']) ?></td>
                    <td><?= $expiry ?></td>
                    <td><?= round($days_left) ?> 天</td>
                    <td><?= $status ?></td>
                    <td><strong><?= $batch['quantity'] ?></strong></td>
                </tr>
                <?php endwhile; ?>
            </tbody>
        </table>
    </div>
    <?php else: ?>
    <div class="text-center text-muted py-4">
        <i class="bi bi-inbox fs-1 d-block mb-2"></i>
        暂无数据
    </div>
    <?php endif; ?>
</div>

<?php
} else {
    // 显示盘点单列表
    $page = $_GET['page'] ?? 1;
    $per_page = 20;
    $offset = ($page - 1) * $per_page;

    // 统计总数
    $result = $conn->query("SELECT COUNT(*) as total FROM inventory_sessions");
    $total = $result->fetch_assoc()['total'];
    $total_pages = ceil($total / $per_page);

    // 获取盘点单列表
    $stmt = $conn->prepare("
        SELECT s.*, u.username,
               (SELECT COUNT(*) FROM batches WHERE session_id = s.id) as item_count
        FROM inventory_sessions s
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
        LIMIT ? OFFSET ?
    ");
    $stmt->bind_param("ii", $per_page, $offset);
    $stmt->execute();
    $sessions = $stmt->get_result();
?>

<!-- 页面标题 -->
<div class="d-flex justify-content-between align-items-center mb-3">
    <h4 class="fw-bold mb-0">📋 历史盘点单</h4>
    <a href="inventory.php" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i>新建盘点
    </a>
</div>

<!-- 统计信息 -->
<div class="custom-card mb-3">
    <div class="row text-center">
        <div class="col-md-4">
            <div class="h4 mb-1"><?= number_format($total) ?></div>
            <small class="text-muted">总盘点单数</small>
        </div>
        <div class="col-md-4">
            <?php
            $result = $conn->query("SELECT COUNT(DISTINCT user_id) as count FROM inventory_sessions");
            $users = $result->fetch_assoc()['count'];
            ?>
            <div class="h4 mb-1"><?= $users ?></div>
            <small class="text-muted">参与人数</small>
        </div>
        <div class="col-md-4">
            <?php
            $result = $conn->query("SELECT SUM(item_count) as total FROM (SELECT COUNT(*) as item_count FROM batches GROUP BY session_id) as t");
            $items = $result->fetch_assoc()['total'] ?: 0;
            ?>
            <div class="h4 mb-1"><?= number_format($items) ?></div>
            <small class="text-muted">总商品数</small>
        </div>
    </div>
</div>

<!-- 盘点单列表 -->
<?php if ($sessions->num_rows > 0): ?>
<div class="custom-card">
    <div class="list-group list-group-flush">
        <?php while ($session = $sessions->fetch_assoc()): ?>
        <a href="history.php?view=<?= $session['id'] ?>"
           class="list-group-item list-group-item-action">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">
                        #<?= $session['id'] ?> -
                        <?= formatDate($session['created_at']) ?>
                    </div>
                    <div class="small text-muted">
                        <i class="bi bi-person me-1"></i><?= htmlspecialchars($session['username']) ?>
                        <span class="mx-2">•</span>
                        <i class="bi bi-box-seam me-1"></i><?= $session['item_count'] ?> 个商品
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2">
                    <?php if ($session['user_id'] == $user_id || $is_admin): ?>
                    <a href="edit_inventory.php?id=<?= $session['id'] ?>"
                       class="btn btn-sm btn-outline-warning"
                       onclick="event.stopPropagation()">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <?php endif; ?>
                    <i class="bi bi-chevron-right text-muted"></i>
                </div>
            </div>
        </a>
        <?php endwhile; ?>
    </div>
</div>

<!-- 分页 -->
<?php if ($total_pages > 1): ?>
<nav aria-label="分页导航" class="mt-3">
    <ul class="pagination justify-content-center">
        <?php if ($page > 1): ?>
        <li class="page-item">
            <a class="page-link" href="history.php?page=<?= $page - 1 ?>">上一页</a>
        </li>
        <?php endif; ?>

        <?php for ($i = max(1, $page - 2); $i <= min($total_pages, $page + 2); $i++): ?>
        <li class="page-item <?= $i == $page ? 'active' : '' ?>">
            <a class="page-link" href="history.php?page=<?= $i ?>"><?= $i ?></a>
        </li>
        <?php endfor; ?>

        <?php if ($page < $total_pages): ?>
        <li class="page-item">
            <a class="page-link" href="history.php?page=<?= $page + 1 ?>">下一页</a>
        </li>
        <?php endif; ?>
    </ul>
</nav>
<?php endif; ?>

<?php else: ?>
<div class="custom-card text-center py-5">
    <i class="bi bi-inbox fs-1 d-block mb-3 text-muted"></i>
    <h5>还没有盘点单</h5>
    <p class="text-muted mb-3">开始第一次盘点吧</p>
    <a href="inventory.php" class="btn btn-primary">
        <i class="bi bi-plus-circle me-1"></i>新建盘点
    </a>
</div>
<?php endif; ?>

<?php } // end if (view vs list) ?>

<?php include 'includes/footer.php'; ?>
