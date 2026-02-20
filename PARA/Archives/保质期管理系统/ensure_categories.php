<?php
require_once 'db.php';
$conn = getDBConnection();

echo "=== 检查分类数据 ===\n\n";

// 检查categories表
$res = $conn->query("SELECT * FROM categories");
$count = $res->num_rows;
echo "categories表: $count 条记录\n";

if ($count > 0) {
    echo "\n现有分类:\n";
    while ($row = $res->fetch_assoc()) {
        echo "  ID: {$row['id']}, 名称: {$row['name']}, 类型: {$row['type']}\n";
    }
} else {
    echo "\n⚠️ 分类表为空！\n";
    echo "正在添加默认分类...\n";
    
    // 添加默认分类
    $categories = [
        ['咖啡豆', 'coffee', '{"need_buffer":true, "scrap_on_removal":false, "allow_gift":true}'],
        ['小食品', 'snack', '{"need_buffer":true, "scrap_on_removal":true}'],
        ['物料', 'material', '{"need_buffer":false, "scrap_on_removal":false}'],
        ['乳制品', 'dairy', '{"need_buffer":true, "scrap_on_removal":false}'],
        ['包装材料', 'packaging', '{"need_buffer":false, "scrap_on_removal":false}'],
        ['饮品', 'beverage', '{"need_buffer":true, "scrap_on_removal":false}']
    ];
    
    $stmt = $conn->prepare("INSERT INTO categories (name, type, rule) VALUES (?, ?, ?)");
    foreach ($categories as $cat) {
        $stmt->bind_param("sss", $cat[0], $cat[1], $cat[2]);
        $stmt->execute();
        echo "  ✅ 已添加: {$cat[0]}\n";
    }
}

echo "\n✅ 完成！\n";
?>
