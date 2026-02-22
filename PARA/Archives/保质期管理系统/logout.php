<?php
/**
 * 用户登出
 */

session_start();
session_destroy();

header('Location: login.php');
exit;
?>
