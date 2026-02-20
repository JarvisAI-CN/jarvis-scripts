<?php
require_once 'db.php';
$conn = getDBConnection();

session_start();
$_SESSION['user_id'] = 1;

header('Content-Type: application/json');

// 测试添加到商品管理
$action = 'add_todos_to_products';

if ($action === 'add_todos_to_products') {
    $data = json_decode(file_get_contents('php://input'), true);
    $ids = $data['ids'] ?? [1, 2]; // 测试ID

    if (empty($ids)) {
        echo json_encode(['success'=>false, 'message'=>'未选择任何SKU']); exit;
    }

    // 获取要添加的SKU数据
    $ids_str = str_repeat('?,', count($ids) - 1) . '?';
    $types = str_repeat('i', count($ids));
    
    $stmt = $conn->prepare("SELECT sku, name, category_id, inventory_cycle FROM sku_todos WHERE id IN ($ids_str)");
    $stmt->bind_param($types, ...$ids);
    $stmt->execute();
    $res = $stmt->get_result();
    
    $added = 0;
    $skipped = 0;
    $errors = [];

    while ($todo = $res->fetch_assoc()) {
        $sku = $todo['sku'];
        $name = $todo['name'];
        $category_id = $todo['category_id'] ?? 0;
        $inventory_cycle = $todo['inventory_cycle'] ?? 'none';

        // 检查是否已存在
        $check = $conn->prepare("SELECT id FROM products WHERE sku = ?");
        $check->bind_param("s", $sku);
        $check->execute();
        
        if ($check->get_result()->num_rows > 0) {
            // 已存在，更新
            $update = $conn->prepare("UPDATE products SET name = ?, category_id = ?, inventory_cycle = ? WHERE sku = ?");
            $update->bind_param("siss", $name, $category_id, $inventory_cycle, $sku);
            if ($update->execute()) {
                $skipped++;
            } else {
                $errors[] = "SKU $sku 更新失败";
            }
        } else {
            // 不存在，插入
            $insert = $conn->prepare("INSERT INTO products (sku, name, category_id, inventory_cycle) VALUES (?, ?, ?, ?)");
            $insert->bind_param("ssis", $sku, $name, $category_id, $inventory_cycle);
            if ($insert->execute()) {
                $added++;
            } else {
                $errors[] = "SKU $sku 插入失败";
            }
        }
    }

    echo json_encode([
        'success'=>true,
        'message'=>"测试：已添加 $added 个新商品，更新 $skipped 个已有商品",
        'added'=>$added,
        'skipped'=>$skipped,
        'errors'=>$errors
    ]);
}
?>
