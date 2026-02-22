<?php
/**
 * 保质期管理系统 - v4.0.0 登录API
 * 用户身份验证接口
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 设置CORS头部
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// 处理OPTIONS请求
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 只接受POST请求
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        'success' => false,
        'message' => '方法不允许',
        'error' => '只接受POST请求'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 获取请求数据
$data = json_decode(file_get_contents('php://input'), true);

// 验证请求参数
$requiredFields = ['username', 'password'];
foreach ($requiredFields as $field) {
    if (!isset($data[$field]) || empty($data[$field])) {
        http_response_code(400);
        echo json_encode([
            'success' => false,
            'message' => '缺少必填字段',
            'error' => "字段 '$field' 不能为空"
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
}

$username = trim($data['username']);
$password = trim($data['password']);
$remember = isset($data['remember']) && $data['remember'];

// 验证输入格式
$usernameResult = validateInput($username, 'username');
if (!$usernameResult['valid']) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'message' => $usernameResult['message'],
        'error' => '用户名格式不正确'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

$passwordResult = validateInput($password, 'password', ['minLength' => 6]);
if (!$passwordResult['valid']) {
    http_response_code(400);
    echo json_encode([
        'success' => false,
        'message' => $passwordResult['message'],
        'error' => '密码格式不正确'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 尝试登录
$loginResult = loginUser($username, $password);

if ($loginResult['success']) {
    // 登录成功
    $user = $loginResult['user'];
    
    // 如果选择记住我，设置长期cookie
    if ($remember) {
        $rememberToken = generateRandomString(32);
        $expires = time() + 60 * 60 * 24 * 7; // 7天
        
        // 保存记住我的token到数据库
        $db = getDB();
        $db->update(TABLE_PREFIX . 'users', [
            'remember_token' => $rememberToken,
            'remember_token_expires' => date('Y-m-d H:i:s', $expires)
        ], 'id = ?', [$user['id']]);
        
        // 设置cookie
        setcookie('remember_token', $rememberToken, $expires, '/', '', false, true);
    }
    
    logger('info', '用户登录成功', [
        'user_id' => $user['id'],
        'username' => $user['username'],
        'role' => $user['role'],
        'remember' => $remember,
        'ip_address' => getClientIP(),
        'user_agent' => getUserAgent()
    ]);
    
    http_response_code(200);
    echo json_encode([
        'success' => true,
        'message' => '登录成功',
        'user' => [
            'id' => $user['id'],
            'username' => $user['username'],
            'realname' => $user['realname'] ?? $user['username'],
            'role' => $user['role']
        ]
    ], JSON_UNESCAPED_UNICODE);
} else {
    // 登录失败
    logger('warning', '用户登录失败', [
        'username' => $username,
        'error' => $loginResult['message'],
        'ip_address' => getClientIP(),
        'user_agent' => getUserAgent()
    ]);
    
    http_response_code(401);
    echo json_encode([
        'success' => false,
        'message' => $loginResult['message'],
        'error' => '用户名或密码错误'
    ], JSON_UNESCAPED_UNICODE);
}

// 安全地退出脚本
exit;
