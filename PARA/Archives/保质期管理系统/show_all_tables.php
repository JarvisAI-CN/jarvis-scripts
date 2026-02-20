<?php
require_once 'db.php';
$conn = getDBConnection();

// 显示所有表
$res = $conn->query("SHOW TABLES");
echo "=== 数据库中的所有表 ===\n\n";
while ($row = $res->fetch_array()) {
    $table = $row[0];
    $count_res = $conn->query("SELECT COUNT(*) as cnt FROM `$table`");
    $count_row = $count_res->fetch_assoc();
    echo sprintf("%-30s %5d 条记录\n", $table, $count_row['cnt']);
}

// 检查是否有商品相关的其他表
echo "\n=== 检查是否有商品数据 ===\n";
$possible_tables = ['products', 'goods', 'items', 'inventory', 'stock'];
foreach ($possible_tables as $table) {
    $res = $conn->query("SHOW TABLES LIKE '$table'");
    if ($res->num_rows > 0) {
        $count_res = $conn->query("SELECT COUNT(*) as cnt FROM `$table`");
        $count_row = $count_res->fetch_assoc();
        if ($count_row['cnt'] > 0) {
            echo "$table 表有 {$count_row['cnt']} 条数据！\n";
        }
    }
}
?>
