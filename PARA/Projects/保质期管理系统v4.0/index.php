<?php
/**
 * 保质期管理系统 - v4.0.0 入口文件
 * 重定向到登录页面
 */

require_once __DIR__ . '/includes/config.php';
require_once __DIR__ . '/includes/functions.php';
require_once __DIR__ . '/includes/check_auth.php';

// 检查是否已登录
if (checkAuth()) {
    // 已登录，重定向到首页
    header('Location: /pages/index.php');
} else {
    // 未登录，重定向到登录页面
    header('Location: /pages/login.php');
}

exit;
