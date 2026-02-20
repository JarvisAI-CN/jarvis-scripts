<?php
/**
 * 清空产品数据（保留测试用）
 */
require_once 'db.php';

$conn = getDBConnection();
if (!$conn) {
    die("数据库连接失败\n");
}

echo "开始清理数据...\n";

// 1. 清空products表
echo "1. 清空产品表 (products)...\n";
$conn->query("DELETE FROM products");
$affected = $conn->affected_rows;
echo "   已删除 $affected 条产品记录\n";

// 2. 清空batches表
echo "2. 清空批次表 (batches)...\n";
$conn->query("DELETE FROM batches");
$affected = $conn->affected_rows;
echo "   已删除 $affected 条批次记录\n";

// 3. 清空sku_todos表
echo "3. 清空SKU待办表 (sku_todos)...\n";
$conn->query("DELETE FROM sku_todos");
$affected = $conn->affected_rows;
echo "   已删除 $affected 条待办记录\n";

// 4. 清空sku_upload_tasks表
echo "4. 清空上传任务表 (sku_upload_tasks)...\n";
$conn->query("DELETE FROM sku_upload_tasks");
$affected = $conn->affected_rows;
echo "   已删除 $affected 条上传记录\n";

// 5. 重置自增ID
echo "5. 重置自增ID...\n";
$conn->query("ALTER TABLE products AUTO_INCREMENT = 1");
$conn->query("ALTER TABLE batches AUTO_INCREMENT = 1");
$conn->query("ALTER TABLE sku_todos AUTO_INCREMENT = 1");
$conn->query("ALTER TABLE sku_upload_tasks AUTO_INCREMENT = 1");
echo "   ID已重置\n";

echo "\n✅ 清理完成！\n";
echo "现在可以重新导入SKU数据了！\n";
?>
