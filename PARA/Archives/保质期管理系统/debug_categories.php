<?php
require_once 'db.php';
$conn = getDBConnection();

header('Content-Type: application/json');

// 模拟登录状态
session_start();
$_SESSION['user_id'] = 1;

// 调用get_categories API
$action = 'get_categories';
$conn = getDBConnection();

if ($action === 'get_categories') {
    $res = $conn->query("SELECT * FROM categories");
    $list = [];
    while($r = $res->fetch_assoc()) {
        $list[] = $r;
    }
    echo json_encode(['success'=>true, 'categories'=>$list]);
}
?>
