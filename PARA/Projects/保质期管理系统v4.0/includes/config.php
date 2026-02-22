<?php
/**
 * 保质期管理系统 - v4.0.0 系统配置文件
 *
 * 包含系统的基本配置信息和常量定义
 */

// ==========================================
// 系统配置
// ==========================================

// 应用基本信息
define('APP_NAME', '保质期管理系统');
define('APP_VERSION', '4.0.0');
define('APP_DESCRIPTION', '专业的商品保质期管理系统');

// 系统路径配置
define('ROOT_DIR', dirname(__DIR__));
define('API_DIR', ROOT_DIR . '/api');
define('PAGES_DIR', ROOT_DIR . '/pages');
define('INCLUDES_DIR', ROOT_DIR . '/includes');
define('ASSETS_DIR', ROOT_DIR . '/assets');
define('TESTS_DIR', ROOT_DIR . '/tests');
define('DOCS_DIR', ROOT_DIR . '/docs');

// 系统URL配置
define('BASE_URL', 'http://pandian.dhmip.cn');
define('API_BASE', BASE_URL . '/api');
define('PAGES_BASE', BASE_URL);

// 错误报告配置
define('DEBUG_MODE', true); // 生产环境设为 false

// 安全配置
define('PASSWORD_HASH_COST', 10);
define('SESSION_TIMEOUT', 1800); // 30分钟
define('CSRF_TOKEN_EXPIRE', 3600); // 1小时

// 缓存配置
define('CACHE_ENABLED', false);
define('CACHE_TIME', 300); // 5分钟

// 数据备份配置
define('BACKUP_ENABLED', true);
define('BACKUP_PATH', ROOT_DIR . '/backup');
define('BACKUP_RETENTION', 30); // 保留30天备份

// 通知配置
define('EMAIL_ENABLED', false);
define('SMTP_HOST', 'smtp.example.com');
define('SMTP_PORT', 587);
define('SMTP_USER', '');
define('SMTP_PASS', '');
define('FROM_EMAIL', '');

// ==========================================
// 数据库配置
// ==========================================

define('DB_HOST', 'localhost');
define('DB_PORT', 3306);
define('DB_NAME', 'pandian');
define('DB_USER', 'root');
define('DB_PASS', '');

// 表前缀（可选，用于多应用共享数据库）
define('TABLE_PREFIX', 'pd_');

// 数据库连接选项
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATION', 'utf8mb4_unicode_ci');
define('DB_PERSISTENT', true);

// ==========================================
// 业务配置
// ==========================================

// 盘点配置
define('INVENTORY_DEFAULT_CATEGORY', '食品');
define('INVENTORY_MAX_ITEMS', 1000); // 单盘点最大商品数

// 保质期配置
define('EXPIRY_WARNING_DAYS', 7); // 保质期预警天数
define('EXPIRY_DANGER_DAYS', 3); // 保质期危险天数

// 二维码配置
define('QR_ENABLED', true);
define('QR_AUTO_DECODE', true);

// 文件上传配置
define('UPLOAD_ENABLED', true);
define('UPLOAD_PATH', ROOT_DIR . '/uploads');
define('UPLOAD_MAX_SIZE', 1048576); // 1MB
define('UPLOAD_ALLOWED_TYPES', ['image/jpeg', 'image/png', 'application/pdf']);

// ==========================================
// 日志配置
// ==========================================

define('LOG_ENABLED', true);
define('LOG_PATH', ROOT_DIR . '/logs');
define('LOG_LEVEL', 'DEBUG'); // DEBUG, INFO, WARNING, ERROR, CRITICAL

// 日志文件大小
define('LOG_MAX_SIZE', 10485760); // 10MB
define('LOG_BACKUP_COUNT', 5);

// ==========================================
// 错误处理配置
// ==========================================

// 显示错误（调试模式）
if (DEBUG_MODE) {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
} else {
    error_reporting(E_ERROR | E_WARNING | E_PARSE);
    ini_set('display_errors', 0);
}

// 错误日志路径
ini_set('error_log', LOG_PATH . '/php_errors.log');

// ==========================================
// 时区配置
// ==========================================

date_default_timezone_set('Asia/Shanghai');

// ==========================================
// Session配置
// ==========================================

session_set_cookie_params([
    'lifetime' => SESSION_TIMEOUT,
    'path' => '/',
    'domain' => '',
    'secure' => false,
    'httponly' => true,
    'samesite' => 'Lax'
]);

session_name('pd_session');

// ==========================================
// 自动加载和初始化
// ==========================================

// 加载函数库
require_once INCLUDES_DIR . '/functions.php';

// 数据库连接
require_once INCLUDES_DIR . '/db.php';

// 权限检查
require_once INCLUDES_DIR . '/check_auth.php';

// 安全头
header('X-Frame-Options: DENY');
header('X-Content-Type-Options: nosniff');
header('X-XSS-Protection: 1; mode=block');
header('Referrer-Policy: no-referrer-when-downgrade');
header('Content-Security-Policy: default-src \'self\'');
