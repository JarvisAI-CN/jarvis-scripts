<?php
/**
 * ========================================
 * 保质期管理系统 - 主页面（完整版）
 * 文件名: index.php
 * 版本: v2.1.1-alpha
 * 创建日期: 2026-02-15
 * ========================================
 * 功能说明：
 * 1. 分类管理: 酸奶/饼干(小食品)、物料、咖啡豆，支持不同下架规则
 * 2. 提前下架: 支持设置每个商品提前 N 天提醒/下架
 * 3. 智能化: 首页健康大盘可视化
 * 4. 安全化: 关键操作全程日志记录
 * 5. 预警化: 支持配置 3/7/15 天自动预警
 * 6. 权限控制: 仅登录用户可访问
 * 7. 一键升级: 在线热更新
 * ========================================
 */

// 升级配置
define('APP_VERSION', '2.1.3-alpha');
define('UPDATE_URL', 'https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/main/');

// 启动 Session
session_start();

// 引入数据库连接文件
require_once 'db.php';

// ========================================
// 自动数据库升级逻辑 (Auto-Migration)
// ========================================
function autoMigrate() {
    $conn = getDBConnection();
    if (!$conn) return;

    // 1. 检查 products 表是否有 category_id 字段
    $res = $conn->query("SHOW COLUMNS FROM `products` LIKE 'category_id'");
    if ($res && $res->num_rows == 0) {
        // 分步执行：先加字段，再加索引，确保语法兼容
        $conn->query("ALTER TABLE `products` ADD COLUMN `category_id` INT(11) UNSIGNED DEFAULT 0 AFTER `id` ");
        $conn->query("ALTER TABLE `products` ADD INDEX(`category_id`) ");
    }

    // 2. 检查 categories 表是否存在
    $res = $conn->query("SHOW TABLES LIKE 'categories'");
    if ($res && $res->num_rows == 0) {
        $conn->query("
            CREATE TABLE `categories` (
              `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
              `name` VARCHAR(50) NOT NULL,
              `type` VARCHAR(20) NOT NULL,
              `rule` TEXT,
              `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
              PRIMARY KEY (`id`),
              UNIQUE KEY `uk_name` (`name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ");
        
        // 初始数据
        $conn->query("INSERT IGNORE INTO `categories` (`name`, `type`, `rule`) VALUES 
            ('小食品', 'snack', '{\"need_buffer\":true, \"scrap_on_removal\":true}'),
            ('物料', 'material', '{\"need_buffer\":false, \"scrap_on_removal\":false}'),
            ('咖啡豆', 'coffee', '{\"need_buffer\":true, \"scrap_on_removal\":false, \"allow_gift\":true}')");
    }
}

// 每次运行尝试静默升级
autoMigrate();

// ========================================
// PHP 后端 API 处理
// ========================================

// 处理 AJAX 请求
if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    $action = $_GET['api'];
    
    // 获取数据库连接
    $conn = getDBConnection();
    if (!$conn) {
        echo json_encode(['success' => false, 'message' => '数据库连接失败'], JSON_UNESCAPED_UNICODE);
        exit;
    }

    // ========================================
    // 公开 API: 登录
    // ========================================
    if ($action === 'login') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        $user = $data['username'] ?? '';
        $pass = $data['password'] ?? '';

        $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ? LIMIT 1");
        $stmt->bind_param("s", $user);
        $stmt->execute();
        $res = $stmt->get_result();

        if ($row = $res->fetch_assoc()) {
            if (password_verify($pass, $row['password'])) {
                $_SESSION['user_id'] = $row['id'];
                $_SESSION['username'] = $row['username'];
                echo json_encode(['success' => true, 'message' => '登录成功']);
                exit;
            }
        }
        echo json_encode(['success' => false, 'message' => '账号或密码错误']);
        exit;
    }

    // ========================================
    // 公开 API: 登出
    // ========================================
    if ($action === 'logout') {
        session_destroy();
        echo json_encode(['success' => true, 'message' => '已成功登出']);
        exit;
    }

    // ========================================
    // 公开 API: 检查更新
    // ========================================
    if ($action === 'check_upgrade') {
        $latest_version_url = UPDATE_URL . 'VERSION.txt';
        $latest_version = @file_get_contents($latest_version_url);
        
        if ($latest_version === false) {
            echo json_encode(['success' => false, 'message' => '无法连接到更新服务器']);
        } else {
            $latest_version = trim($latest_version);
            $has_update = version_compare($latest_version, APP_VERSION, '>');
            echo json_encode([
                'success' => true,
                'current' => APP_VERSION,
                'latest' => $latest_version,
                'has_update' => $has_update
            ]);
        }
        exit;
    }

    // ========================================
    // 公开 API: 执行升级
    // ========================================
    if ($action === 'execute_upgrade') {
        $files = ['index.php', 'db.php', 'install.php', 'VERSION.txt'];
        $errors = [];
        
        foreach ($files as $file) {
            $remote_content = @file_get_contents(UPDATE_URL . $file);
            if ($remote_content !== false) {
                if (!@file_put_contents(__DIR__ . '/' . $file, $remote_content)) {
                    $errors[] = "无法写入 $file";
                }
            } else {
                $errors[] = "无法下载 $file";
            }
        }
        
        if (empty($errors)) {
            echo json_encode(['success' => true, 'message' => '升级成功！正在刷新页面...']);
        } else {
            echo json_encode(['success' => false, 'message' => implode(", ", $errors)]);
        }
        exit;
    }

    // --- 以下 API 均需要登录 ---
    checkAuth();
    
    // ========================================
    // API 1: 根据 SKU 查询商品信息
    // ========================================
    if ($action === 'get_product') {
        $sku = isset($_GET['sku']) ? trim($_GET['sku']) : '';
        
        if (empty($sku)) {
            echo json_encode(['success' => false, 'message' => 'SKU 不能为空'], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 连表查询分类规则
        $stmt = $conn->prepare("
            SELECT p.*, c.name as category_name, c.type as category_type, c.rule as category_rule 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.sku = ? LIMIT 1
        ");
        $stmt->bind_param("s", $sku);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            $product = $result->fetch_assoc();
            $productId = $product['id'];
            $buffer = (int)$product['removal_buffer'];
            $rule = json_decode($product['category_rule'] ?? '{}', true);
            $needBuffer = $rule['need_buffer'] ?? true;
            
            // 查询该商品的所有批次
            $stmt_batch = $conn->prepare("SELECT * FROM batches WHERE product_id = ? ORDER BY expiry_date ASC");
            $stmt_batch->bind_param("i", $productId);
            $stmt_batch->execute();
            $batch_result = $stmt_batch->get_result();
            
            $batches = [];
            while ($batch = $batch_result->fetch_assoc()) {
                $expiryDate = $batch['expiry_date'];
                
                // 根据分类规则决定是否应用缓冲
                $effectiveBuffer = $needBuffer ? $buffer : 0;
                $removalDate = date('Y-m-d', strtotime("$expiryDate - $effectiveBuffer days"));
                
                $today = date('Y-m-d');
                $daysToRemoval = (strtotime($removalDate) - strtotime($today)) / 86400;
                
                // 构建AI状态描述
                $ai_status_text = "";
                if ($daysToRemoval < 0) {
                    if ($product['category_type'] === 'coffee') {
                        $ai_status_text = "⚠️ 停止销售 (可赠送)";
                    } else {
                        $ai_status_text = "🔴 立即下架/报废";
                    }
                } elseif ($daysToRemoval <= 7) {
                    $ai_status_text = "🟡 临期紧急";
                } else {
                    $ai_status_text = "🟢 状态良好";
                }
                
                $batches[] = [
                    'id' => $batch['id'],
                    'expiry_date' => $expiryDate,
                    'removal_date' => $removalDate,
                    'quantity' => (int)$batch['quantity'],
                    'days_to_removal' => (int)$daysToRemoval,
                    'status' => $daysToRemoval < 0 ? 'expired' : ($daysToRemoval <= 30 ? 'warning' : 'normal'),
                    'ai_status' => $ai_status_text
                ];
            }
            
            echo json_encode([
                'success' => true,
                'exists' => true,
                'product' => $product,
                'batches' => $batches
            ], JSON_UNESCAPED_UNICODE);
        } else {
            // 商品不存在
            echo json_encode([
                'success' => true,
                'exists' => false,
                'message' => '新商品，请输入商品名称'
            ], JSON_UNESCAPED_UNICODE);
        }
        exit;
    }
    
    // ========================================
    // API 2: 保存商品和批次信息
    // ========================================
    if ($action === 'save_product') {
        // 只接受 POST 请求
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
            echo json_encode(['success' => false, 'message' => '请求方法错误'], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 获取 JSON 数据
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        
        $sku = isset($data['sku']) ? trim($data['sku']) : '';
        $name = isset($data['name']) ? trim($data['name']) : '';
        $cid = isset($data['category_id']) ? (int)$data['category_id'] : 0;
        $buffer = isset($data['removal_buffer']) ? (int)$data['removal_buffer'] : 0;
        $batches = isset($data['batches']) ? $data['batches'] : [];
        
        // 数据验证
        if (empty($sku)) {
            echo json_encode(['success' => false, 'message' => 'SKU 不能为空'], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        if (empty($name)) {
            echo json_encode(['success' => false, 'message' => '商品名称不能为空'], JSON_UNESCAPED_UNICODE);
            exit;
        }
        
        // 开始事务
        $conn->begin_transaction();
        
        try {
            $stmt_check = $conn->prepare("SELECT id FROM products WHERE sku = ? LIMIT 1");
            $stmt_check->bind_param("s", $sku);
            $stmt_check->execute();
            $check_result = $stmt_check->get_result();
            
            $productId = null;
            if ($row = $check_result->fetch_assoc()) {
                $productId = $row['id'];
                $stmt_update = $conn->prepare("UPDATE products SET name = ?, category_id = ?, removal_buffer = ? WHERE id = ?");
                $stmt_update->bind_param("siii", $name, $cid, $buffer, $productId);
                $stmt_update->execute();
                
                $conn->query("DELETE FROM batches WHERE product_id = $productId");
            } else {
                $stmt_insert = $conn->prepare("INSERT INTO products (sku, name, category_id, removal_buffer) VALUES (?, ?, ?, ?)");
                $stmt_insert->bind_param("ssii", $sku, $name, $cid, $buffer);
                $stmt_insert->execute();
                $productId = $conn->insert_id;
            }
            
            $stmt_batch = $conn->prepare("INSERT INTO batches (product_id, expiry_date, quantity) VALUES (?, ?, ?)");
            foreach ($batches as $batch) {
                $stmt_batch->bind_param("isi", $productId, $batch['expiry_date'], $batch['quantity']);
                $stmt_batch->execute();
            }
            
            addLog("保存商品", "SKU: $sku, 分类ID: $cid, 缓冲: $buffer");
            $conn->commit();
            echo json_encode(['success' => true, 'message' => '保存成功！', 'product_id' => $productId]);
        } catch (Exception $e) {
            $conn->rollback();
            echo json_encode(['success' => false, 'message' => '保存失败: ' . $e->getMessage()]);
        }
        exit;
    }
    
    // ========================================
    // API 3: 获取统计数据
    // ========================================
    if ($action === 'get_statistics') {
        // 统计商品总数
        $result_products = $conn->query("SELECT COUNT(*) as total FROM products");
        $total_products = $result_products->fetch_assoc()['total'];
        
        // 统计批次总数
        $result_batches = $conn->query("SELECT COUNT(*) as total FROM batches");
        $total_batches = $result_batches->fetch_assoc()['total'];
        
        // 统计即将过期的批次（30天内）
        $stmt_expiry_soon = $conn->prepare("
            SELECT COUNT(*) as total 
            FROM batches 
            WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ");
        $stmt_expiry_soon->execute();
        $expiry_soon = $stmt_expiry_soon->get_result()->fetch_assoc()['total'];
        
        // 统计已过期的批次
        $stmt_expired = $conn->prepare("
            SELECT COUNT(*) as total 
            FROM batches 
            WHERE expiry_date < CURDATE()
        ");
        $stmt_expired->execute();
        $expired = $stmt_expired->get_result()->fetch_assoc()['total'];
        
        echo json_encode([
            'success' => true,
            'statistics' => [
                'total_products' => (int)$total_products,
                'total_batches' => (int)$total_batches,
                'expiry_soon' => (int)$expiry_soon,
                'expired' => (int)$expired
            ]
        ], JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // ========================================
    // API 4: 导出盘点表 (CSV 格式)
    // ========================================
    if ($action === 'export_inventory') {
        // 设置 HTTP 头部，触发下载
        $filename = "盘点表_" . date('Ymd_His') . ".csv";
        header('Content-Type: text/csv; charset=utf-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');
        
        // 输出 UTF-8 BOM，确保 Excel 打开不乱码
        echo "\xEF\xBB\xBF";
        
        $output = fopen('php://output', 'w');
        
        // 写入表头
        fputcsv($output, ['SKU/条形码', '商品名称', '到期日期', '当前数量', '状态/AI建议']);
        
        // 查询所有商品及其批次，核心：按到期日期升序排列 (AI 整理逻辑)
        // 找到期的放在前面，后到期的放在后面
        $query = "
            SELECT p.sku, p.name, p.removal_buffer, b.expiry_date, b.quantity 
            FROM products p 
            JOIN batches b ON p.id = b.product_id 
            ORDER BY DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) ASC
        ";
        $result = $conn->query($query);
        
        while ($row = $result->fetch_assoc()) {
            $today = date('Y-m-d');
            $buffer = (int)$row['removal_buffer'];
            $expiryDate = $row['expiry_date'];
            $removalDate = date('Y-m-d', strtotime("$expiryDate - $buffer days"));
            
            $diffDays = (strtotime($removalDate) - strtotime($today)) / 86400;
            
            // AI 状态整理逻辑
            $ai_status = "";
            if ($diffDays < 0) {
                $ai_status = "🔴 已过期/需下架 (原到期: $expiryDate)";
            } elseif ($diffDays <= 30) {
                $ai_status = "🟡 临期预警 (" . floor($diffDays) . "天内需下架)";
            } else {
                $ai_status = "🟢 正常 (" . floor($diffDays) . "天后下架)";
            }
            
            fputcsv($output, [
                $row['sku'],
                $row['name'],
                $row['expiry_date'],
                $row['quantity'],
                $ai_status
            ]);
        }
        
        fclose($output);
        exit;
    }

    // ========================================
    // API 7: 获取用户列表
    // ========================================
    if ($action === 'get_users') {
        $result = $conn->query("SELECT id, username, created_at FROM users");
        $users = [];
        while ($row = $result->fetch_assoc()) {
            $users[] = $row;
        }
        echo json_encode(['success' => true, 'users' => $users]);
        exit;
    }

    // ========================================
    // API 8: 添加用户
    // ========================================
    if ($action === 'add_user') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        $user = $data['username'] ?? '';
        $pass = $data['password'] ?? '';

        if (empty($user) || empty($pass)) {
            echo json_encode(['success' => false, 'message' => '请填写完整信息']);
            exit;
        }

        $hashed = password_hash($pass, PASSWORD_DEFAULT);
        $stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
        $stmt->bind_param("ss", $user, $hashed);
        if ($stmt->execute()) {
            echo json_encode(['success' => true, 'message' => '用户添加成功']);
        } else {
            echo json_encode(['success' => false, 'message' => '用户名已存在']);
        }
        exit;
    }

    // ========================================
    // API 9: 修改密码 (无验证)
    // ========================================
    if ($action === 'reset_password') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        $uid = $data['user_id'] ?? 0;
        $new_pass = $data['new_password'] ?? '';

        if (empty($uid) || empty($new_pass)) {
            echo json_encode(['success' => false, 'message' => '参数错误']);
            exit;
        }

        $hashed = password_hash($new_pass, PASSWORD_DEFAULT);
        $stmt = $conn->prepare("UPDATE users SET password = ? WHERE id = ?");
        $stmt->bind_param("si", $hashed, $uid);
        if ($stmt->execute()) {
            echo json_encode(['success' => true, 'message' => '密码修改成功']);
        } else {
            echo json_encode(['success' => false, 'message' => '修改失败']);
        }
        exit;
    }

    // ========================================
    // API 10: 保存 AI 设置
    // ========================================
    if ($action === 'save_settings') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        
        $success = true;
        foreach ($data as $key => $value) {
            if (!setSetting($key, $value)) $success = false;
        }
        
        echo json_encode(['success' => $success, 'message' => $success ? '设置保存成功' : '部分设置保存失败']);
        exit;
    }

    // ========================================
    // API 11: 获取当前设置
    // ========================================
    if ($action === 'get_settings') {
        echo json_encode([
            'success' => true,
            'settings' => [
                'ai_api_url' => getSetting('ai_api_url'),
                'ai_api_key' => getSetting('ai_api_key'),
                'ai_model' => getSetting('ai_model'),
                'alert_email' => getSetting('alert_email'),
                'alert_days' => getSetting('alert_days')
            ]
        ]);
        exit;
    }

    // ========================================
    // API 12: 获取健康报告数据
    // ========================================
    if ($action === 'get_health_report') {
        // 过期数据分布 (基于下架日期，关联分类规则)
        $query = "
            SELECT 
                SUM(CASE WHEN DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) < CURDATE() THEN 1 ELSE 0 END) as expired,
                SUM(CASE WHEN DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END) as urgent,
                SUM(CASE WHEN DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) BETWEEN DATE_ADD(CURDATE(), INTERVAL 8 DAY) AND DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as warning,
                SUM(CASE WHEN DATE_SUB(b.expiry_date, INTERVAL p.removal_buffer DAY) > DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 1 ELSE 0 END) as healthy
            FROM batches b
            JOIN products p ON b.product_id = p.id
        ";
        $data = $conn->query($query)->fetch_assoc();
        echo json_encode(['success' => true, 'report' => $data]);
        exit;
    }

    // ========================================
    // API 13: 获取最新日志
    // ========================================
    if ($action === 'get_logs') {
        $query = "SELECT l.*, u.username FROM logs l LEFT JOIN users u ON l.user_id = u.id ORDER BY l.created_at DESC LIMIT 10";
        $res = $conn->query($query);
        $logs = [];
        while($row = $res->fetch_assoc()) $logs[] = $row;
        echo json_encode(['success' => true, 'logs' => $logs]);
        exit;
    }

    // ========================================
    // API 14: 获取全部分类
    // ========================================
    if ($action === 'get_categories') {
        $res = $conn->query("SELECT * FROM categories ORDER BY id ASC");
        $list = [];
        while($row = $res->fetch_assoc()) $list[] = $row;
        echo json_encode(['success' => true, 'categories' => $list]);
        exit;
    }

    // ========================================
    // API 15: 保存分类
    // ========================================
    if ($action === 'save_category') {
        $json = file_get_contents('php://input');
        $data = json_decode($json, true);
        $name = $data['name'] ?? '';
        $type = $data['type'] ?? '';
        $rule = $data['rule'] ?? '';

        $stmt = $conn->prepare("INSERT INTO categories (name, type, rule) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE type=VALUES(type), rule=VALUES(rule)");
        $stmt->bind_param("sss", $name, $type, $rule);
        if ($stmt->execute()) {
            echo json_encode(['success' => true, 'message' => '分类保存成功']);
        } else {
            echo json_encode(['success' => false, 'message' => '保存失败']);
        }
        exit;
    }

    // 未知的 API 请求
    echo json_encode([
        'success' => false,
        'message' => '未知的 API 请求'
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>保质期管理系统 v2.1</title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    <!-- html5-qrcode 扫码库 -->
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    
    <style>
        /* ========================================
           全局样式
           ======================================== */
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
        }
        
        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }
        
        body {
            background: #f0f2f5;
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            padding-bottom: 50px;
        }
        
        /* ========================================
           头部样式
           ======================================== */
        .app-header {
            background: #fff;
            color: #333;
            padding: 12px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            margin-bottom: 15px;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .app-header h1 {
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0;
            color: var(--primary-color);
        }
        
        .app-header .subtitle {
            font-size: 0.75rem;
            color: #999;
        }

        /* 版本标签 */
        .version-tag {
            font-size: 0.65rem;
            padding: 2px 6px;
            background: #eee;
            border-radius: 4px;
            color: #666;
        }
        
        /* ========================================
           卡片样式
           ======================================== */
        .custom-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            border: none;
        }
        
        .custom-card .card-title {
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* ========================================
           扫码区域 (仿微信扫一扫)
           ======================================== */
        .scan-trigger-area {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border-radius: 12px;
            padding: 40px 20px;
            text-align: center;
            color: white;
            cursor: pointer;
            transition: opacity 0.2s;
        }

        .scan-trigger-area:active {
            opacity: 0.8;
        }

        .scan-trigger-area i {
            font-size: 3rem;
            display: block;
            margin-bottom: 10px;
        }

        .scan-trigger-area span {
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* 全屏扫描容器 */
        #scanOverlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #000;
            z-index: 2000;
            display: none;
            flex-direction: column;
        }

        #reader {
            width: 100%;
            height: 100%;
        }

        .scan-overlay-header {
            position: absolute;
            top: 0;
            width: 100%;
            padding: 20px;
            z-index: 2001;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }

        .scan-hint {
            position: absolute;
            bottom: 150px;
            width: 100%;
            text-align: center;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
            z-index: 2001;
        }

        .close-scan-btn {
            background: rgba(0, 0, 0, 0.5);
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 1.2rem;
        }
        
        /* ========================================
           统计与大盘
           ======================================== */
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 15px;
        }

        .stat-item {
            background: white;
            padding: 12px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-item .val {
            font-size: 1.4rem;
            font-weight: 700;
            display: block;
        }

        .stat-item .label {
            font-size: 0.7rem;
            color: #999;
        }

        .health-bar-container {
            padding: 10px;
            background: #fff;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        /* ========================================
           表单优化
           ======================================== */
        .form-floating > .form-control {
            height: 55px;
            border-radius: 8px;
            border: 1px solid #eee;
        }

        .batch-item {
            background: #f9f9f9;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            border: 1px solid #f0f0f0;
        }
        
        .btn-lg-custom {
            height: 50px;
            border-radius: 25px;
            font-weight: 600;
        }

        /* 隐藏不必要的元素 */
        .desktop-only { display: none; }
        @media (min-width: 992px) { .desktop-only { display: block; } }

    </style>
</head>
<body>
    <!-- 全屏扫描遮罩 -->
    <div id="scanOverlay">
        <div class="scan-overlay-header">
            <button class="close-scan-btn" id="stopScanBtn"><i class="bi bi-x-lg"></i></button>
            <div class="fw-bold">扫一扫</div>
            <div style="width: 40px;"></div>
        </div>
        <div id="reader"></div>
        <div class="scan-hint">请将二维码/条形码置于框内</div>
    </div>

    <!-- 移动端头部 -->
    <div class="app-header">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h1>保质期管理 <span class="version-tag">v<?php echo APP_VERSION; ?></span></h1>
                    <div class="subtitle">让临期商品无处遁形</div>
                </div>
                <div class="dropdown">
                    <button class="btn btn-light btn-sm rounded-pill" type="button" data-bs-toggle="dropdown">
                        <i class="bi bi-list"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end shadow border-0" style="border-radius: 12px;">
                        <?php if (isset($_SESSION['user_id'])): ?>
                        <li><a class="dropdown-item" href="#" data-bs-toggle="modal" data-bs-target="#settingsModal"><i class="bi bi-gear me-2"></i>管理中心</a></li>
                        <li><a class="dropdown-item text-danger" href="#" id="logoutBtn"><i class="bi bi-box-arrow-right me-2"></i>退出登录</a></li>
                        <?php endif; ?>
                        <li><a class="dropdown-item" href="#" id="upgradeBtn"><i class="bi bi-cloud-arrow-up me-2"></i>系统升级</a></li>
                        <li><a class="dropdown-item" href="#" id="exportBtn"><i class="bi bi-file-earmark-spreadsheet me-2"></i>导出报表</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <?php if (!isset($_SESSION['user_id'])): ?>
        <!-- 登录页 (保持原有逻辑) -->
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="custom-card fade-in text-center mt-5">
                    <h3 class="mb-4 fw-bold text-primary">⚡ 身份验证</h3>
                    <form id="loginForm">
                        <div class="form-floating mb-3">
                            <input type="text" class="form-control" id="loginUser" placeholder="用户名" required>
                            <label for="loginUser">用户名</label>
                        </div>
                        <div class="form-floating mb-4">
                            <input type="password" class="form-control" id="loginPass" placeholder="密码" required>
                            <label for="loginPass">密码</label>
                        </div>
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg-custom">进入系统</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
        <?php else: ?>
        
        <!-- 健康看板 (移动端紧凑版) -->
        <div class="health-bar-container shadow-sm mb-3">
            <div class="d-flex justify-content-between mb-1 small px-1">
                <span class="text-muted">效期健康度</span>
                <span id="refreshStatsBtn" class="text-primary" style="cursor: pointer;"><i class="bi bi-arrow-clockwise"></i> 刷新</span>
            </div>
            <div class="progress mb-2" style="height: 12px; border-radius: 6px; background: #eee;">
                <div id="bar-expired" class="progress-bar bg-danger" role="progressbar"></div>
                <div id="bar-urgent" class="progress-bar bg-warning" role="progressbar"></div>
                <div id="bar-healthy" class="progress-bar bg-success" role="progressbar"></div>
            </div>
            <div class="row text-center g-0">
                <div class="col-4 border-end">
                    <span class="d-block fw-bold text-danger" id="val-expired">0</span>
                    <span class="text-muted" style="font-size: 0.6rem;">已过期</span>
                </div>
                <div class="col-4 border-end">
                    <span class="d-block fw-bold text-warning" id="val-urgent">0</span>
                    <span class="text-muted" style="font-size: 0.6rem;">临期</span>
                </div>
                <div class="col-4">
                    <span class="d-block fw-bold text-success" id="val-healthy">0</span>
                    <span class="text-muted" style="font-size: 0.6rem;">健康</span>
                </div>
            </div>
        </div>

        <!-- 仿微信扫码触发区 -->
        <div class="scan-trigger-area shadow-sm mb-3" id="startScanBtn">
            <i class="bi bi-qr-code-scan"></i>
            <span>点此开始扫描二维码 / 条形码</span>
        </div>

        <!-- 商品录入表单 -->
        <div class="custom-card shadow-sm">
            <form id="productForm">
                <div class="row g-2 mb-3">
                    <div class="col-12">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="sku" name="sku" placeholder="SKU/条形码" required>
                            <label for="sku">SKU / 条形码</label>
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="form-floating">
                            <select class="form-select" id="categoryId" name="categoryId">
                                <option value="0">选择商品分类</option>
                            </select>
                            <label for="categoryId">所属分类</label>
                        </div>
                    </div>
                </div>
                
                <div class="row g-2 mb-3">
                    <div class="col-8">
                        <div class="form-floating">
                            <input type="text" class="form-control" id="productName" name="productName" placeholder="商品名称" required>
                            <label for="productName">商品名称</label>
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="form-floating">
                            <input type="number" class="form-control" id="removalBuffer" name="removalBuffer" value="0" min="0" required>
                            <label for="removalBuffer">提前下架</label>
                        </div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="fw-bold"><i class="bi bi-layers text-primary"></i> 批次明细</span>
                        <button type="button" class="btn btn-success btn-sm rounded-pill" id="addBatchBtn">
                            <i class="bi bi-plus"></i> 添加批次
                        </button>
                    </div>
                    <div id="batchesContainer"></div>
                </div>
                
                <div class="d-grid gap-2">
                    <button type="submit" class="btn btn-primary btn-lg-custom">确认录入并保存</button>
                    <button type="button" class="btn btn-light btn-sm text-muted" id="resetFormBtn">重置清空</button>
                </div>
            </form>
        </div>

        <!-- 简易说明 -->
        <div class="text-center text-muted mt-2" style="font-size: 0.75rem;">
            Powered by Jarvis AI · 技术安全第一位
        </div>
        <?php endif; ?>
    </div>

    <!-- 管理设置模态框 -->
    <div class="modal fade" id="settingsModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content" style="border-radius: 15px;">
                <div class="modal-header">
                    <h5 class="modal-title fw-bold"><i class="bi bi-gear-wide-connected"></i> 管理中心</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <ul class="nav nav-tabs mb-3" id="settingsTabs">
                        <li class="nav-item">
                            <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#userTab">用户管理</button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#categoryTab">分类规则</button>
                        </li>
                        <li class="nav-item">
                            <button class="nav-link" data-bs-toggle="tab" data-bs-target="#aiTab">AI 与预警</button>
                        </li>
                    </ul>
                    <div class="tab-content">
                        <!-- 用户管理 -->
                        <div class="tab-pane fade show active" id="userTab">
                            <div class="row">
                                <div class="col-md-7">
                                    <h6>当前用户</h6>
                                    <div class="table-responsive">
                                        <table class="table table-sm table-hover align-middle">
                                            <thead><tr><th>用户名</th><th>操作</th></tr></thead>
                                            <tbody id="userListBody"></tbody>
                                        </table>
                                    </div>
                                </div>
                                <div class="col-md-5 border-start">
                                    <h6>添加新用户</h6>
                                    <form id="addUserForm">
                                        <input type="text" class="form-control form-control-sm mb-2" id="newUsername" placeholder="用户名" required>
                                        <input type="password" class="form-control form-control-sm mb-2" id="newUserPass" placeholder="密码" required>
                                        <button type="submit" class="btn btn-primary btn-sm w-100">添加</button>
                                    </form>
                                    <hr>
                                    <h6>重置用户密码</h6>
                                    <form id="resetPassForm">
                                        <select class="form-select form-select-sm mb-2" id="resetUserId"></select>
                                        <input type="password" class="form-control form-control-sm mb-2" id="resetNewPass" placeholder="新密码" required>
                                        <button type="submit" class="btn btn-warning btn-sm w-100 text-white">直接重置</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                        <!-- 分类规则 -->
                        <div class="tab-pane fade" id="categoryTab">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>分类列表</h6>
                                    <div id="categoryListContainer" class="list-group small"></div>
                                </div>
                                <div class="col-md-6 border-start">
                                    <h6>编辑/新增分类</h6>
                                    <form id="categoryForm">
                                        <input type="text" class="form-control form-control-sm mb-2" id="catName" placeholder="分类名称 (如: 小食品)" required>
                                        <select class="form-select form-select-sm mb-2" id="catType">
                                            <option value="snack">小食品 (提前下架+报废)</option>
                                            <option value="material">物料 (不需要提前下架)</option>
                                            <option value="coffee">咖啡豆 (提前下架+可赠送)</option>
                                        </select>
                                        <div class="form-check form-switch small mb-2">
                                            <input class="form-check-input" type="checkbox" id="catNeedBuffer" checked>
                                            <label class="form-check-label">启用提前下架缓冲</label>
                                        </div>
                                        <div class="form-check form-switch small mb-2">
                                            <input class="form-check-input" type="checkbox" id="catScrapOnRemoval">
                                            <label class="form-check-label">下架即报废</label>
                                        </div>
                                        <button type="submit" class="btn btn-success btn-sm w-100">保存分类</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                        <!-- AI 配置 -->
                        <div class="tab-pane fade" id="aiTab">
                            <form id="aiSettingsForm">
                                <h6 class="fw-bold mb-3 border-bottom pb-2">AI 模型配置</h6>
                                <div class="mb-3">
                                    <label class="form-label small">API 接口地址 (Base URL)</label>
                                    <input type="text" class="form-control" id="ai_api_url" placeholder="https://api.openai.com/v1">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small">API Key</label>
                                    <input type="password" class="form-control" id="ai_api_key">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small">模型名称 (Model)</label>
                                    <input type="text" class="form-control" id="ai_model" placeholder="gpt-4o">
                                </div>
                                <h6 class="fw-bold mb-3 mt-4 border-bottom pb-2">系统主动预警</h6>
                                <div class="mb-3">
                                    <label class="form-label small">预警接收邮箱 (留空禁用)</label>
                                    <input type="email" class="form-control" id="alert_email" placeholder="you@example.com">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small">预警阈值 (天，逗号分隔)</label>
                                    <input type="text" class="form-control" id="alert_days" placeholder="3,7,15">
                                </div>
                                <button type="submit" class="btn btn-success w-100">保存所有设置</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 提示消息容器 -->
    <div class="alert-container" id="alertContainer"></div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <script>
        // ========================================
        // 全局变量
        // ========================================
        let html5QrCode = null;
        let isScanning = false;
        
        // ========================================
        // 工具函数
        // ========================================
        
        /**
         * 显示提示消息
         * @param {string} message - 消息内容
         * @param {string} type - 消息类型 (success/danger/warning/info)
         */
        function showAlert(message, type = 'info') {
            const container = document.getElementById('alertContainer');
            
            // 图标映射
            const icons = {
                success: 'bi-check-circle',
                danger: 'bi-exclamation-triangle',
                warning: 'bi-exclamation-circle',
                info: 'bi-info-circle'
            };
            
            const alertHtml = `
                <div class="alert alert-${type} alert-dismissible fade show fade-in" role="alert">
                    <i class="bi ${icons[type]}"></i> ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', alertHtml);
            
            // 3秒后自动消失
            setTimeout(() => {
                const alerts = container.querySelectorAll('.alert');
                if (alerts.length > 0) {
                    alerts[0].remove();
                }
            }, 3000);
        }
        
        /**
         * 计算到期状态
         * @param {string} expiryDate - 到期日期 (YYYY-MM-DD)
         * @returns {object} - { status: 'expired'|'warning'|'normal', text: string, days: number }
         */
        function getExpiryStatus(expiryDate) {
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const expiry = new Date(expiryDate);
            expiry.setHours(0, 0, 0, 0);
            
            // 获取提前下架天数
            const buffer = parseInt(document.getElementById('removalBuffer')?.value) || 0;
            const removal = new Date(expiry);
            removal.setDate(removal.getDate() - buffer);
            
            const diffTime = removal - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays < 0) {
                return {
                    status: 'expired',
                    text: buffer > 0 ? `需下架 (原到期: ${expiryDate})` : `已过期 ${Math.abs(diffDays)} 天`,
                    class: 'expired',
                    badgeClass: 'expired'
                };
            } else if (diffDays <= 30) {
                return {
                    status: 'warning',
                    text: `${diffDays} 天后需下架`,
                    class: 'warning',
                    badgeClass: 'warning'
                };
            } else {
                return {
                    status: 'normal',
                    text: `${diffDays} 天后需下架`,
                    class: '',
                    badgeClass: 'normal'
                };
            }
        }
        
        /**
         * 格式化日期显示
         * @param {string} dateStr - 日期字符串 (YYYY-MM-DD)
         * @returns {string} - 格式化后的日期 (YYYY年MM月DD日)
         */
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
        }
        
        // ========================================
        // 统计功能
        // ========================================
        
        /**
         * 加载统计数据
         */
        async function loadStatistics() {
            try {
                const response = await fetch('index.php?api=get_statistics');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.statistics;
                    // 如果存在对应的 DOM 则填充
                    if (document.getElementById('val-expired')) {
                        document.getElementById('val-expired').textContent = stats.expired;
                    }
                }
            } catch (error) {
                console.error('加载统计数据失败:', error);
            }
        }
        
        // 页面加载时获取统计数据
        document.addEventListener('DOMContentLoaded', function() {
            // 检查版本更新
            checkUpgrade();

            // 如果已经登录，加载统计
            if (document.getElementById('startScanBtn')) {
                loadStatistics();
                refreshHealthDashboard();
            }
            
            // 刷新统计按钮
            if (document.getElementById('refreshStatsBtn')) {
                document.getElementById('refreshStatsBtn').addEventListener('click', function() {
                    loadStatistics();
                    refreshHealthDashboard();
                    showAlert('数据已更新', 'success');
                });
            }

            // 导出盘点表按钮
            if (document.getElementById('exportBtn')) {
                document.getElementById('exportBtn').addEventListener('click', function() {
                    window.location.href = 'index.php?api=export_inventory';
                    showAlert('正在生成 AI 整理的盘点表...', 'info');
                });
            }

            // 登录处理
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('loginUser').value;
                    const password = document.getElementById('loginPass').value;
                    const resp = await fetch('index.php?api=login', {
                        method: 'POST',
                        body: JSON.stringify({ username, password })
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showAlert('登录成功，欢迎回来', 'success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showAlert(data.message, 'danger');
                    }
                });
            }

            // 登出处理
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', async () => {
                    await fetch('index.php?api=logout');
                    location.reload();
                });
            }

            // 设置相关初始化
            const settingsBtn = document.getElementById('settingsBtn');
            if (settingsBtn) {
                settingsBtn.addEventListener('click', () => {
                    loadUserList();
                    loadAISettings();
                    loadCategories();
                });
            }

            // 分类表单处理
            const categoryForm = document.getElementById('categoryForm');
            if (categoryForm) {
                categoryForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const name = document.getElementById('catName').value;
                    const type = document.getElementById('catType').value;
                    const rule = JSON.stringify({
                        need_buffer: document.getElementById('catNeedBuffer').checked,
                        scrap_on_removal: document.getElementById('catScrapOnRemoval').checked
                    });
                    const resp = await fetch('index.php?api=save_category', {
                        method: 'POST',
                        body: JSON.stringify({ name, type, rule })
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showAlert(data.message, 'success');
                        loadCategories();
                        categoryForm.reset();
                    }
                });
            }

            // 添加用户处理
            const addUserForm = document.getElementById('addUserForm');
            if (addUserForm) {
                addUserForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('newUsername').value;
                    const password = document.getElementById('newUserPass').value;
                    const resp = await fetch('index.php?api=add_user', {
                        method: 'POST',
                        body: JSON.stringify({ username, password })
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showAlert(data.message, 'success');
                        addUserForm.reset();
                        loadUserList();
                    } else {
                        showAlert(data.message, 'danger');
                    }
                });
            }

            // 重置密码处理
            const resetPassForm = document.getElementById('resetPassForm');
            if (resetPassForm) {
                resetPassForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const user_id = document.getElementById('resetUserId').value;
                    const new_password = document.getElementById('resetNewPass').value;
                    const resp = await fetch('index.php?api=reset_password', {
                        method: 'POST',
                        body: JSON.stringify({ user_id, new_password })
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showAlert(data.message, 'success');
                        resetPassForm.reset();
                    } else {
                        showAlert(data.message, 'danger');
                    }
                });
            }

            // AI 设置处理
            const aiSettingsForm = document.getElementById('aiSettingsForm');
            if (aiSettingsForm) {
                aiSettingsForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const ai_api_url = document.getElementById('ai_api_url').value;
                    const ai_api_key = document.getElementById('ai_api_key').value;
                    const ai_model = document.getElementById('ai_model').value;
                    const alert_email = document.getElementById('alert_email').value;
                    const alert_days = document.getElementById('alert_days').value;
                    const resp = await fetch('index.php?api=save_settings', {
                        method: 'POST',
                        body: JSON.stringify({ ai_api_url, ai_api_key, ai_model, alert_email, alert_days })
                    });
                    const data = await resp.json();
                    if (data.success) {
                        showAlert(data.message, 'success');
                    } else {
                        showAlert(data.message, 'danger');
                    }
                });
            }
        });

        async function refreshHealthDashboard() {
            const resp = await fetch('index.php?api=get_health_report');
            const data = await resp.json();
            if (data.success) {
                const r = data.report;
                const total = parseInt(r.expired) + parseInt(r.urgent) + parseInt(r.warning) + parseInt(r.healthy);
                if (total > 0) {
                    document.getElementById('bar-expired').style.width = (r.expired / total * 100) + '%';
                    document.getElementById('bar-urgent').style.width = ((parseInt(r.urgent) + parseInt(r.warning)) / total * 100) + '%';
                    document.getElementById('bar-healthy').style.width = (r.healthy / total * 100) + '%';
                }
                document.getElementById('val-expired').innerText = r.expired || 0;
                document.getElementById('val-urgent').innerText = (parseInt(r.urgent) + parseInt(r.warning)) || 0;
                document.getElementById('val-healthy').innerText = r.healthy || 0;
            }
        }

        async function loadUserList() {
            const resp = await fetch('index.php?api=get_users');
            const data = await resp.json();
            if (data.success) {
                const tbody = document.getElementById('userListBody');
                const select = document.getElementById('resetUserId');
                tbody.innerHTML = '';
                select.innerHTML = '';
                data.users.forEach(u => {
                    tbody.innerHTML += `<tr><td>${u.username}</td><td><span class="badge bg-secondary">管理</span></td></tr>`;
                    select.innerHTML += `<option value="${u.id}">${u.username}</option>`;
                });
            }
        }

        async function loadAISettings() {
            const resp = await fetch('index.php?api=get_settings');
            const data = await resp.json();
            if (data.success) {
                document.getElementById('ai_api_url').value = data.settings.ai_api_url;
                document.getElementById('ai_api_key').value = data.settings.ai_api_key;
                document.getElementById('ai_model').value = data.settings.ai_model;
                document.getElementById('alert_email').value = data.settings.alert_email;
                document.getElementById('alert_days').value = data.settings.alert_days;
            }
        }

        async function loadCategories() {
            const resp = await fetch('index.php?api=get_categories');
            const data = await resp.json();
            if (data.success) {
                // 更新分类列表
                const container = document.getElementById('categoryListContainer');
                container.innerHTML = data.categories.map(c => `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        ${c.name} <span class="badge bg-info">${c.type}</span>
                    </div>
                `).join('');

                // 更新商品录入页面的下拉框
                const select = document.getElementById('categoryId');
                if (select) {
                    select.innerHTML = '<option value="0">选择分类</option>' + 
                        data.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
                }
            }
        }

        // ========================================
        // 扫码功能 (UI 优化版)
        // ========================================
        
        /**
         * 启动全屏扫码
         */
        document.getElementById('startScanBtn')?.addEventListener('click', async function() {
            const overlay = document.getElementById('scanOverlay');
            overlay.style.display = 'flex';
            
            try {
                if (!html5QrCode) {
                    html5QrCode = new Html5Qrcode("reader");
                }
                
                const config = {
                    fps: 15,
                    qrbox: { width: 280, height: 200 }, // 矩形框适合条形码
                    aspectRatio: 1.0
                };
                
                await html5QrCode.start(
                    { facingMode: "environment" },
                    config,
                    onScanSuccess,
                    onScanError
                );
                
                isScanning = true;
                
            } catch (err) {
                showAlert('无法启动摄像头: ' + err, 'danger');
                hideScanOverlay();
            }
        });
        
        /**
         * 停止并隐藏扫码
         */
        document.getElementById('stopScanBtn')?.addEventListener('click', hideScanOverlay);
        
        function hideScanOverlay() {
            const overlay = document.getElementById('scanOverlay');
            if (html5QrCode && isScanning) {
                html5QrCode.stop().then(() => {
                    overlay.style.display = 'none';
                    isScanning = false;
                }).catch(err => {
                    console.error('停止扫描失败:', err);
                    overlay.style.display = 'none';
                });
            } else {
                overlay.style.display = 'none';
            }
        }
        
        /**
         * 扫码成功回调
         */
        function onScanSuccess(decodedText, decodedResult) {
            // 填充 SKU
            document.getElementById('sku').value = decodedText;
            
            // 播放提示音
            playBeep();
            
            // 停止扫描
            hideScanOverlay();
            
            // 自动查询商品
            searchProduct(decodedText);
            
            showAlert(`扫码成功: ${decodedText}`, 'success');
        }
        
        /**
         * 扫码错误回调（静默处理）
         */
        function onScanError(error) {
            // 静默处理
        }
        
        /**
         * 播放提示音 (叮~)
         */
        function playBeep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                // 第一个频率：短促清脆
                const osc1 = audioCtx.createOscillator();
                const gain1 = audioCtx.createGain();
                osc1.type = 'sine';
                osc1.frequency.setValueAtTime(1200, audioCtx.currentTime);
                gain1.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain1.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                
                osc1.connect(gain1);
                gain1.connect(audioCtx.destination);
                
                osc1.start();
                osc1.stop(audioCtx.currentTime + 0.1);

                // 第二个频率：略高的尾音
                setTimeout(() => {
                    const osc2 = audioCtx.createOscillator();
                    const gain2 = audioCtx.createGain();
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(1600, audioCtx.currentTime);
                    gain2.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                    
                    osc2.connect(gain2);
                    gain2.connect(audioCtx.destination);
                    
                    osc2.start();
                    osc2.stop(audioCtx.currentTime + 0.2);
                }, 50);

            } catch (e) {
                console.warn('播放音效失败:', e);
            }
        }
        
        // ========================================
        // 升级功能
        // ========================================
        
        /**
         * 检查更新
         */
        async function checkUpgrade() {
            try {
                const response = await fetch('index.php?api=check_upgrade');
                const data = await response.json();
                
                if (data.success && data.has_update) {
                    const upgradeBtn = document.getElementById('upgradeBtn');
                    upgradeBtn.classList.remove('d-none');
                    upgradeBtn.innerHTML = `<i class="bi bi-cloud-arrow-up"></i> 升级到 ${data.latest}`;
                    
                    upgradeBtn.onclick = async () => {
                        if (confirm(`确定要从 ${data.current} 升级到 ${data.latest} 吗？\n系统将自动从 GitHub 下载最新代码覆盖本地文件。`)) {
                            upgradeBtn.disabled = true;
                            upgradeBtn.innerHTML = `<i class="bi bi-hourglass-split"></i> 升级中...`;
                            
                            const execResp = await fetch('index.php?api=execute_upgrade');
                            const execData = await execResp.json();
                            
                            if (execData.success) {
                                showAlert(execData.message, 'success');
                                setTimeout(() => window.location.reload(), 1500);
                            } else {
                                showAlert('升级失败: ' + execData.message, 'danger');
                                upgradeBtn.disabled = false;
                            }
                        }
                    };
                }
            } catch (error) {
                console.log('检查更新失败');
            }
        }

        // ========================================
        // 商品查询功能
        // ========================================
        
        /**
         * 手动查询按钮
         */
        document.getElementById('manualSearchBtn')?.addEventListener('click', function() {
            const sku = document.getElementById('manualSku').value.trim();
            if (sku) {
                document.getElementById('sku').value = sku;
                searchProduct(sku);
            } else {
                showAlert('请输入 SKU', 'warning');
            }
        });
        
        /**
         * 根据 SKU 查询商品信息
         * @param {string} sku - 商品 SKU
         */
        async function searchProduct(sku) {
            sku = sku || document.getElementById('sku').value.trim();
            
            if (!sku) {
                showAlert('请输入或扫描 SKU', 'warning');
                return;
            }
            
            try {
                showAlert('正在查询...', 'info');
                
                const response = await fetch(`index.php?api=get_product&sku=${encodeURIComponent(sku)}`);
                const data = await response.json();
                
                if (data.success) {
                    if (data.exists) {
                        // 商品存在，回显信息
                        document.getElementById('productName').value = data.product.name;
                        document.getElementById('categoryId').value = data.product.category_id || 0;
                        document.getElementById('removalBuffer').value = data.product.removal_buffer || 0;
                        
                        // 显示已有批次
                        displayBatches(data.batches);
                        
                        showAlert(`已加载商品: ${data.product.name}`, 'success');
                    } else {
                        // 商品不存在，准备新建
                        document.getElementById('productName').value = '';
                        document.getElementById('categoryId').value = 0;
                        document.getElementById('removalBuffer').value = 0;
                        clearBatches();
                        addBatchRow();
                        
                        showAlert('新商品，请输入商品名称', 'info');
                    }
                } else {
                    showAlert(data.message || '查询失败', 'danger');
                }
            } catch (error) {
                showAlert('网络错误: ' + error.message, 'danger');
            }
        }
        
        // ========================================
        // 批次管理功能
        // ========================================
        
        /**
         * 添加批次按钮
         */
        document.getElementById('addBatchBtn')?.addEventListener('click', function() {
            addBatchRow();
            showAlert('已添加新批次行', 'info');
        });
        
        /**
         * 添加批次行
         * @param {object} batchData - 批次数据
         */
        function addBatchRow(batchData = null) {
            const container = document.getElementById('batchesContainer');
            if (!container) return;

            const batchIndex = container.children.length + 1;
            const today = new Date().toISOString().split('T')[0];
            const expiryDate = batchData ? batchData.expiry_date : today;
            const quantity = batchData ? batchData.quantity : '';
            const expiryStatus = batchData ? getExpiryStatus(expiryDate) : getExpiryStatus(today);
            const statusClass = batchData ? expiryStatus.class : '';
            const statusText = batchData ? (batchData.ai_status || expiryStatus.text) : '新批次';
            
            const batchHtml = `
                <div class="batch-item ${statusClass} fade-in" data-batch-id="${batchData ? batchData.id : ''}">
                    <div class="row g-2">
                        <div class="col-6">
                            <label class="form-label small text-muted">到期时间</label>
                            <input type="date" class="form-control expiry-date-input" value="${expiryDate}" required>
                        </div>
                        <div class="col-4">
                            <label class="form-label small text-muted">数量</label>
                            <input type="number" class="form-control quantity-input" value="${quantity}" min="0" placeholder="0" required>
                        </div>
                        <div class="col-2">
                            <label class="form-label small">&nbsp;</label>
                            <button type="button" class="btn btn-outline-danger w-100 remove-batch-btn border-0">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                    <div class="mt-2 small d-flex justify-content-between">
                        <span class="status-badge ${expiryStatus.badgeClass}">${statusText}</span>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', batchHtml);
            
            const newBatch = container.lastElementChild;
            newBatch.querySelector('.remove-batch-btn').addEventListener('click', function() {
                if (container.children.length > 1) {
                    newBatch.remove();
                } else {
                    showAlert('至少保留一个批次', 'warning');
                }
            });
            
            const dateInput = newBatch.querySelector('.expiry-date-input');
            dateInput.addEventListener('change', function() {
                updateBatchStatus(newBatch, this.value);
            });
        }
        
        /**
         * 更新批次状态显示
         */
        function updateBatchStatus(batchElement, expiryDate) {
            const status = getExpiryStatus(expiryDate);
            batchElement.classList.remove('expired', 'warning');
            if (status.class) batchElement.classList.add(status.class);
            
            let statusBadge = batchElement.querySelector('.status-badge');
            if (statusBadge) {
                statusBadge.className = `status-badge ${status.badgeClass}`;
                statusBadge.textContent = status.text;
            }
        }
        
        /**
         * 显示批次列表
         */
        function displayBatches(batches) {
            const container = document.getElementById('batchesContainer');
            if (!container) return;
            container.innerHTML = '';
            
            if (batches && batches.length > 0) {
                batches.forEach(batch => addBatchRow(batch));
            } else {
                addBatchRow();
            }
        }
        
        /**
         * 清空批次列表
         */
        function clearBatches() {
            const container = document.getElementById('batchesContainer');
            if (container) container.innerHTML = '';
        }
        
        // ========================================
        // 表单提交功能
        // ========================================
        
        /**
         * 表单提交事件
         */
        document.getElementById('productForm')?.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const sku = document.getElementById('sku').value.trim();
            const name = document.getElementById('productName').value.trim();
            const category_id = document.getElementById('categoryId').value;
            const removal_buffer = parseInt(document.getElementById('removalBuffer').value) || 0;
            
            const batches = [];
            document.querySelectorAll('.batch-item').forEach(item => {
                const expiryDate = item.querySelector('.expiry-date-input').value;
                const quantity = parseInt(item.querySelector('.quantity-input').value) || 0;
                if (expiryDate && quantity >= 0) {
                    batches.push({ expiry_date: expiryDate, quantity: quantity });
                }
            });
            
            if (batches.length === 0) {
                showAlert('请至少添加一个有效批次', 'warning');
                return;
            }
            
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            
            try {
                const response = await fetch('index.php?api=save_product', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sku, name, category_id, removal_buffer, batches
                    })
                });
                
                const data = await response.json();
                if (data.success) {
                    showAlert('保存成功', 'success');
                    loadStatistics();
                    refreshHealthDashboard();
                    searchProduct(sku);
                } else {
                    showAlert(data.message, 'danger');
                }
            } catch (error) {
                showAlert('网络错误', 'danger');
            } finally {
                submitBtn.disabled = false;
            }
        });
        
        /**
         * 重置表单
         */
        document.getElementById('resetFormBtn')?.addEventListener('click', function() {
            document.getElementById('productForm').reset();
            clearBatches();
            addBatchRow();
        });

        // 监听提前下架天数变化
        document.getElementById('removalBuffer')?.addEventListener('input', function() {
            document.querySelectorAll('.batch-item').forEach(item => {
                const dateInput = item.querySelector('.expiry-date-input');
                if (dateInput && dateInput.value) updateBatchStatus(item, dateInput.value);
            });
        });

    </script>
</body>
</html>
