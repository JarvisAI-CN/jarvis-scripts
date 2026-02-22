<?php
/**
 * 保质期管理系统 - v4.0.0 数据库连接类
 */

require_once 'config.php';

class Database
{
    private static $instance = null;
    private $pdo;

    private function __construct()
    {
        $dsn = "mysql:host=" . DB_HOST . ";port=" . DB_PORT . ";dbname=" . DB_NAME . ";charset=" . DB_CHARSET;
        
        $options = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
            PDO::ATTR_PERSISTENT => DB_PERSISTENT,
        ];

        try {
            $this->pdo = new PDO($dsn, DB_USER, DB_PASS, $options);
            
            // 设置字符集
            $this->pdo->exec("SET NAMES '" . DB_CHARSET . "' COLLATE '" . DB_COLLATION . "'");
            
            // 启用外键约束
            $this->pdo->exec("SET foreign_key_checks = 1");
            
            // 检查数据库连接状态
            $this->checkConnection();
            
            logger('info', '数据库连接成功');
        } catch (PDOException $e) {
            logger('critical', '数据库连接失败: ' . $e->getMessage());
            die('数据库连接失败');
        }
    }

    public static function getInstance()
    {
        if (self::$instance === null) {
            self::$instance = new Database();
        }
        return self::$instance;
    }

    public function getPDO()
    {
        return $this->pdo;
    }

    private function checkConnection()
    {
        try {
            $stmt = $this->pdo->query("SELECT 1");
            if (!$stmt || $stmt->fetch() !== ['1' => '1']) {
                throw new Exception('连接验证失败');
            }
        } catch (Exception $e) {
            logger('error', '数据库连接验证失败: ' . $e->getMessage());
            die('数据库连接验证失败');
        }
    }

    // 执行查询
    public function query($sql, $params = [])
    {
        try {
            $stmt = $this->pdo->prepare($sql);
            $stmt->execute($params);
            return $stmt;
        } catch (PDOException $e) {
            logger('error', '查询失败: ' . $sql . ' | ' . $e->getMessage());
            throw $e;
        }
    }

    // 获取单行结果
    public function fetchOne($sql, $params = [])
    {
        $stmt = $this->query($sql, $params);
        return $stmt->fetch();
    }

    // 获取所有结果
    public function fetchAll($sql, $params = [])
    {
        $stmt = $this->query($sql, $params);
        return $stmt->fetchAll();
    }

    // 执行插入操作
    public function insert($table, $data)
    {
        $columns = implode(', ', array_keys($data));
        $placeholders = implode(', ', array_fill(0, count($data), '?'));
        $values = array_values($data);
        
        $sql = "INSERT INTO " . TABLE_PREFIX . $table . " (" . $columns . ") VALUES (" . $placeholders . ")";
        
        $this->query($sql, $values);
        return $this->pdo->lastInsertId();
    }

    // 执行更新操作
    public function update($table, $data, $where, $whereParams = [])
    {
        $setClause = implode('=?, ', array_keys($data)) . "=?";
        $values = array_merge(array_values($data), $whereParams);
        
        $sql = "UPDATE " . TABLE_PREFIX . $table . " SET " . $setClause . " WHERE " . $where;
        
        $stmt = $this->query($sql, $values);
        return $stmt->rowCount();
    }

    // 执行删除操作
    public function delete($table, $where, $whereParams = [])
    {
        $sql = "DELETE FROM " . TABLE_PREFIX . $table . " WHERE " . $where;
        $stmt = $this->query($sql, $whereParams);
        return $stmt->rowCount();
    }

    // 事务管理
    public function beginTransaction()
    {
        $this->pdo->beginTransaction();
    }

    public function commit()
    {
        $this->pdo->commit();
    }

    public function rollBack()
    {
        $this->pdo->rollBack();
    }

    // 获取受影响行数
    public function rowCount($stmt)
    {
        return $stmt->rowCount();
    }

    // 获取错误信息
    public function errorInfo($stmt)
    {
        return $stmt->errorInfo();
    }

    // 自动创建表结构（安装/升级）
    public function createTables()
    {
        $tables = [
            'users' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "users (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'categories' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "categories (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE,
                type VARCHAR(20) DEFAULT 'food',
                description TEXT DEFAULT NULL,
                rule TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'products' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "products (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'inventory_sessions' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "inventory_sessions (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                session_key VARCHAR(50) NOT NULL UNIQUE,
                user_id INT UNSIGNED DEFAULT NULL,
                item_count INT DEFAULT 0,
                status ENUM('draft', 'submitted', 'completed') DEFAULT 'draft',
                notes TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES " . TABLE_PREFIX . "users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'inventory_entries' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "inventory_entries (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(50) DEFAULT NULL,
                product_id INT UNSIGNED DEFAULT NULL,
                quantity INT DEFAULT 1,
                batches TEXT DEFAULT NULL,
                notes TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES " . TABLE_PREFIX . "products(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'batches' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "batches (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(50) DEFAULT NULL,
                product_id INT UNSIGNED DEFAULT NULL,
                batch_code VARCHAR(50) DEFAULT NULL,
                expiry_date DATE DEFAULT NULL,
                quantity INT DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES " . TABLE_PREFIX . "products(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION,

            'logs' => "CREATE TABLE IF NOT EXISTS " . TABLE_PREFIX . "logs (
                id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                user_id INT UNSIGNED DEFAULT NULL,
                action VARCHAR(100) NOT NULL,
                details TEXT DEFAULT NULL,
                ip_address VARCHAR(45) DEFAULT NULL,
                user_agent TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES " . TABLE_PREFIX . "users(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=" . DB_CHARSET . " COLLATE=" . DB_COLLATION
        ];

        try {
            foreach ($tables as $tableName => $sql) {
                $this->query($sql);
                logger('info', "表 " . TABLE_PREFIX . $tableName . " 创建/检查完成");
            }

            // 插入默认数据
            $this->insertDefaultData();
            
            logger('info', '数据库表结构创建完成');
            return true;
        } catch (Exception $e) {
            logger('critical', '表结构创建失败: ' . $e->getMessage());
            return false;
        }
    }

    // 插入默认数据
    private function insertDefaultData()
    {
        // 检查是否有管理员用户
        $adminCount = $this->fetchOne("SELECT COUNT(*) as count FROM " . TABLE_PREFIX . "users WHERE role = 'admin'");
        
        if ($adminCount['count'] == 0) {
            $password = password_hash('fs123456', PASSWORD_DEFAULT);
            
            $this->insert('users', [
                'username' => 'admin',
                'password' => $password,
                'email' => 'admin@example.com',
                'realname' => '系统管理员',
                'role' => 'admin',
                'status' => 'active'
            ]);
            
            logger('info', '默认管理员用户创建成功');
        }

        // 检查是否有默认分类
        $categoryCount = $this->fetchOne("SELECT COUNT(*) as count FROM " . TABLE_PREFIX . "categories");
        
        if ($categoryCount['count'] == 0) {
            $categories = [
                ['name' => '小食品', 'type' => 'snack', 'description' => '小食品类商品'],
                ['name' => '物料', 'type' => 'material', 'description' => '物料类商品'],
                ['name' => '咖啡豆', 'type' => 'coffee', 'description' => '咖啡豆类商品']
            ];
            
            foreach ($categories as $category) {
                $this->insert('categories', $category);
            }
            
            logger('info', '默认分类创建成功');
        }
    }

    // 数据库版本检查
    public function checkDatabaseVersion()
    {
        try {
            $result = $this->fetchOne("SELECT VERSION() as version");
            logger('info', 'MySQL版本: ' . $result['version']);
            
            $result = $this->fetchOne("SELECT @@sql_mode as mode");
            logger('info', 'SQL模式: ' . $result['mode']);
            
            return true;
        } catch (Exception $e) {
            logger('error', '数据库版本检查失败: ' . $e->getMessage());
            return false;
        }
    }
}

// 获取数据库实例
function getDB()
{
    return Database::getInstance();
}

// 初始化数据库
if (DEBUG_MODE) {
    try {
        $db = getDB();
        $db->checkDatabaseVersion();
    } catch (Exception $e) {
        logger('critical', '数据库初始化失败: ' . $e->getMessage());
    }
}
