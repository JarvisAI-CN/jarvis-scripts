<?php
/**
 * 公共头部文件 - 简化版
 */

if (!defined('APP_LOADED')) {
    die('Direct access not allowed');
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title><?= $page_title ?? '保质期管理系统' ?> - 保质期管理 v3.0.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <style>
        :root { --apple-blue: #007AFF; --apple-light-blue: #E3F2FD; --apple-bg: #F5F5F7; }
        body { background: var(--apple-bg); font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif; }
        .app-header { background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); padding: 12px 0; border-bottom: 1px solid rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }
        .custom-card { background: white; border-radius: 16px; padding: 16px; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); }
        .nav-link { color: #333; font-weight: 500; padding: 8px 16px !important; border-radius: 10px; transition: all 0.3s; }
        .nav-link:hover, .nav-link.active { background: var(--apple-light-blue); color: var(--apple-blue); }
        .btn-primary { background: var(--apple-blue); border-color: var(--apple-blue); border-radius: 12px; }
        .btn-primary:hover { background: #0051D5; }
        #scanOverlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: #000; z-index: 2000; display: none; }
    </style>
</head>
<body>
    <nav class="app-header">
        <div class="container d-flex justify-content-between align-items-center">
            <h1 class="h5 mb-0 fw-bold" style="color: var(--apple-blue)">
                <i class="bi bi-box-seam me-2"></i>保质期管理
            </h1>
            <div class="d-flex align-items-center gap-2">
                <a href="index.php" class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'index.php' ? 'active' : '' ?>">
                    <i class="bi bi-house-door me-1"></i>首页
                </a>
                <a href="inventory.php" class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'inventory.php' ? 'active' : '' ?>">
                    <i class="bi bi-qr-code-scan me-1"></i>盘点
                </a>
                <a href="history.php" class="nav-link <?= basename($_SERVER['PHP_SELF']) == 'history.php' ? 'active' : '' ?>">
                    <i class="bi bi-clock-history me-1"></i>历史
                </a>
                <div class="dropdown">
                    <button class="btn btn-light btn-sm rounded-pill" data-bs-toggle="dropdown">
                        <i class="bi bi-person-circle me-1"></i><?= htmlspecialchars($_SESSION['username'] ?? 'User') ?>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow border-0">
                        <?php if ($_SESSION['is_admin'] ?? false): ?>
                        <li><a class="dropdown-item" href="admin.php"><i class="bi bi-gear me-2"></i>管理后台</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <?php endif; ?>
                        <li><a class="dropdown-item text-danger" href="logout.php"><i class="bi bi-box-arrow-right me-2"></i>退出登录</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>
    <div class="container py-4">
