<?php
/**
 * 获取商品信息 API
 * 根据 SKU 查询商品信息
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/db.php';
require_once __DIR__ . '/../includes/functions.php';

// 设置响应头
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');

// 获取参数
$sku = trim($_GET['sku'] ?? '');

// 验证参数
if (empty($sku)) {
    echo json_encode([
        'success' => false,
        'message' => 'SKU 参数不能为空',
        'exists' => false
    ]);
    exit;
}

try {
    // 初始化数据库连接
    $db = getDB();
    
    // 查询商品信息
    $stmt = $db->prepare("
        SELECT 
            id, sku, name, category_id, unit, removal_buffer, description, 
            created_at, updated_at
        FROM pd_products 
        WHERE sku = ?
    ");
    
    $stmt->execute([$sku]);
    $product = $stmt->fetch(PDO::FETCH_ASSOC);
    
    if ($product) {
        // 商品存在
        echo json_encode([
            'success' => true,
            'exists' => true,
            'product' => [
                'id' => (int)$product['id'],
                'sku' => $product['sku'],
                'name' => $product['name'],
                'category_id' => (int)$product['category_id'],
                'unit' => $product['unit'],
                'removal_buffer' => (int)$product['removal_buffer'],
                'description' => $product['description'],
                'created_at' => $product['created_at'],
                'updated_at' => $product['updated_at']
            ],
            'message' => '商品查询成功'
        ]);
    } else {
        // 商品不存在
        echo json_encode([
            'success' => true,
            'exists' => false,
            'product' => null,
            'message' => '商品不存在'
        ]);
    }
    
} catch (PDOException $e) {
    // 数据库查询失败
    error_log('获取商品信息失败: ' . $e->getMessage());
    echo json_encode([
        'success' => false,
        'exists' => false,
        'message' => '数据库查询失败: ' . $e->getMessage()
    ]);
} catch (Exception $e) {
    // 其他异常
    error_log('获取商品信息异常: ' . $e->getMessage());
    echo json_encode([
        'success' => false,
        'exists' => false,
        'message' => '服务器错误: ' . $e->getMessage()
    ]);
}
