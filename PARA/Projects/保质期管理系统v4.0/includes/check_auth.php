<?php
/**
 * 保质期管理系统 - v4.0.0 权限检查和会话管理
 */

// 防止直接访问
if (!defined('APP_NAME')) {
    header('Location: /');
    exit;
}

/**
 * 用户认证检查
 * @param string $requiredRole 要求的角色 (user, admin)
 * @return bool 用户是否已认证
 */
function checkAuth($requiredRole = 'user')
{
    // 检查会话是否已初始化
    if (session_status() == PHP_SESSION_NONE) {
        session_start();
    }
    
    // 检查用户是否已登录
    if (!isset($_SESSION['user_id']) || !isset($_SESSION['username'])) {
        if (DEBUG_MODE) {
            logger('debug', '用户未登录');
        }
        return false;
    }
    
    // 检查会话是否过期
    if (checkSessionExpiry()) {
        if (DEBUG_MODE) {
            logger('debug', '会话已过期');
        }
        return false;
    }
    
    // 更新会话时间戳
    updateSessionTimestamp();
    
    // 检查用户角色权限
    $hasPermission = checkUserPermission($requiredRole);
    
    if (!DEBUG_MODE && !$hasPermission) {
        logger('warning', '用户权限不足', [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username'],
            'required_role' => $requiredRole,
            'actual_role' => $_SESSION['role'] ?? 'unknown'
        ]);
    }
    
    return $hasPermission;
}

/**
 * 会话过期检查
 * @return bool 会话是否已过期
 */
function checkSessionExpiry()
{
    if (!isset($_SESSION['last_activity'])) {
        $_SESSION['last_activity'] = time();
        return false;
    }
    
    $elapsed = time() - $_SESSION['last_activity'];
    
    if ($elapsed > SESSION_TIMEOUT) {
        logger('info', '会话过期', [
            'user_id' => $_SESSION['user_id'] ?? 'unknown',
            'username' => $_SESSION['username'] ?? 'unknown',
            'elapsed' => $elapsed,
            'timeout' => SESSION_TIMEOUT
        ]);
        
        logoutUser();
        return true;
    }
    
    return false;
}

/**
 * 更新会话时间戳
 * @return void
 */
function updateSessionTimestamp()
{
    $_SESSION['last_activity'] = time();
}

/**
 * 检查用户权限
 * @param string $requiredRole 要求的角色
 * @return bool 用户是否有权限
 */
function checkUserPermission($requiredRole)
{
    $userRole = $_SESSION['role'] ?? 'user';
    
    $roleHierarchy = [
        'user' => 1,
        'admin' => 2
    ];
    
    $requiredLevel = $roleHierarchy[$requiredRole] ?? 1;
    $userLevel = $roleHierarchy[$userRole] ?? 1;
    
    return $userLevel >= $requiredLevel;
}

/**
 * 用户登录
 * @param string $username 用户名
 * @param string $password 密码
 * @return bool|array 登录结果
 */
