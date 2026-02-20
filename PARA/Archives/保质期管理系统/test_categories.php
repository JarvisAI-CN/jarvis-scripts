<?php
require_once 'db.php';
session_start();
$conn = getDBConnection();

// 模拟登录
$_SESSION['user_id'] = 1;

header('Content-Type: application/json');

// 调用get_categories API
$res = $conn->query("SELECT * FROM categories");
$list = [];
while($r = $res->fetch_assoc()) {
    $list[] = $r;
}

echo json_encode(['success'=>true, 'categories'=>$list]);
?>
