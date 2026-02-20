<?php
require_once 'db.php';
$conn = getDBConnection();

if (!$conn) {
    die("数据库连接失败\n");
}

echo "=== 数据库信息 ===\n";
echo "数据库: " . DB_NAME . "\n";
echo "主机: " . DB_HOST . "\n\n";

echo "=== 各表记录数 ===\n";
$tables = ['products', 'batches', 'sku_todos', 'categories'];
foreach ($tables as $table) {
    $res = $conn->query("SELECT COUNT(*) as cnt FROM $table");
    $row = $res->fetch_assoc();
    echo "$table: {$row['cnt']} 条\n";
}

echo "\n=== products 表前3条 ===\n";
$res = $conn->query("SELECT * FROM products LIMIT 3");
if ($res && $res->num_rows > 0) {
    while ($row = $res->fetch_assoc()) {
        echo "SKU: {$row['sku']}, 名称: {$row['name']}\n";
    }
} else {
    echo "（空表）\n";
}
?>
