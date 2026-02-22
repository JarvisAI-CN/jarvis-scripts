<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="description" content="<?php echo APP_DESCRIPTION; ?>">
    <meta name="keywords" content="保质期管理,盘点系统,库存管理">
    <meta name="author" content="OpenClaw AI">
    <meta name="robots" content="noindex, nofollow">
    
    <title><?php echo $pageTitle ?? '保质期管理系统'; ?></title>
    
    <!-- Bootstrap 5.3 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    <!-- Custom Styles -->
    <link rel="stylesheet" href="<?php echo BASE_URL; ?>/assets/css/main.css">
    <link rel="stylesheet" href="<?php echo BASE_URL; ?>/assets/css/<?php echo $customCss ?? 'default'; ?>.css">
    
    <!-- HTML5 QR Code Scanner -->
    <?php if ($pageName === 'new'): ?>
        <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <?php endif; ?>
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Security Headers -->
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Referrer-Policy" content="no-referrer-when-downgrade">
    
    <!-- CSRF Token Meta Tag -->
    <meta name="csrf-token" content="<?php echo generateCSRFToken(); ?>">
</head>
<body class="bg-light">
    <div class="container-fluid min-vh-100">
        <!-- Top Navigation -->
        <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm border-bottom">
            <div class="container">
                <a class="navbar-brand" href="<?php echo BASE_URL; ?>/index.php">
                    <i class="bi bi-calendar-check text-primary"></i>
                    <span class="fw-bold text-dark">保质期管理系统 v<?php echo APP_VERSION; ?></span>
                </a>
                
                <?php if (checkAuth()): ?>
                    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    
                    <div class="collapse navbar-collapse" id="navbarNav">
                        <ul class="navbar-nav ms-auto">
                            <li class="nav-item">
                                <a class="nav-link <?php echo ($pageName === 'index') ? 'active' : ''; ?>" href="<?php echo BASE_URL; ?>/index.php">
                                    <i class="bi bi-house-door"></i>
                                    首页
                                </a>
                            </li>
                            
                            <li class="nav-item">
                                <a class="nav-link <?php echo ($pageName === 'new') ? 'active' : ''; ?>" href="<?php echo BASE_URL; ?>/new.php">
                                    <i class="bi bi-plus-circle"></i>
                                    新增盘点
                                </a>
                            </li>
                            
                            <li class="nav-item">
                                <a class="nav-link <?php echo ($pageName === 'past') ? 'active' : ''; ?>" href="<?php echo BASE_URL; ?>/past.php">
                                    <i class="bi bi-clock-history"></i>
                                    历史盘点
                                </a>
                            </li>
                            
                            <?php if (isAdmin()): ?>
                                <li class="nav-item">
                                    <a class="nav-link <?php echo ($pageName === 'settings') ? 'active' : ''; ?>" href="<?php echo BASE_URL; ?>/settings.php">
                                        <i class="bi bi-gear"></i>
                                        系统设置
                                    </a>
                                </li>
                            <?php endif; ?>
                            
                            <li class="nav-item dropdown">
                                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="bi bi-person-circle"></i>
                                    <?php echo htmlEscape($_SESSION['realname'] ?? $_SESSION['username']); ?>
                                </a>
                                <ul class="dropdown-menu dropdown-menu-end">
                                    <li><a class="dropdown-item" href="#">
                                        <i class="bi bi-person"></i>
                                        个人中心
                                    </a></li>
                                    <li><hr class="dropdown-divider"></li>
                                    <li><a class="dropdown-item text-danger" href="<?php echo BASE_URL; ?>/api/logout.php">
                                        <i class="bi bi-box-arrow-right"></i>
                                        退出登录
                                    </a></li>
                                </ul>
                            </li>
                        </ul>
                    </div>
                <?php endif; ?>
            </div>
        </nav>
        
        <!-- Alert Container -->
        <div class="container mt-3" id="alert-container">
            <!-- Success alert -->
            <div id="alert-success" class="alert alert-success alert-dismissible fade show d-none" role="alert">
                <i class="bi bi-check-circle-fill"></i>
                <span id="alert-success-text"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            
            <!-- Error alert -->
            <div id="alert-error" class="alert alert-danger alert-dismissible fade show d-none" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <span id="alert-error-text"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            
            <!-- Warning alert -->
            <div id="alert-warning" class="alert alert-warning alert-dismissible fade show d-none" role="alert">
                <i class="bi bi-exclamation-triangle-fill"></i>
                <span id="alert-warning-text"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            
            <!-- Info alert -->
            <div id="alert-info" class="alert alert-info alert-dismissible fade show d-none" role="alert">
                <i class="bi bi-info-circle-fill"></i>
                <span id="alert-info-text"></span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        </div>
        
        <!-- Main Content -->
        <main class="container mt-4 mb-5" id="main-content">
