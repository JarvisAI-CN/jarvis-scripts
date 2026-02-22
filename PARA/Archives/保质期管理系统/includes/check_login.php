<?php
/**
 * 登录状态检查
 * 如果未登录，重定向到登录页
 */

if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}
?>
