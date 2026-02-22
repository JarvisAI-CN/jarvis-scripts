<?php
/**
 * 提交盘点数据 API
 * 将扫描的商品数据保存到数据库
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 设置响应头
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');

// 检查用户是否登录
if (!checkAuth()) {
    echo json_encode([
        'success' => false,
        'message' => '用户未登录'
    ]);
    exit;
}

// 检查请求方法
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode([
        'success' => false,
        'message' => '只支持 POST 请求'
    ]);
    exit;
}

// 获取请求数据
$data = json_decode(file_get_contents('php://input'), true);

// 验证数据
if (empty($data['products']) || !is_array($data['products'])) {
    echo json_encode([
        'success' => false,
        'message' => '商品列表不能为空'
    ]);
    exit;
}

$products = $data['products'];
$notes = $data['notes'] ?? '手动盘点';

try {
    // 初始化数据库连接
    $db = getDB();
    
    // 开始事务
    $db->beginTransaction();
    
    // 创建盘点会话
    $sessionKey = generateSessionKey();
    $userId = getCurrentUserId();
    
    $stmt = $db->prepare("
        INSERT INTO pd_inventory_sessions (
            session_key, user_id, item_count, notes, status, created_at, updated_at
        ) VALUES (?, ?, ?, ?, 'completed', NOW(), NOW())
    ");
    
    $stmt->execute([$sessionKey, $userId, count($products)]);
    $sessionId = $db->lastInsertId();
    
    // 插入盘点条目
    $entryStmt = $db->prepare("
        INSERT INTO pd_inventory_entries (
            session_id, product_id, sku, product_name, quantity, batches, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, NOW(), NOW())
    ");
    
    foreach ($products as $product) {
        // 查找商品ID
        $productStmt = $db->prepare("SELECT id FROM pd_products WHERE sku = ?");
        $productStmt->execute([$product['sku']]);
        $productData = $productStmt->fetch(PDO::FETCH_ASSOC);
        
        $productId = $productData['id'] ?? null;
        
        // 插入条目
        $entryStmt->execute([
            $sessionId,
            $productId,
            $product['sku'],
            $product['productName'],
            $product['quantity'],
            json_encode([]) // 批次信息，暂时为空
        ]);
    }
    
    // 提交事务
    $db->commit();
    
    // 返回成功响应
    echo json_encode([
        'success' => true,
        'message' => '盘点数据提交成功',
        'session_key' => $sessionKey,
        'item_count' => count($products)
    ]);
    
} catch (PDOException $e) {
    // 数据库错误，回滚事务
    if (isset($db) && $db->inTransaction()) {
        $db->rollBack();
    }
    
    error_log('提交盘点数据失败: ' . $e->getMessage());
    echo json_encode([
        'success' => false,
        'message' => '数据库操作失败: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    // 其他异常
    error_log('提交盘点数据异常: ' . $e->getMessage());
    echo json_encode([
        'success' => false,
        'message' => '服务器错误: ' . $e->getMessage()
    ]);
}
