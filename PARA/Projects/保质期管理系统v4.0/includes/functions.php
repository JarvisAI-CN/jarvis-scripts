<?php
/**
 * 保质期管理系统 - v4.0.0 工具函数库
 * 包含系统通用函数、验证函数、格式化函数等
 */

// 防止直接访问
if (!defined('APP_NAME')) {
    header('Location: /');
    exit;
}

/**
 * 日志记录函数
 * @param string $level 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
 * @param string $message 日志内容
 * @param array $context 上下文信息
 * @return bool
 */
function logger($level, $message, $context = [])
{
    if (!LOG_ENABLED) {
        return false;
    }

    $level = strtoupper($level);
    $validLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'];
    
    if (!in_array($level, $validLevels)) {
        $level = 'INFO';
    }

    $timestamp = date('Y-m-d H:i:s');
    $logEntry = sprintf(
        "[%s] %-8s %s",
        $timestamp,
        $level,
        $message
    );

    if (!empty($context)) {
        $logEntry .= ' | ' . json_encode($context);
    }

    $logEntry .= "\n";

    $logPath = LOG_PATH . '/' . date('Y-m-d') . '.log';

    try {
        // 确保日志目录存在
        if (!is_dir(dirname($logPath))) {
            mkdir(dirname($logPath), 0755, true);
        }

        // 写入日志文件
        $result = file_put_contents($logPath, $logEntry, FILE_APPEND | LOCK_EX);
        
        if ($result === false) {
            return false;
        }

        // 检查文件大小并备份
        if (filesize($logPath) > LOG_MAX_SIZE) {
            backupLogFile($logPath);
        }

        return true;
    } catch (Exception $e) {
        error_log('日志写入失败: ' . $e->getMessage());
        return false;
    }
}

/**
 * 备份日志文件
 * @param string $logPath 日志文件路径
 */
function backupLogFile($logPath)
{
    $dir = dirname($logPath);
    $fileName = basename($logPath, '.log');

    for ($i = LOG_BACKUP_COUNT - 1; $i > 0; $i--) {
        $oldFile = $dir . '/' . $fileName . '.' . $i . '.log';
        $newFile = $dir . '/' . $fileName . '.' . ($i + 1) . '.log';
        
        if (file_exists($oldFile)) {
            if ($i === LOG_BACKUP_COUNT - 1) {
                unlink($oldFile);
            } else {
                rename($oldFile, $newFile);
            }
        }
    }

    if (file_exists($logPath)) {
        rename($logPath, $dir . '/' . $fileName . '.1.log');
    }
}

/**
 * 响应JSON数据
 * @param array $data 响应数据
 * @param int $statusCode HTTP状态码
 * @return void
 */
