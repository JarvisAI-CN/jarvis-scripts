<?php
/**
 * 下载处理脚本
 * 通过安全 token 下载转换后的文件
 */

session_start();

if (!isset($_GET['token']) || !isset($_SESSION['ncm_download_' . $_GET['token']])) {
    http_response_code(404);
    die('下载链接已过期或无效');
}

$downloadData = $_SESSION['ncm_download_' . $_GET['token']];
$filePath = $downloadData['path'];
$fileName = $downloadData['name'];

if (!file_exists($filePath)) {
    unset($_SESSION['ncm_download_' . $_GET['token']]);
    http_response_code(404);
    die('文件不存在');
}

// 发送文件
header('Content-Description: File Transfer');
header('Content-Type: audio/flac');
header('Content-Disposition: attachment; filename="' . $fileName . '"');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize($filePath));

readfile($filePath);

// 清理临时文件
if (isset($downloadData['cleanup'])) {
    foreach ($downloadData['cleanup'] as $file) {
        @unlink($file);
    }
}

// 清除 session
unset($_SESSION['ncm_download_' . $_GET['token']]);

exit;
