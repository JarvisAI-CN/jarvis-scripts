<?php
/**
 * 保质期管理系统 v3.0.0 自动安装脚本
 * 上传此文件到服务器，访问即可自动安装
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>🚀 正在安装保质期管理系统 v3.0.0...</h1>";
echo "<style>body{font-family:-apple-system,sans-serif;padding:20px;} .success{color:green;} .error{color:red;}</style>";

// 文件列表
$files = [
    'login.php' => '文件内容在底部',
    'inventory.php' => '文件内容在底部',
    'history.php' => '文件内容在底部',
    'logout.php' => '文件内容在底部',
    'index.php' => '文件内容在底部',
    'includes/db.php' => '文件内容在底部',
    'includes/check_login.php' => '文件内容在底部',
    'includes/header.php' => '文件内容在底部',
    'includes/footer.php' => '文件内容在底部',
];

// 备份旧文件
if (file_exists('index.php')) {
    copy('index.php', 'index_v2.14.2_backup_' . date('YmdHis') . '.php');
    echo "<p class='success'>✅ 已备份旧版index.php</p>";
}

// 创建includes目录
if (!is_dir('includes')) {
    mkdir('includes', 0755, true);
    echo "<p class='success'>✅ 已创建includes目录</p>";
}

// 下载文件从GitHub
$repoUrl = 'https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/';
$fileMap = [
    'login.php' => 'login.php',
    'inventory.php' => 'inventory.php',
    'history.php' => 'history.php',
    'logout.php' => 'logout.php',
    'index.php' => 'index.php',
    'includes/db.php' => 'includes/db.php',
    'includes/check_login.php' => 'includes/check_login.php',
    'includes/header.php' => 'includes/header.php',
    'includes/footer.php' => 'includes/footer.php',
];

foreach ($fileMap as $localPath => $remotePath) {
    $url = $repoUrl . $remotePath;
    $content = @file_get_contents($url);

    if ($content === false) {
        echo "<p class='error'>❌ 无法下载 $localPath</p>";
        continue;
    }

    // 确保目录存在
    $dir = dirname($localPath);
    if (!is_dir($dir)) {
        mkdir($dir, 0755, true);
    }

    if (file_put_contents($localPath, $content)) {
        echo "<p class='success'>✅ 已创建 $localPath</p>";
    } else {
        echo "<p class='error'>❌ 无法写入 $localPath</p>";
    }
}

echo "<hr>";
echo "<h2>✅ 安装完成！</h2>";
echo "<p><a href='login.php' style='font-size:20px;'>👉 点击访问新版系统</a></p>";
echo "<p><small>如果页面显示异常，请恢复备份文件</small></p>";
?>