function jsonResponse($data, $statusCode = 200)
{
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

/**
 * 成功响应
 * @param string $message 成功信息
 * @param array $data 附加数据
 * @return void
 */
function successResponse($message, $data = [])
{
    $response = [
        'success' => true,
        'message' => $message
    ];
    
    if (!empty($data)) {
        $response['data'] = $data;
    }
    
    jsonResponse($response, 200);
}

/**
 * 错误响应
 * @param string $message 错误信息
 * @param array $data 附加数据
 * @param int $statusCode HTTP状态码
 * @return void
 */
function errorResponse($message, $data = [], $statusCode = 400)
{
    $response = [
        'success' => false,
        'message' => $message
    ];
    
    if (!empty($data)) {
        $response['data'] = $data;
    }
    
    jsonResponse($response, $statusCode);
}

/**
 * 重定向函数
 * @param string $url 重定向地址
 * @param int $statusCode 状态码 (301或302)
 * @return void
 */
function redirect($url, $statusCode = 302)
{
    header('Location: ' . $url, true, $statusCode);
    exit;
}

/**
 * 输入验证函数
 * @param string $value 要验证的值
 * @param string $type 验证类型 (email, phone, username, password等)
 * @param array $options 验证选项
 * @return bool|array 验证结果
 */
function validateInput($value, $type, $options = [])
{
    $validTypes = ['email', 'phone', 'username', 'password', 'sku', 'date'];
    
    if (!in_array($type, $validTypes)) {
        return true; // 不支持的验证类型，默认通过
    }

    $result = ['valid' => true, 'message' => ''];

    switch ($type) {
        case 'email':
            $result = validateEmail($value);
            break;
            
        case 'phone':
            $result = validatePhone($value);
            break;
            
        case 'username':
            $result = validateUsername($value, $options);
            break;
            
        case 'password':
            $result = validatePassword($value, $options);
            break;
            
        case 'sku':
            $result = validateSKU($value, $options);
            break;
            
        case 'date':
            $result = validateDate($value, $options);
            break;
    }

    return $result;
}

function validateEmail($email)
{
    $pattern = '/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/';
    
    if (!preg_match($pattern, $email)) {
        return ['valid' => false, 'message' => '邮箱格式不正确'];
    }
    
    return ['valid' => true, 'message' => ''];
}

function validatePhone($phone)
{
    $pattern = '/^1[3-9]\d{9}$/';
    
    if (!preg_match($pattern, $phone)) {
        return ['valid' => false, 'message' => '手机号码格式不正确'];
    }
    
    return ['valid' => true, 'message' => ''];
}

function validateUsername($username, $options = [])
{
    $minLength = $options['minLength'] ?? 3;
    $maxLength = $options['maxLength'] ?? 20;
    
    if (mb_strlen($username) < $minLength || mb_strlen($username) > $maxLength) {
        return ['valid' => false, 'message' => '用户名长度应在' . $minLength . '-' . $maxLength . '个字符之间'];
    }
    
    $pattern = '/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/';
    if (!preg_match($pattern, $username)) {
        return ['valid' => false, 'message' => '用户名只能包含字母、数字、下划线和中文'];
    }
    
    return ['valid' => true, 'message' => ''];
}

function validatePassword($password, $options = [])
{
    $minLength = $options['minLength'] ?? 6;
    $requireComplexity = $options['requireComplexity'] ?? true;
    
    if (mb_strlen($password) < $minLength) {
        return ['valid' => false, 'message' => '密码长度至少需要' . $minLength . '个字符'];
    }
    
    if ($requireComplexity) {
        $pattern = '/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/';
        
        if (!preg_match($pattern, $password)) {
            return ['valid' => false, 'message' => '密码应包含大小写字母和数字'];
        }
    }
    
    return ['valid' => true, 'message' => ''];
}

function validateSKU($sku, $options = [])
{
    $minLength = $options['minLength'] ?? 4;
    $maxLength = $options['maxLength'] ?? 50;
    
    if (mb_strlen($sku) < $minLength || mb_strlen($sku) > $maxLength) {
        return ['valid' => false, 'message' => 'SKU长度应在' . $minLength . '-' . $maxLength . '个字符之间'];
    }
    
    $pattern = '/^[a-zA-Z0-9_-]+$/';
    if (!preg_match($pattern, $sku)) {
        return ['valid' => false, 'message' => 'SKU只能包含字母、数字、下划线和短横线'];
    }
    
    return ['valid' => true, 'message' => ''];
}

function validateDate($date, $options = [])
{
    $format = $options['format'] ?? 'Y-m-d';
    
    $dateObj = DateTime::createFromFormat($format, $date);
    
    if (!$dateObj) {
        return ['valid' => false, 'message' => '日期格式不正确，应为' . $format];
    }
    
    return ['valid' => true, 'message' => ''];
}

/**
 * 格式化日期
 * @param string $date 日期字符串
 * @param string $format 输出格式
 * @return string
 */
function formatDate($date, $format = 'Y年m月d日')
{
    if (empty($date)) {
        return '';
    }
    
    try {
        $dateObj = new DateTime($date);
        return $dateObj->format($format);
    } catch (Exception $e) {
        logger('error', '日期格式化失败: ' . $e->getMessage());
        return $date;
    }
}

/**
 * 格式化时间
 * @param string $time 时间字符串
 * @param string $format 输出格式
 * @return string
 */
function formatTime($time, $format = 'H:i:s')
{
    if (empty($time)) {
        return '';
    }
    
    try {
        $timeObj = new DateTime($time);
        return $timeObj->format($format);
    } catch (Exception $e) {
        logger('error', '时间格式化失败: ' . $e->getMessage());
        return $time;
    }
}

/**
 * 格式化文件大小
 * @param int $bytes 字节数
 * @return string
 */
function formatFileSize($bytes)
{
    $units = ['B', 'KB', 'MB', 'GB', 'TB'];
    
    for ($i = 0; $bytes > 1024 && $i < count($units) - 1; $i++) {
        $bytes /= 1024;
    }
    
    return round($bytes, 2) . ' ' . $units[$i];
}

/**
 * 生成随机字符串
 * @param int $length 字符串长度
 * @param string $type 字符串类型 (alpha, numeric, alphanumeric, hex, md5)
 * @return string
 */
function generateRandomString($length = 8, $type = 'alphanumeric')
{
    $chars = '';
    
    switch ($type) {
        case 'alpha':
            $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
            break;
        case 'numeric':
            $chars = '0123456789';
            break;
        case 'alphanumeric':
            $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            break;
        case 'hex':
            $chars = '0123456789abcdef';
            break;
        case 'md5':
            return md5(uniqid(rand(), true));
        default:
            $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    }
    
    $string = '';
    
    for ($i = 0; $i < $length; $i++) {
        $string .= $chars[rand(0, strlen($chars) - 1)];
    }
    
    return $string;
}

/**
 * 验证密码强度
 * @param string $password 密码
 * @return int 强度等级 (0-4)
 */
function checkPasswordStrength($password)
{
    $strength = 0;
    
    if (mb_strlen($password) >= 8) {
        $strength++;
    }
    
    if (preg_match('/[a-z]/', $password) && preg_match('/[A-Z]/', $password)) {
        $strength++;
    }
    
    if (preg_match('/\d/', $password)) {
        $strength++;
    }
    
    if (preg_match('/[^a-zA-Z\d]/', $password)) {
        $strength++;
    }
    
    return $strength;
}

/**
 * 安全转义输出
 * @param string $string 原始字符串
 * @return string 转义后的字符串
 */
function htmlEscape($string)
{
    return htmlspecialchars($string, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

/**
 * 清理输入数据
 * @param mixed $data 要清理的数据
 * @return mixed 清理后的数据
 */
function sanitizeInput($data)
{
    if (is_array($data)) {
        foreach ($data as $key => $value) {
            $data[$key] = sanitizeInput($value);
        }
        return $data;
    }
    
    // 去除多余空格
    $data = trim($data);
    
    // 去除换行符和回车
    $data = str_replace(["\r\n", "\r", "\n"], '', $data);
    
    return $data;
}

/**
 * 安全的文件操作函数
 * @param string $path 文件路径
 * @param string $mode 操作模式 (read, write, delete等)
 * @param mixed $content 写入内容
 * @return bool|string 操作结果
 */
function safeFileOperation($path, $mode, $content = null)
{
    try {
        // 防止路径遍历
        $realPath = realpath($path);
        if (false === $realPath) {
            return false;
        }
        
        // 验证路径是否在允许的目录内
        $allowedDirs = [
            UPLOAD_PATH,
            LOG_PATH,
            BACKUP_PATH
        ];
        
        $isAllowed = false;
        foreach ($allowedDirs as $allowedDir) {
            if (strpos($realPath, $allowedDir) === 0) {
                $isAllowed = true;
                break;
            }
        }
        
        if (!$isAllowed) {
            logger('warning', '文件操作路径不在允许目录内: ' . $path);
            return false;
        }
        
        switch ($mode) {
            case 'read':
                if (is_readable($realPath)) {
                    return file_get_contents($realPath);
                }
                return false;
                
            case 'write':
                if (is_writable(dirname($realPath))) {
                    return file_put_contents($realPath, $content, LOCK_EX);
                }
                return false;
                
            case 'delete':
                if (is_writable($realPath)) {
                    return unlink($realPath);
                }
                return false;
                
            default:
                return false;
        }
    } catch (Exception $e) {
        logger('error', '文件操作失败: ' . $e->getMessage());
        return false;
    }
}

/**
 * 生成CSRF令牌
 * @return string
 */
function generateCSRFToken()
{
    if (!isset($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = bin2hex(random_bytes(32));
        $_SESSION['csrf_token_time'] = time();
    }
    
    return $_SESSION['csrf_token'];
}

/**
 * 验证CSRF令牌
 * @param string $token 要验证的令牌
 * @return bool
 */
function validateCSRFToken($token)
{
    if (!isset($_SESSION['csrf_token']) || !isset($_SESSION['csrf_token_time'])) {
        return false;
    }
    
    if (time() - $_SESSION['csrf_token_time'] > CSRF_TOKEN_EXPIRE) {
        unset($_SESSION['csrf_token']);
        unset($_SESSION['csrf_token_time']);
        return false;
    }
    
    return hash_equals($_SESSION['csrf_token'], $token);
}

/**
 * 计算保质期状态
 * @param string $expiryDate 过期日期
 * @return string 状态 (safe, warning, danger, expired)
 */
function calculateExpiryStatus($expiryDate)
{
    $today = new DateTime();
    $expiry = new DateTime($expiryDate);
    
    $interval = $today->diff($expiry);
    
    if ($interval->invert === 1) {
        return 'expired'; // 已过期
    }
    
    $days = $interval->days;
    
    if ($days <= EXPIRY_DANGER_DAYS) {
        return 'danger'; // 危险
    } elseif ($days <= EXPIRY_WARNING_DAYS) {
        return 'warning'; // 警告
    } else {
        return 'safe'; // 安全
    }
}

/**
 * 计算剩余天数
 * @param string $expiryDate 过期日期
 * @return int 剩余天数
 */
function calculateRemainingDays($expiryDate)
{
    $today = new DateTime();
    $expiry = new DateTime($expiryDate);
    
    $interval = $today->diff($expiry);
    
    return $interval->invert === 1 ? -$interval->days : $interval->days;
}

/**
 * 格式化剩余天数显示
 * @param int $days 剩余天数
 * @return string
 */
function formatRemainingDays($days)
{
    if ($days < 0) {
        return '已过期' . abs($days) . '天';
    } elseif ($days === 0) {
        return '今天过期';
    } elseif ($days === 1) {
        return '明天过期';
    } elseif ($days <= 7) {
        return $days . '天后过期';
    } elseif ($days <= 30) {
        return '约' . round($days / 7) . '周后过期';
    } else {
        return '约' . round($days / 30) . '月后过期';
    }
}

/**
 * 获取保质期状态对应的CSS类
 * @param string $status 状态
 * @return string CSS类名
 */
function getExpiryStatusClass($status)
{
    $statusMap = [
        'safe' => 'text-success',
        'warning' => 'text-warning',
        'danger' => 'text-danger',
        'expired' => 'text-danger font-weight-bold'
    ];
    
    return $statusMap[$status] ?? 'text-muted';
}

/**
 * 计算数据摘要
 * @param string $data 数据
 * @param string $algorithm 算法
 * @return string 摘要结果
 */
function computeHash($data, $algorithm = 'sha256')
{
    if (!in_array($algorithm, hash_algos())) {
        $algorithm = 'sha256';
    }
    
    return hash($algorithm, $data);
}

/**
 * 数组深度比较
 * @param array $arr1 第一个数组
 * @param array $arr2 第二个数组
 * @return bool 是否相等
 */
function arrayDeepCompare($arr1, $arr2)
{
    if (count($arr1) !== count($arr2)) {
        return false;
    }
    
    foreach ($arr1 as $key => $value) {
        if (!array_key_exists($key, $arr2)) {
            return false;
        }
        
        if (is_array($value) && is_array($arr2[$key])) {
            if (!arrayDeepCompare($value, $arr2[$key])) {
                return false;
            }
        } elseif ($value !== $arr2[$key]) {
            return false;
        }
    }
    
    return true;
}
