<?php
/**
 * 保质期管理系统 - v4.0.0 登出API
 * 用户会话管理接口
 */

require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/check_auth.php';

// 设置CORS头部
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// 处理OPTIONS请求
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 只接受GET请求
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => '方法不允许',
        'error' => '只接受GET请求'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 检查是否已登录
if (!checkAuth()) {
    // 即使未登录，也返回成功响应（避免错误显示）
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => '已处于登出状态'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 清除记住我的token
if (isset($_COOKIE['remember_token'])) {
    try {
        $db = getDB();
        $db->update(TABLE_PREFIX . 'users', [
            'remember_token' => null,
            'remember_token_expires' => null
        ], 'id = ?', [$_SESSION['user_id']]);
    } catch (Exception $e) {
        logger('error', '清除记住我token失败: ' . $e->getMessage());
    }
    
    // 删除cookie
    setcookie('remember_token', '', time() - 3600, '/', '', false, true);
}

// 记录用户登出日志
logger('info', '用户登出', [
    'user_id' => $_SESSION['user_id'],
    'username' => $_SESSION['username'],
    'role' => $_SESSION['role'],
    'ip_address' => getClientIP(),
    'user_agent' => getUserAgent()
]);

// 执行登出操作
logoutUser();

// 响应成功
http_response_code(200);
echo json_encode([
    'success' => true,
    'message' => '登出成功'
], JSON_UNESCAPED_UNICODE);
exit;
