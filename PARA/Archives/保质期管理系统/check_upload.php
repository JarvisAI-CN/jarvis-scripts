<?php
require_once 'db.php';
$conn = getDBConnection();

echo "=== 检查数据导入状态 ===\n\n";

// 检查sku_todos表
$res = $conn->query("SELECT COUNT(*) as cnt FROM sku_todos");
$row = $res->fetch_assoc();
echo "sku_todos表: {$row['cnt']} 条记录\n";

if ($row['cnt'] > 0) {
    echo "\n前5条数据:\n";
    $res = $conn->query("SELECT id, sku, name, category_name, status FROM sku_todos LIMIT 5");
    while ($row = $res->fetch_assoc()) {
        echo "  SKU: {$row['sku']}, 名称: {$row['name']}, 公司分类: {$row['category_name']}, 状态: {$row['status']}\n";
    }
    
    // 检查有多少不同的公司分类
    echo "\n公司分类列表:\n";
    $res = $conn->query("SELECT DISTINCT category_name FROM sku_todos WHERE category_name IS NOT NULL AND category_name != '' ORDER BY category_name");
    while ($row = $res->fetch_assoc()) {
        echo "  - {$row['category_name']}\n";
    }
} else {
    echo "（表为空，数据可能还在处理中）\n";
}
?>
