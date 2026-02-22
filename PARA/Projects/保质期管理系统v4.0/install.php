<?php
/**
 * 保质期管理系统 - v4.0.0 安装程序
 * 一键安装和初始化系统
 */

// 防止重复安装
if (file_exists(__DIR__ . '/.installed')) {
    die('系统已经安装，如需重新安装，请删除 .installed 文件');
}

// 设置错误报告
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 创建必要的目录
$directories = [
    '/logs',
    '/backup',
    '/uploads',
    '/assets/css',
    '/assets/js',
    '/assets/images'
];

foreach ($directories as $dir) {
    $fullPath = __DIR__ . $dir;
    if (!is_dir($fullPath)) {
        mkdir($fullPath, 0755, true);
        echo "✅ 创建目录: {$dir}\n";
    }
}

// 创建空的 .htaccess 文件
file_put_contents(__DIR__ . '/.htaccess', "Order Deny,Allow\nDeny from all\n");

// 设置配置
define('APP_NAME', '保质期管理系统');
define('APP_VERSION', '4.0.0');

// 数据库配置（根据实际环境修改）
define('DB_HOST', 'localhost');
define('DB_NAME', 'pandian');
define('DB_USER', 'root');
define('DB_PASS', '');

// 表前缀
define('TABLE_PREFIX', 'pd_');

echo "=== 保质期管理系统 v4.0.0 安装程序 ===\n\n";

try {
    // 连接数据库
    $dsn = "mysql:host=" . DB_HOST . ";charset=utf8mb4";
    $pdo = new PDO($dsn, DB_USER, DB_PASS);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    echo "✅ 数据库连接成功\n";
    
    // 创建数据库（如果不存在）
    $pdo->exec("CREATE DATABASE IF NOT EXISTS `" . DB_NAME . "` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci");
    echo "✅ 数据库创建成功\n";
    
    // 选择数据库
    $pdo->exec("USE `" . DB_NAME . "`");
    echo "✅ 选择数据库成功\n";
    
    // 创建用户表
    $sqlUsers = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "users` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(100) DEFAULT NULL,
        realname VARCHAR(50) DEFAULT NULL,
        role ENUM('admin', 'user') DEFAULT 'user',
        status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
        last_login DATETIME DEFAULT NULL,
        login_count INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlUsers);
    echo "✅ 用户表创建成功\n";
    
    // 创建分类表
    $sqlCategories = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "categories` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        type VARCHAR(20) DEFAULT 'food',
        description TEXT DEFAULT NULL,
        rule TEXT DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlCategories);
    echo "✅ 分类表创建成功\n";
    
    // 创建商品表
    $sqlProducts = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "products` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        sku VARCHAR(50) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        category_id INT UNSIGNED DEFAULT NULL,
        unit VARCHAR(20) DEFAULT '个',
        removal_buffer INT DEFAULT 0,
        description TEXT DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES " . TABLE_PREFIX . "categories(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlProducts);
    echo "✅ 商品表创建成功\n";
    
    // 创建盘点会话表
    $sqlInventorySessions = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "inventory_sessions` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        session_key VARCHAR(50) NOT NULL UNIQUE,
        user_id INT UNSIGNED DEFAULT NULL,
        item_count INT DEFAULT 0,
        status ENUM('draft', 'submitted', 'completed') DEFAULT 'draft',
        notes TEXT DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES " . TABLE_PREFIX . "users(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlInventorySessions);
    echo "✅ 盘点会话表创建成功\n";
    
    // 创建盘点条目表
    $sqlInventoryEntries = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "inventory_entries` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(50) DEFAULT NULL,
        product_id INT UNSIGNED DEFAULT NULL,
        quantity INT DEFAULT 1,
        batches TEXT DEFAULT NULL,
        notes TEXT DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES " . TABLE_PREFIX . "products(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlInventoryEntries);
    echo "✅ 盘点条目表创建成功\n";
    
    // 创建批次表
    $sqlBatches = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "batches` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        session_id VARCHAR(50) DEFAULT NULL,
        product_id INT UNSIGNED DEFAULT NULL,
        batch_code VARCHAR(50) DEFAULT NULL,
        expiry_date DATE DEFAULT NULL,
        quantity INT DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES " . TABLE_PREFIX . "products(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlBatches);
    echo "✅ 批次表创建成功\n";
    
    // 创建日志表
    $sqlLogs = "CREATE TABLE IF NOT EXISTS `" . TABLE_PREFIX . "logs` (
        id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNSIGNED DEFAULT NULL,
        action VARCHAR(100) NOT NULL,
        details TEXT DEFAULT NULL,
        ip_address VARCHAR(45) DEFAULT NULL,
        user_agent TEXT DEFAULT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES " . TABLE_PREFIX . "users(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci";
    
    $pdo->exec($sqlLogs);
    echo "✅ 日志表创建成功\n";
    
    // 检查是否有管理员用户
    $stmt = $pdo->prepare("SELECT COUNT(*) as count FROM `" . TABLE_PREFIX . "users` WHERE role = 'admin'");
    $stmt->execute();
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($result['count'] == 0) {
        // 创建默认管理员用户
        $password = password_hash('fs123456', PASSWORD_DEFAULT);
        
        $stmt = $pdo->prepare("INSERT INTO `" . TABLE_PREFIX . "users` (username, password, email, realname, role, status) VALUES (?, ?, ?, ?, ?, ?)");
        $stmt->execute(['admin', $password, 'admin@example.com', '系统管理员', 'admin', 'active']);
        
        echo "✅ 默认管理员用户创建成功 (用户名: admin, 密码: fs123456)\n";
    } else {
        echo "ℹ️  管理员用户已存在，跳过创建\n";
    }
    
    // 检查是否有默认分类
    $stmt = $pdo->prepare("SELECT COUNT(*) as count FROM `" . TABLE_PREFIX . "categories`");
    $stmt->execute();
    $result = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($result['count'] == 0) {
        // 创建默认分类
        $categories = [
            ['小食品', 'snack', '小食品类商品'],
            ['物料', 'material', '物料类商品'],
            ['咖啡豆', 'coffee', '咖啡豆类商品']
        ];
        
        $stmt = $pdo->prepare("INSERT INTO `" . TABLE_PREFIX . "categories` (name, type, description) VALUES (?, ?, ?)");
        
        foreach ($categories as $category) {
            $stmt->execute($category);
        }
        
        echo "✅ 默认分类创建成功\n";
    } else {
        echo "ℹ️  默认分类已存在，跳过创建\n";
    }
    
    // 创建安装标记文件
    file_put_contents(__DIR__ . '/.installed', date('Y-m-d H:i:s'));
    
    echo "\n";
    echo "=== 安装完成 ===\n";
    echo "✅ 数据库初始化完成\n";
    echo "✅ 默认管理员用户: admin / fs123456\n";
    echo "✅ 系统版本: " . APP_VERSION . "\n";
    echo "\n";
    echo "请删除 install.php 文件以保证系统安全\n";
    echo "请访问 /pages/login.php 开始使用系统\n";
    
} catch (PDOException $e) {
    echo "\n";
    echo "❌ 安装失败: " . $e->getMessage() . "\n";
    echo "\n";
    echo "请检查数据库配置和连接权限\n";
    exit(1);
}
