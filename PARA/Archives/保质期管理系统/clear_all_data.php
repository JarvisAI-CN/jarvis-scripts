<?php
/**
 * 彻底清空保质期管理系统所有数据
 */
require_once 'db.php';

$conn = getDBConnection();
if (!$conn) {
    die("数据库连接失败\n");
}

echo "=== 彻底清空所有数据 ===\n\n";

// 开始事务
$conn->begin_transaction();

try {
    // 1. 清空batches表（批次记录）
    echo "1. 清空批次表 (batches)...\n";
    $conn->query("DELETE FROM batches");
    $affected = $conn->affected_rows;
    echo "   已删除 $affected 条批次记录\n";

    // 2. 清空products表（商品记录）
    echo "2. 清空商品表 (products)...\n";
    $conn->query("DELETE FROM products");
    $affected = $conn->affected_rows;
    echo "   已删除 $affected 条商品记录\n";

    // 3. 清空sku_todos表（SKU待办）
    echo "3. 清空SKU待办表 (sku_todos)...\n";
    $conn->query("DELETE FROM sku_todos");
    $affected = $conn->affected_rows;
    echo "   已删除 $affected 条待办记录\n";

    // 4. 清空sku_upload_tasks表（上传任务）
    echo "4. 清空上传任务表 (sku_upload_tasks)...\n";
    $conn->query("DELETE FROM sku_upload_tasks");
    $affected = $conn->affected_rows;
    echo "   已删除 $affected 条上传记录\n";

    // 5. 重置所有自增ID
    echo "5. 重置自增ID...\n";
    $conn->query("ALTER TABLE products AUTO_INCREMENT = 1");
    $conn->query("ALTER TABLE batches AUTO_INCREMENT = 1");
    $conn->query("ALTER TABLE sku_todos AUTO_INCREMENT = 1");
    $conn->query("ALTER TABLE sku_upload_tasks AUTO_INCREMENT = 1");
    echo "   ID已重置\n";

    // 提交事务
    $conn->commit();

    echo "\n✅ 所有数据已彻底清空！\n";
    echo "系统现在处于全新状态。\n";

} catch (Exception $e) {
    $conn->rollback();
    echo "\n❌ 清空失败: " . $e->getMessage() . "\n";
}
?>
