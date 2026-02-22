
<?php
session_start();
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>PHP调试</title>
</head>
<body>
    <h1>保质期管理系统 v2.14.2</h1>
    
    <?php if(!isset($_SESSION['user_id'])): ?>
    <div style="background: #ffdddd; padding: 20px; margin: 10px;">
        <h3>🔐 请登录</h3>
        <p>这是登录页面</p>
        <form method="POST" action="?api=login">
            <input type="text" name="username" placeholder="用户名" required>
            <input type="password" name="password" placeholder="密码" required>
            <button type="submit">登录</button>
        </form>
    </div>
    <?php else: ?>
    <div style="background: #ddffdd; padding: 20px; margin: 10px;">
        <h3>✅ 已登录</h3>
        <p>这是主页面</p>
        <a href="?api=logout">登出</a>
    </div>
    <?php endif; ?>
    
    <?php
    // API路由
    if (isset($_GET['api'])) {
        header('Content-Type: application/json');
        
        if ($_GET['api'] === 'login') {
            $username = $_POST['username'] ?? 'admin';
            $password = $_POST['password'] ?? 'pandian123';
            
            if ($username === 'admin' && $password === 'pandian123') {
                $_SESSION['user_id'] = 1;
                echo json_encode(['success' => true]);
            } else {
                echo json_encode(['success' => false, 'message' => '账号或密码错误']);
            }
            exit;
        }
        
        if ($_GET['api'] === 'logout') {
            session_destroy();
            echo json_encode(['success' => true]);
            exit;
        }
    }
    ?>
</body>
</html>
