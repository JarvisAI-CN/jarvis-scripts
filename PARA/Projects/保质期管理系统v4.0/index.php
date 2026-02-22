<?php
/**
 * 保质期管理系统 - v4.0.0 入口文件
 * 重定向到登录页面
 */

// 检查文件是否在正确位置
$config_file = dirname(__FILE__) . '/includes/config.php';
if (!file_exists($config_file)) {
    $config_file = dirname(dirname(__FILE__)) . '/includes/config.php';
    if (!file_exists($config_file)) {
        $config_file = '/www/wwwroot/pandian.dhmip.cn/public_html/includes/config.php';
    }
}

require_once $config_file;

$functions_file = dirname(__FILE__) . '/includes/functions.php';
if (!file_exists($functions_file)) {
    $functions_file = dirname(dirname(__FILE__)) . '/includes/functions.php';
    if (!file_exists($functions_file)) {
        $functions_file = '/www/wwwroot/pandian.dhmip.cn/public_html/includes/functions.php';
    }
}

require_once $functions_file;

$check_auth_file = dirname(__FILE__) . '/includes/check_auth.php';
if (!file_exists($check_auth_file)) {
    $check_auth_file = dirname(dirname(__FILE__)) . '/includes/check_auth.php';
    if (!file_exists($check_auth_file)) {
        $check_auth_file = '/www/wwwroot/pandian.dhmip.cn/public_html/includes/check_auth.php';
    }
}

require_once $check_auth_file;

// 检查是否已登录
if (checkAuth()) {
    // 已登录，重定向到首页
    header('Location: /pages/index.php');
} else {
    // 未登录，重定向到登录页面
    header('Location: /pages/login.php');
}

exit;
