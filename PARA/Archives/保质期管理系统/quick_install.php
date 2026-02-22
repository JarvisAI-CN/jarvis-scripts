<?php
/**
 * 快速安装脚本 v3.0.0
 * 上传此单个文件到服务器，访问即可自动安装
 */

error_reporting(E_ALL);
ini_set('display_errors', 1);

?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>安装保质期管理系统 v3.0.0</title>
    <style>
        body { font-family: -apple-system, sans-serif; padding: 20px; background: #f5f5f7; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        h1 { color: #007AFF; }
        .success { color: #34C759; }
        .error { color: #FF3B30; }
        .btn { display: inline-block; padding: 12px 24px; background: #007AFF; color: white; text-decoration: none; border-radius: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 安装保质期管理系统 v3.0.0</h1>

        <?php
        // 备份旧文件
        if (file_exists('index.php')) {
            $backup = 'index_v2.14.2_backup_' . date('YmdHis') . '.php';
            copy('index.php', $backup);
            echo "<p class='success'>✅ 已备份旧版 index.php → $backup</p>";
        }

        // 创建includes目录
        if (!is_dir('includes')) {
            mkdir('includes', 0755, true);
            echo "<p class='success'>✅ 已创建 includes 目录</p>";
        }

        // 文件下载URL
        $baseUrl = 'https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/';
        $files = [
            'login.php',
            'inventory.php',
            'history.php',
            'logout.php',
            'index.php',
            'includes/db.php',
            'includes/check_login.php',
            'includes/header.php',
            'includes/footer.php',
        ];

        $success = 0;
        foreach ($files as $file) {
            $url = $baseUrl . $file;
            $content = @file_get_contents($url);

            if ($content === false) {
                echo "<p class='error'>❌ 无法下载 $file</p>";
                continue;
            }

            // 确保目录存在
            $dir = dirname($file);
            if ($dir !== '.' && !is_dir($dir)) {
                mkdir($dir, 0755, true);
            }

            if (file_put_contents($file, $content)) {
                echo "<p class='success'>✅ 已安装 $file</p>";
                $success++;
            } else {
                echo "<p class='error'>❌ 无法写入 $file</p>";
            }
        }

        echo "<hr>";
        if ($success === count($files)) {
            echo "<h2 class='success'>✅ 安装完成！</h2>";
            echo "<a href='login.php' class='btn'>👉 访问新版系统</a>";
        } else {
            echo "<p class='error'>⚠️ 部分文件安装失败，请重试</p>";
        }
        ?>
    </div>
</body>
</html>
