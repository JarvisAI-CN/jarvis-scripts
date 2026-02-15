<?php
/**
 * ========================================
 * 保质期管理系统 - 数据库连接文件
 * 文件名: db.php
 * ========================================
 */

// 数据库配置
define('DB_HOST', 'localhost');        // 数据库主机
define('DB_USER', 'expiry_user');      // 数据库用户名
define('DB_PASS', 'Expiry@2026System!'); // 数据库密码
define('DB_NAME', 'expiry_system');    // 数据库名称
define('DB_CHARSET', 'utf8mb4');       // 字符集

// 错误报告设置（生产环境建议关闭）
error_reporting(E_ALL);
ini_set('display_errors', 1);

/**
 * 获取数据库连接（单例模式）
 * @return mysqli|false 返回数据库连接对象，失败返回 false
 */
function getDBConnection() {
    static $conn = null;
    
    // 如果连接已存在，直接返回
    if ($conn !== null) {
        return $conn;
    }
    
    try {
        $conn = new mysqli(
            DB_HOST,
            DB_USER,
            DB_PASS,
            DB_NAME
        );
        
        // 检查连接是否成功
        if ($conn->connect_error) {
            error_log("数据库连接失败: " . $conn->connect_error);
            return false;
        }
        
        // 设置字符集
        $conn->set_charset(DB_CHARSET);
        
        return $conn;
        
    } catch (Exception $e) {
        error_log("数据库连接异常: " . $e->getMessage());
        return false;
    }
}

/**
 * 安全的 SQL 转义
 * @param mysqli $conn 数据库连接
 * @param string $value 需要转义的值
 * @return string 转义后的值
 */
function escapeValue($conn, $value) {
    return $conn->real_escape_string($value);
}

/**
 * 输出 JSON 响应
 * @param array $data 响应数据
 * @param int $statusCode HTTP 状态码
 */
function jsonResponse($data, $statusCode = 200) {
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

/**
 * 记录错误日志
 * @param string $message 错误信息
 * @param mixed $context 上下文数据
 */
function logError($message, $context = null) {
    $logMessage = date('[Y-m-d H:i:s] ') . $message;
    if ($context !== null) {
        $logMessage .= ' | Context: ' . json_encode($context, JSON_UNESCAPED_UNICODE);
    }
    error_log($logMessage);
    
    // 可选：写入文件日志
    // file_put_contents(__DIR__ . '/error.log', $logMessage . "\n", FILE_APPEND);
}
