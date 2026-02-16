<?php
/**
 * NCM 转 FLAC 上传处理脚本
 * 安全处理文件上传、转换和下载
 */

session_start();

// 错误报告设置（生产环境应关闭）
error_reporting(E_ALL);
ini_set('display_errors', 0);

// 临时文件清理函数
function cleanupFiles(array $files): void {
    foreach ($files as $file) {
        if (file_exists($file)) {
            @unlink($file);
        }
    }
}

// 发送 JSON 响应
function sendJsonResponse(bool $success, string $message, ?string $downloadUrl = null): void {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        'success' => $success,
        'message' => $message,
        'downloadUrl' => $downloadUrl
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 验证 NCM 文件魔术字
function validateNcmFile(string $filePath): bool {
    $handle = @fopen($filePath, 'rb');
    if ($handle === false) {
        return false;
    }
    
    $magic = fread($handle, 4);
    fclose($handle);
    
    // NCM 文件魔术字: CTCN
    return $magic === 'CTCN';
}

// 主处理逻辑
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    sendJsonResponse(false, '仅支持 POST 请求');
}

if (!isset($_FILES['ncm_file']) || $_FILES['ncm_file']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    sendJsonResponse(false, '文件上传失败，请重试');
}

// 配置
$uploadDir = __DIR__ . '/temp/';
$outputDir = __DIR__ . '/temp/';  // 转换输出目录
$pythonScript = __DIR__ . '/这个项目的文件/脚本/ncm_converter.py';

// 确保目录存在
if (!is_dir($uploadDir)) {
    @mkdir($uploadDir, 0755, true);
}

// 文件验证
$fileName = basename($_FILES['ncm_file']['name']);
$fileExt = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

if ($fileExt !== 'ncm') {
    http_response_code(400);
    sendJsonResponse(false, '仅支持 .ncm 格式文件');
}

// 文件大小检查（50MB 限制）
$maxSize = 50 * 1024 * 1024;
if ($_FILES['ncm_file']['size'] > $maxSize) {
    http_response_code(400);
    sendJsonResponse(false, '文件大小超过 50MB 限制');
}

// 生成唯一文件名
$uniqueId = uniqid('ncm_', true);
$tmpFilePath = $uploadDir . $uniqueId . '_' . $fileName;

// 记录需要清理的文件
$filesToCleanup = [$tmpFilePath];

// 移动上传文件
if (!move_uploaded_file($_FILES['ncm_file']['tmp_name'], $tmpFilePath)) {
    cleanupFiles($filesToCleanup);
    http_response_code(500);
    sendJsonResponse(false, '文件保存失败，请重试');
}

// 验证 NCM 文件格式
if (!validateNcmFile($tmpFilePath)) {
    cleanupFiles($filesToCleanup);
    http_response_code(400);
    sendJsonResponse(false, '无效的 NCM 文件格式');
}

// 构造输出文件路径
$baseName = pathinfo($fileName, PATHINFO_FILENAME);
$outputFilePath = $outputDir . $uniqueId . '_' . $baseName . '.flac';
$filesToCleanup[] = $outputFilePath;

// 检查 Python 脚本是否存在
if (!file_exists($pythonScript)) {
    cleanupFiles($filesToCleanup);
    error_log("Python 脚本不存在: $pythonScript");
    http_response_code(500);
    sendJsonResponse(false, '转换服务暂时不可用，请联系管理员');
}

// 执行转换命令
$escapedInput = escapeshellarg($tmpFilePath);
$escapedOutput = escapeshellarg($outputFilePath);
$command = "python3 " . escapeshellarg($pythonScript) . " $escapedInput -o $escapedOutput 2>&1";

// 执行命令并捕获输出
$output = [];
$returnVar = 0;
exec($command, $output, $returnVar);

// 记录日志
error_log("NCM 转换命令: $command");
error_log("NCM 转换结果: return_var=$returnVar, output=" . implode('\n', $output));

// 检查转换结果
if ($returnVar !== 0 || !file_exists($outputFilePath) || filesize($outputFilePath) === 0) {
    cleanupFiles($filesToCleanup);
    
    // 根据返回码提供友好的错误信息
    $errorMsg = '转换失败';
    if (strpos(implode("\n", $output), '不是有效的 NCM 文件') !== false) {
        $errorMsg = '无效的 NCM 文件，请确保文件完整且未损坏';
    } elseif (strpos(implode("\n", $output), '不是 FLAC 格式') !== false) {
        $errorMsg = '该文件不是 FLAC 格式，本工具仅支持 NCM 加密的 FLAC 文件';
    }
    
    http_response_code(422);
    sendJsonResponse(false, $errorMsg);
}

// 转换成功，设置下载
$downloadName = $baseName . '.flac';

// 检查是否是 JSON 请求（Ajax）
if (isset($_SERVER['HTTP_ACCEPT']) && 
    strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) {
    // 返回下载 URL（通过额外的参数触发下载）
    $downloadToken = md5($outputFilePath . time());
    $_SESSION['ncm_download_' . $downloadToken] = [
        'path' => $outputFilePath,
        'name' => $downloadName,
        'cleanup' => $filesToCleanup
    ];
    
    sendJsonResponse(true, '转换成功', 'download.php?token=' . $downloadToken);
} else {
    // 直接下载（兼容旧版）
    header('Content-Description: File Transfer');
    header('Content-Type: audio/flac');
    header('Content-Disposition: attachment; filename="' . $downloadName . '"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($outputFilePath));
    
    // 输出文件
    readfile($outputFilePath);
    
    // 下载后清理
    cleanupFiles($filesToCleanup);
    exit;
}
