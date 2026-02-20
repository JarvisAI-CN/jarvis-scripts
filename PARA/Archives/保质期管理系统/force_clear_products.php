<?php
/**
 * 检查并清空所有商品相关数据
 */
require_once 'db.php';

$conn = getDBConnection();
if (!$conn) {
    die("数据库连接失败\n");
}

echo "=== 检查数据库状态 ===\n\n";

// 检查各表的数据量
$tables = ['products', 'batches', 'sku_todos', 'categories'];
foreach ($tables as $table) {
    $res = $conn->query("SELECT COUNT(*) as cnt FROM $table");
    $row = $res->fetch_assoc();
    echo "$table 表: {$row['cnt']} 条记录\n";
}

echo "\n=== 开始清空 ===\n\n";

// 清空products表
echo "1. 清空 products 表...\n";
$conn->query("DELETE FROM products");
echo "   删除了 {$conn->affected_rows} 条记录\n";

// 清空batches表
echo "2. 清空 batches 表...\n";
$conn->query("DELETE FROM batches");
echo "   删除了 {$conn->affected_rows} 条记录\n";

// 清空sku_todos表
echo "3. 清空 sku_todos 表...\n";
$conn->query("DELETE FROM sku_todos");
echo "   删除了 {$conn->affected_rows} 条记录\n";

// 重置自增ID
echo "\n4. 重置自增ID...\n";
$conn->query("ALTER TABLE products AUTO_INCREMENT = 1");
$conn->query("ALTER TABLE batches AUTO_INCREMENT = 1");
$conn->query("ALTER TABLE sku_todos AUTO_INCREMENT = 1");
echo "   完成\n";

echo "\n✅ 清空完成！\n";
?>
