
<?php
/**
 * 修复API路由问题
 * 将PHP后端代码添加到v2.14.2的index.php中
 */

// 读取当前服务器上的index.php
$remote_url = 'http://pandian.dhmip.cn/';
$current_index = file_get_contents($remote_url);

// 检查是否已经包含API代码
if (strpos($current_index, 'API接口') !== false) {
    echo "API代码已存在\n";
    exit(0);
}

// 读取v2.8.2的PHP后端代码
$v282 = '/tmp/index_before_v3.php';
$v282_content = file_get_contents($v282);

// 提取PHP后端的API路由代码
// 从<?php开始到?>结束的部分，但需要排除HTML标签
preg_match('/<\?php(.*?)\?>(?!.*<\?php)/s', $v282_content, $matches);
$php_backend = '<?php' . $matches[1] . '?>';

// 更新数据库连接参数
$php_backend = str_replace(
    "define('DB_HOST', 'localhost');\ndefine('DB_USER', 'pandian');\ndefine('DB_PASS', 'pandian');\ndefine('DB_NAME', 'pandian');",
    "define('DB_HOST', 'localhost');\ndefine('DB_USER', 'pandian');\ndefine('DB_PASS', 'fs123456');\ndefine('DB_NAME', 'pandian');"
);

// 更新版本号
$php_backend = str_replace("define('APP_VERSION', '2.8.2');", "define('APP_VERSION', '2.14.2');", $php_backend);

// 在<head>标签前添加PHP后端代码
$fixed_content = preg_replace(
    '/<!DOCTYPE html>/',
    '<?php' . preg_replace('/<\?php|\?>/', '', $php_backend) . '?>' . "\n<!DOCTYPE html>",
    $current_index
);

// 保存修复后的文件
$temp_file = '/tmp/index_fixed_v2.14.2.php';
file_put_contents($temp_file, $fixed_content);

// 上传到服务器
$ftp = ftp_connect('211.154.19.189');
ftp_login($ftp, 'pandian', 'pandian');
ftp_pasv($ftp, true);
$fp = fopen($temp_file, 'r');
ftp_fput($ftp, 'index.php', $fp, FTP_BINARY);
fclose($fp);
ftp_close($ftp);

echo "API路由问题已修复\n";
?>