function loginUser($username, $password)
{
    // 清理输入
    $username = trim($username);
    $password = trim($password);
    
    // 输入验证
    $usernameResult = validateInput($username, 'username');
    if (!$usernameResult['valid']) {
        return ['success' => false, 'message' => $usernameResult['message']];
    }
    
    $passwordResult = validateInput($password, 'password', ['minLength' => 6]);
    if (!$passwordResult['valid']) {
        return ['success' => false, 'message' => $passwordResult['message']];
    }
    
    try {
        $db = getDB();
        
        // 查询用户
        $user = $db->fetchOne("
            SELECT * FROM " . TABLE_PREFIX . "users 
            WHERE username = ? AND status = 'active'
        ", [$username]);
        
        if (!$user) {
            logger('warning', '登录失败: 用户名不存在或用户已被禁用', [
                'username' => $username
            ]);
            return ['success' => false, 'message' => '用户名或密码错误'];
        }
        
        // 验证密码
        if (!password_verify($password, $user['password'])) {
            logger('warning', '登录失败: 密码错误', [
                'username' => $username
            ]);
            return ['success' => false, 'message' => '用户名或密码错误'];
        }
        
        // 初始化会话
        if (session_status() == PHP_SESSION_NONE) {
            session_start();
        }
        
        // 生成新的会话ID以防止会话固定攻击
        session_regenerate_id(true);
        
        // 设置会话变量
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        $_SESSION['realname'] = $user['realname'] ?? $user['username'];
        $_SESSION['last_activity'] = time();
        $_SESSION['login_time'] = time();
        
        // 记录登录日志
        logger('info', '用户登录成功', [
            'user_id' => $user['id'],
            'username' => $user['username'],
            'role' => $user['role'],
            'ip_address' => getClientIP(),
            'user_agent' => getUserAgent()
        ]);
        
        // 更新用户登录信息
        $db->update(TABLE_PREFIX . 'users', [
            'last_login' => date('Y-m-d H:i:s'),
            'login_count' => $user['login_count'] + 1
        ], 'id = ?', [$user['id']]);
        
        return ['success' => true, 'user' => $user];
        
    } catch (Exception $e) {
        logger('error', '登录失败: ' . $e->getMessage(), [
            'username' => $username,
            'error' => $e->getMessage()
        ]);
        return ['success' => false, 'message' => '登录过程中发生错误'];
    }
}

/**
 * 用户登出
 * @return void
 */
function logoutUser()
{
    if (session_status() == PHP_SESSION_NONE) {
        session_start();
    }
    
    if (isset($_SESSION['user_id']) && isset($_SESSION['username'])) {
        logger('info', '用户登出', [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username'],
            'ip_address' => getClientIP(),
            'user_agent' => getUserAgent()
        ]);
    }
    
    // 清除会话变量
    $_SESSION = [];
    
    // 清除会话cookie
    if (ini_get('session.use_cookies')) {
        $params = session_get_cookie_params();
        setcookie(session_name(), '', time() - 42000,
            $params['path'], $params['domain'],
            $params['secure'], $params['httponly']
        );
    }
    
    // 销毁会话
    session_destroy();
}

/**
 * 获取客户端IP地址
 * @return string IP地址
 */
function getClientIP()
{
    $ipaddress = 'unknown';
    
    if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ipaddress = $_SERVER['HTTP_X_FORWARDED_FOR'];
    } elseif (isset($_SERVER['HTTP_X_REAL_IP'])) {
        $ipaddress = $_SERVER['HTTP_X_REAL_IP'];
    } elseif (isset($_SERVER['HTTP_CLIENT_IP'])) {
        $ipaddress = $_SERVER['HTTP_CLIENT_IP'];
    } elseif (isset($_SERVER['REMOTE_ADDR'])) {
        $ipaddress = $_SERVER['REMOTE_ADDR'];
    }
    
    // 如果有多个IP地址，取第一个
    $ips = explode(',', $ipaddress);
    $ipaddress = trim($ips[0]);
    
    return $ipaddress;
}

/**
 * 获取用户代理信息
 * @return string 用户代理字符串
 */
function getUserAgent()
{
    return $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';
}

/**
 * 强制登录检查（用于API接口）
 * @param string $requiredRole 要求的角色
 * @return void
 */
function requireAuth($requiredRole = 'user')
{
    if (!checkAuth($requiredRole)) {
        $response = [
            'success' => false,
            'message' => '请先登录'
        ];
        
        // 检查请求类型
        $isAjax = isset($_SERVER['HTTP_X_REQUESTED_WITH']) && 
                  strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) == 'xmlhttprequest';
        
        if ($isAjax) {
            // 如果是API请求，返回JSON响应
            header('Content-Type: application/json');
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        } else {
            // 如果是页面请求，重定向到登录页面
            $redirectUrl = BASE_URL . '/';
            header('Location: ' . $redirectUrl);
            exit;
        }
    }
}

/**
 * 检查用户是否是管理员
 * @return bool 用户是否是管理员
 */
function isAdmin()
{
    if (!checkAuth()) {
        return false;
    }
    
    return $_SESSION['role'] === 'admin';
}

/**
 * 检查用户是否是普通用户
 * @return bool 用户是否是普通用户
 */
function isUser()
{
    if (!checkAuth()) {
        return false;
    }
    
    return $_SESSION['role'] === 'user' || isAdmin();
}

/**
 * 获取当前用户信息
 * @return array 用户信息
 */
function getCurrentUser()
{
    if (!checkAuth()) {
        return [];
    }
    
    return [
        'id' => $_SESSION['user_id'],
        'username' => $_SESSION['username'],
        'realname' => $_SESSION['realname'],
        'role' => $_SESSION['role']
    ];
}

/**
 * 获取用户角色
 * @return string 用户角色
 */
function getUserRole()
{
    if (!checkAuth()) {
        return 'guest';
    }
    
    return $_SESSION['role'];
}

/**
 * 更新用户信息
 * @param array $userData 新的用户数据
 * @return bool 更新是否成功
 */
function updateUser($userData)
{
    if (!checkAuth()) {
        return false;
    }
    
    try {
        $db = getDB();
        $userId = $_SESSION['user_id'];
        
        $db->update(TABLE_PREFIX . 'users', $userData, 'id = ?', [$userId]);
        
        // 更新会话中的用户信息
        if (isset($userData['realname'])) {
            $_SESSION['realname'] = $userData['realname'];
        }
        
        logger('info', '用户信息更新成功', [
            'user_id' => $userId,
            'username' => $_SESSION['username'],
            'updated_fields' => array_keys($userData)
        ]);
        
        return true;
    } catch (Exception $e) {
        logger('error', '用户信息更新失败: ' . $e->getMessage());
        return false;
    }
}

