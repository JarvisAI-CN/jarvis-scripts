<?php
/**
 * ========================================
 * 保质期管理系统 - 数据库连接文件
 * 文件名: db.php
 * ========================================
 */

// 检查是否安装
if (!file_exists(__DIR__ . '/config.php')) {
    if (basename($_SERVER['PHP_SELF']) !== 'install.php') {
        header("Location: install.php");
        exit;
    }
} else {
    require_once __DIR__ . '/config.php';
}

// 错误报告设置
error_reporting(E_ALL);
ini_set('display_errors', 1);

/**
 * 获取数据库连接（单例模式）
 */
function getDBConnection() {
    static $conn = null;
    if ($conn !== null) return $conn;
    
    if (!defined('DB_HOST')) return false;

    try {
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        if ($conn->connect_error) return false;
        $conn->set_charset(DB_CHARSET);
        return $conn;
    } catch (Exception $e) {
        return false;
    }
}

function escapeValue($conn, $value) {
    return $conn->real_escape_string($value);
}

function jsonResponse($data, $statusCode = 200) {
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function logError($message, $context = null) {
    $logMessage = date('[Y-m-d H:i:s] ') . $message;
    if ($context !== null) {
        $logMessage .= ' | Context: ' . json_encode($context, JSON_UNESCAPED_UNICODE);
    }
    error_log($logMessage);
}
