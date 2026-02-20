<?php
require_once 'db.php';
$conn = getDBConnection();

echo "=== 检查products表中的SKU数据 ===\n\n";

// 检查products表
$res = $conn->query("SELECT id, sku, name FROM products LIMIT 10");
$count = $res->num_rows;
echo "products表: $count 条记录\n\n";

if ($count > 0) {
    echo "前10条记录:\n";
    echo str_pad("ID", 5) . str_pad("SKU", 15) . "商品名称\n";
    echo str_repeat("-", 80) . "\n";
    while ($row = $res->fetch_assoc()) {
        echo str_pad($row['id'], 5) . str_pad($row['sku'], 15) . $row['name'] . "\n";
    }
}

echo "\n=== 查询SKU: 11179798 ===\n";
$stmt = $conn->prepare("SELECT * FROM products WHERE sku = ?");
$test_sku = "11179798";
$stmt->bind_param("s", $test_sku);
$stmt->execute();
$result = $stmt->get_result();
echo "找到: " . $result->num_rows . " 条记录\n";

if ($row = $result->fetch_assoc()) {
    echo "ID: {$row['id']}, SKU: {$row['sku']}, 名称: {$row['name']}\n";
}

echo "\n=== 查询SKU: 0011179798 ===\n";
$stmt = $conn->prepare("SELECT * FROM products WHERE sku = ?");
$test_sku2 = "0011179798";
$stmt->bind_param("s", $test_sku2);
$stmt->execute();
$result2 = $stmt->get_result();
echo "找到: " . $result2->num_rows . " 条记录\n";

if ($row = $result2->fetch_assoc()) {
    echo "ID: {$row['id']}, SKU: {$row['sku']}, 名称: {$row['name']}\n";
}

echo "\n=== 查询SKU: 001117979820251124#20251124#20260523 ===\n";
$stmt = $conn->prepare("SELECT * FROM products WHERE sku = ?");
$test_sku3 = "001117979820251124#20251124#20260523";
$stmt->bind_param("s", $test_sku3);
$stmt->execute();
$result3 = $stmt->get_result();
echo "找到: " . $result3->num_rows . " 条记录\n";

if ($row = $result3->fetch_assoc()) {
    echo "ID: {$row['id']}, SKU: {$row['sku']}, 名称: {$row['name']}\n";
}
?>
