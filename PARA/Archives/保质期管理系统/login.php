<?php
/**
 * ========================================
 * 保质期管理系统 - 登录页面
 * 版本: v3.0.0
 * 创建日期: 2026-02-22
 * ========================================
 */

session_start();
require_once 'includes/db.php';

// 如果已登录，跳转到主页
if (isset($_SESSION['user_id'])) {
    header('Location: index.php');
    exit;
}

// 处理登录请求
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    $conn = getDBConnection();
    $stmt = $conn->prepare("SELECT id, password, is_admin FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        if (password_verify($password, $user['password'])) {
            $_SESSION['user_id'] = $user['id'];
            $_SESSION['username'] = $username;
            $_SESSION['is_admin'] = $user['is_admin'];

            // 记录登录时间
            $conn->query("UPDATE users SET last_login = NOW() WHERE id = {$user['id']}");

            header('Location: index.php');
            exit;
        }
    }

    $error = "用户名或密码错误";
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - 保质期管理系统</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --apple-blue: #007AFF;
            --apple-light-blue: #E3F2FD;
            --apple-bg: #F5F5F7;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
        }

        .login-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }

        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }

        .login-icon {
            font-size: 3rem;
            color: var(--apple-blue);
            margin-bottom: 10px;
        }

        .form-control {
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid #E0E0E0;
            font-size: 1rem;
        }

        .form-control:focus {
            border-color: var(--apple-blue);
            box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.1);
        }

        .btn-login {
            background: var(--apple-blue);
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .btn-login:hover {
            background: #0051D5;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 122, 255, 0.3);
        }

        .alert {
            border-radius: 12px;
            border: none;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <div class="login-icon">🔐</div>
            <h2 class="fw-bold mb-1">保质期管理系统</h2>
            <p class="text-muted small mb-0">请登录以继续</p>
        </div>

        <?php if (isset($error)): ?>
            <div class="alert alert-danger mb-3">
                <i class="bi bi-exclamation-triangle-fill me-2"></i><?= htmlspecialchars($error) ?>
            </div>
        <?php endif; ?>

        <form method="POST">
            <div class="mb-3">
                <label class="form-label fw-semibold">用户名</label>
                <input type="text" name="username" class="form-control" placeholder="请输入用户名" required autofocus>
            </div>
            <div class="mb-4">
                <label class="form-label fw-semibold">密码</label>
                <input type="password" name="password" class="form-control" placeholder="请输入密码" required>
            </div>
            <button type="submit" class="btn btn-primary btn-login w-100">
                进入系统
            </button>
        </form>

        <div class="text-center mt-4">
            <small class="text-muted">
                版本 3.0.0 | Powered by 贾维斯
            </small>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