/**
 * 密码重置函数
 * @param string $oldPassword 旧密码
 * @param string $newPassword 新密码
 * @return array 操作结果
 */
function changePassword($oldPassword, $newPassword)
{
    if (!checkAuth()) {
        return ['success' => false, 'message' => '请先登录'];
    }
    
    try {
        $db = getDB();
        $userId = $_SESSION['user_id'];
        
        // 获取当前用户信息
        $user = $db->fetchOne("
            SELECT * FROM " . TABLE_PREFIX . "users 
            WHERE id = ?
        ", [$userId]);
        
        // 验证旧密码
        if (!password_verify($oldPassword, $user['password'])) {
            logger('warning', '密码重置失败: 旧密码不正确', [
                'user_id' => $userId,
                'username' => $_SESSION['username']
            ]);
            return ['success' => false, 'message' => '旧密码不正确'];
        }
        
        // 验证新密码
        $passwordResult = validateInput($newPassword, 'password', ['minLength' => 6]);
        if (!$passwordResult['valid']) {
            return ['success' => false, 'message' => $passwordResult['message']];
        }
        
        // 哈希新密码
        $hashedPassword = password_hash($newPassword, PASSWORD_DEFAULT);
        
        // 更新密码
        $db->update(TABLE_PREFIX . 'users', [
            'password' => $hashedPassword
        ], 'id = ?', [$userId]);
        
        logger('info', '密码重置成功', [
            'user_id' => $userId,
            'username' => $_SESSION['username']
        ]);
        
        return ['success' => true, 'message' => '密码更新成功'];
        
    } catch (Exception $e) {
        logger('error', '密码重置失败: ' . $e->getMessage(), [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username']
        ]);
        return ['success' => false, 'message' => '密码更新过程中发生错误'];
    }
}

/**
 * 用户信息验证函数
 * @param array $userData 用户数据
 * @return array 验证结果
 */
function validateUserInfo($userData)
{
    $errors = [];
    
    if (isset($userData['email'])) {
        $emailResult = validateInput($userData['email'], 'email');
        if (!$emailResult['valid']) {
            $errors['email'] = $emailResult['message'];
        }
    }
    
    if (isset($userData['realname'])) {
        $realnameResult = validateInput($userData['realname'], 'username', ['minLength' => 2, 'maxLength' => 20]);
        if (!$realnameResult['valid']) {
            $errors['realname'] = $realnameResult['message'];
        }
    }
    
    if (isset($userData['phone'])) {
        $phoneResult = validateInput($userData['phone'], 'phone');
        if (!$phoneResult['valid']) {
            $errors['phone'] = $phoneResult['message'];
        }
    }
    
    return $errors;
}

/**
 * 获取用户登录历史
 * @param int $userId 用户ID
 * @param int $limit 记录数限制
 * @return array 登录历史
 */
function getUserLoginHistory($userId, $limit = 50)
{
    try {
        $db = getDB();
        
        $logs = $db->fetchAll("
            SELECT * FROM " . TABLE_PREFIX . "logs 
            WHERE user_id = ? AND action IN ('登录', '登出') 
            ORDER BY created_at DESC
            LIMIT ?
        ", [$userId, $limit]);
        
        return $logs;
    } catch (Exception $e) {
        logger('error', '获取用户登录历史失败: ' . $e->getMessage(), [
            'user_id' => $userId
        ]);
        return [];
    }
}

/**
 * 安全的用户操作记录
 * @param string $action 操作类型
 * @param array $details 操作详情
 * @return bool 是否记录成功
 */
function addUserActionLog($action, $details = [])
{
    if (!checkAuth()) {
        return false;
    }
    
    try {
        $db = getDB();
        
        $logData = [
            'user_id' => $_SESSION['user_id'],
            'action' => $action,
            'details' => json_encode($details, JSON_UNESCAPED_UNICODE),
            'ip_address' => getClientIP(),
            'user_agent' => getUserAgent(),
            'created_at' => date('Y-m-d H:i:s')
        ];
        
        $db->insert(TABLE_PREFIX . 'logs', $logData);
        
        logger('info', '用户操作记录', [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username'],
            'action' => $action,
            'details' => $details
        ]);
        
        return true;
    } catch (Exception $e) {
        logger('error', '操作记录失败: ' . $e->getMessage(), [
            'user_id' => $_SESSION['user_id'],
            'username' => $_SESSION['username'],
            'action' => $action,
            'error' => $e->getMessage()
        ]);
        return false;
    }
}

/**
 * 用户会话管理
 * @return bool 是否需要更新会话
 */
function manageUserSession()
{
    // 检查会话是否已初始化
    if (session_status() == PHP_SESSION_NONE) {
        session_start();
    }
    
    // 检查会话是否过期
    if (checkSessionExpiry()) {
        return false;
    }
    
    // 更新会话活动时间
    updateSessionTimestamp();
    
    return true;
}
