<?php
/**
 * 保质期管理系统 - v4.0.0 系统概览API
 * 获取系统统计数据
 */

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 设置响应头
header('Content-Type: application/json; charset=utf-8');

// 检查权限
requireAuth('user');

try {
    $db = getDB();
    
    // 获取总商品数
    $totalProducts = $db->fetchOne("SELECT COUNT(*) as count FROM " . TABLE_PREFIX . "products");
    
    // 获取总盘点数
    $totalInventories = $db->fetchOne("SELECT COUNT(*) as count FROM " . TABLE_PREFIX . "inventory_sessions");
    
    // 获取已过期商品数
    $expiredProducts = $db->fetchOne("
        SELECT COUNT(DISTINCT ie.product_id) as count
        FROM " . TABLE_PREFIX . "inventory_entries ie
        JOIN " . TABLE_PREFIX . "batches b ON b.product_id = ie.product_id
        WHERE b.expiry_date < CURDATE()
    ");
    
    // 获取库存总金额（模拟数据）
    $totalValue = 0;
    
    // 返回结果
    echo json_encode([
        'success' => true,
        'data' => [
            'totalProducts' => $totalProducts['count'] ?? 0,
            'totalInventories' => $totalInventories['count'] ?? 0,
            'expiredProducts' => $expiredProducts['count'] ?? 0,
            'totalValue' => $totalValue
        ]
    ], JSON_UNESCAPED_UNICODE);
    
} catch (Exception $e) {
    logger('error', '获取系统概览失败: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'message' => '获取系统概览失败'
    ], JSON_UNESCAPED_UNICODE);
}

exit;
