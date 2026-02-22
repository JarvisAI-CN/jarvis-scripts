
<?php
// debug_php.php - 用于调试PHP登录判断的最小文件
session_start();
echo "PHP执行成功<br>";
echo "SESSION['user_id']: " . (isset($_SESSION['user_id']) ? $_SESSION['user_id'] : "未设置") . "<br>";

// 测试登录
if (isset($_GET['login'])) {
    $_SESSION['user_id'] = 1;
    echo "登录成功<br>";
    header('Location: ?');
    exit;
}

// 测试登出
if (isset($_GET['logout'])) {
    session_destroy();
    echo "登出成功<br>";
    header('Location: ?');
    exit;
}
?>

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>PHP调试</title>
</head>
<body>
    <h2>PHP登录判断调试</h2>
    <p>当前URL: <?php echo $_SERVER['REQUEST_URI']; ?></p>
    <p>会话ID: <?php echo session_id(); ?></p>
    
    <?php if(!isset($_SESSION['user_id'])): ?>
    <div style="background: #ffdddd; padding: 20px; margin: 10px;">
        <h3>🔐 请登录</h3>
        <p>这是登录页面</p>
        <a href="?login=1">模拟登录</a>
    </div>
    <?php else: ?>
    <div style="background: #ddffdd; padding: 20px; margin: 10px;">
        <h3>✅ 已登录</h3>
        <p>这是主页面</p>
        <a href="?logout=1">登出</a>
    </div>
    <?php endif; ?>
    
    <div style="background: #eeeeee; padding: 20px; margin: 10px;">
        <h4>Session内容:</h4>
        <pre><?php print_r($_SESSION); ?></pre>
    </div>
</body>
</html>
