<?php
require_once 'db.php';
$conn = getDBConnection();

echo "=== 检查商品数据 ===\n\n";

// 检查products表
$res = $conn->query("SELECT COUNT(*) as cnt FROM products");
$row = $res->fetch_assoc();
echo "products表记录数: {$row['cnt']}\n";

if ($row['cnt'] > 0) {
    echo "\n前5条商品:\n";
    $res = $conn->query("SELECT id, sku, name FROM products LIMIT 5");
    while ($row = $res->fetch_assoc()) {
        echo "  ID: {$row['id']}, SKU: {$row['sku']}, 名称: {$row['name']}\n";
    }
    echo "\n正在删除...\n";
    $conn->query("DELETE FROM products");
    echo "已删除 {$conn->affected_rows} 条记录\n";
    $conn->query("ALTER TABLE products AUTO_INCREMENT = 1");
    echo "ID已重置\n";
} else {
    echo "products表为空\n";
}

echo "\n=== 检查batches表 ===\n";
$res = $conn->query("SELECT COUNT(*) as cnt FROM batches");
$row = $res->fetch_assoc();
echo "batches表记录数: {$row['cnt']}\n";
if ($row['cnt'] > 0) {
    $conn->query("DELETE FROM batches");
    echo "已删除 {$conn->affected_rows} 条批次记录\n";
}

echo "\n✅ 完成！\n";
?>
