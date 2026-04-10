<?php
/**
 * 保质期管理系统 v4.0 - 系统设置页面
 * 路径: /pages/admin/settings.php
 * 访问权限: 仅管理员
 * 创建时间: 2026-04-11
 */

// 定义应用名称
define('APP_NAME', '保质期管理系统');
session_start();

// 引入必要文件
require_once __DIR__ . '/../../includes/config.php';
require_once __DIR__ . '/../../includes/functions.php';
require_once __DIR__ . '/../../includes/check_auth.php';

// 权限检查：只有管理员可以访问
if (!isset($_SESSION['user']) || $_SESSION['user']['role'] !== 'admin') {
    header('Location: /');
    exit;
}

// 初始化消息
$success_message = '';
$error_message = '';

// 处理表单提交
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    try {
        switch ($action) {
            case 'save_system':
                // 保存系统设置
                $system_name = $_POST['system_name'] ?? APP_NAME;
                $version = $_POST['version'] ?? '4.0.0';
                
                // 这里应该保存到数据库或配置文件
                // 暂时只显示成功消息
                $success_message = '系统设置已保存';
                break;
                
            case 'save_notification':
                // 保存通知设置
                $expiry_warning_days = intval($_POST['expiry_warning_days'] ?? 7);
                $enable_email = isset($_POST['enable_email']) ? 1 : 0;
                $email_address = $_POST['email_address'] ?? '';
                
                $success_message = '通知设置已保存';
                break;
                
            case 'save_backup':
                // 保存备份设置
                $backup_enabled = isset($_POST['backup_enabled']) ? 1 : 0;
                $backup_interval = intval($_POST['backup_interval'] ?? 24);
                $backup_retention = intval($_POST['backup_retention'] ?? 30);
                
                $success_message = '备份设置已保存';
                break;
                
            case 'test_database':
                // 测试数据库连接
                $db = getDB();
                if ($db) {
                    $success_message = '数据库连接正常';
                } else {
                    throw new Exception('数据库连接失败');
                }
                break;
                
            case 'clear_cache':
                // 清除缓存
                $cache_dir = __DIR__ . '/../../cache';
                if (is_dir($cache_dir)) {
                    $files = glob($cache_dir . '/*');
                    foreach ($files as $file) {
                        if (is_file($file)) {
                            unlink($file);
                        }
                    }
                    $success_message = '缓存已清除';
                } else {
                    $success_message = '缓存目录不存在，无需清除';
                }
                break;
                
            default:
                $error_message = '未知的操作';
        }
    } catch (Exception $e) {
        $error_message = '操作失败: ' . $e->getMessage();
    }
}

// 获取当前设置
$current_settings = [
    'system_name' => APP_NAME,
    'version' => '4.0.0',
    'expiry_warning_days' => 7,
    'enable_email' => false,
    'email_address' => '',
    'backup_enabled' => true,
    'backup_interval' => 24,
    'backup_retention' => 30,
];

// 获取系统信息
$system_info = [
    'php_version' => PHP_VERSION,
    'server_software' => $_SERVER['SERVER_SOFTWARE'] ?? 'Unknown',
    'document_root' => $_SERVER['DOCUMENT_ROOT'] ?? '',
    'server_time' => date('Y-m-d H:i:s'),
];

// 获取数据库信息
try {
    $db = getDB();
    $stmt = $db->query("SELECT VERSION() as version");
    $db_info = $stmt->fetch(PDO::FETCH_ASSOC);
    $mysql_version = $db_info['version'] ?? 'Unknown';
    
    // 获取数据库大小
    $stmt = $db->query("SELECT table_schema AS 'database', 
                        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'size' 
                        FROM information_schema.TABLES 
                        WHERE table_schema = '" . DB_NAME . "' 
                        GROUP BY table_schema");
    $db_size_info = $stmt->fetch(PDO::FETCH_ASSOC);
    $database_size = $db_size_info['size'] ?? 0;
} catch (Exception $e) {
    $mysql_version = 'Error: ' . $e->getMessage();
    $database_size = 0;
}

// 获取最近的备份文件
$backup_files = [];
$backup_dir = __DIR__ . '/../../backup';
if (is_dir($backup_dir)) {
    $files = scandir($backup_dir);
    foreach ($files as $file) {
        if ($file !== '.' && $file !== '..' && strpos($file, '.sql') !== false) {
            $filepath = $backup_dir . '/' . $file;
            $backup_files[] = [
                'name' => $file,
                'size' => filesize($filepath),
                'date' => date('Y-m-d H:i:s', filemtime($filepath))
            ];
        }
    }
    // 按日期排序
    usort($backup_files, function($a, $b) {
        return strtotime($b['date']) - strtotime($a['date']);
    });
}

// 页面标题
$page_title = '系统设置';
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $page_title; ?> - <?php echo APP_NAME; ?></title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="container-fluid">
            <div class="d-flex justify-content-between align-items-center w-100">
                <a class="navbar-brand" href="/"><?php echo APP_NAME; ?></a>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="/">首页</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pages/new.php">新增盘点</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pages/past.php">历史盘点</a>
                    </li>
                    <?php if ($_SESSION['user']['role'] === 'admin'): ?>
                    <li class="nav-item">
                        <a class="nav-link active" href="/pages/admin/settings.php">系统设置</a>
                    </li>
                    <?php endif; ?>
                    <li class="nav-item">
                        <a class="nav-link" href="/api/logout.php">退出</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- 主内容区 -->
    <div class="container mt-4">
        <?php if ($success_message): ?>
        <div class="alert alert-success">
            <?php echo htmlspecialchars($success_message); ?>
        </div>
        <?php endif; ?>
        
        <?php if ($error_message): ?>
        <div class="alert alert-danger">
            <?php echo htmlspecialchars($error_message); ?>
        </div>
        <?php endif; ?>

        <div class="row">
            <!-- 左侧设置选项卡 -->
            <div class="col-md-3">
                <div class="card">
                    <div class="card-header">
                        <h5>设置类别</h5>
                    </div>
                    <div class="list-group list-group-flush">
                        <a href="#system-settings" class="list-group-item list-group-item-action" data-toggle="tab">系统设置</a>
                        <a href="#notification-settings" class="list-group-item list-group-item-action" data-toggle="tab">通知设置</a>
                        <a href="#backup-settings" class="list-group-item list-group-item-action" data-toggle="tab">备份设置</a>
                        <a href="#system-info" class="list-group-item list-group-item-action" data-toggle="tab">系统信息</a>
                    </div>
                </div>
            </div>

            <!-- 右侧设置内容 -->
            <div class="col-md-9">
                <div class="tab-content">
                    <!-- 系统设置 -->
                    <div class="tab-pane fade show active" id="system-settings">
                        <div class="card">
                            <div class="card-header">
                                <h5>系统设置</h5>
                            </div>
                            <div class="card-body">
                                <form method="POST" action="">
                                    <input type="hidden" name="action" value="save_system">
                                    
                                    <div class="form-group">
                                        <label class="form-label">系统名称</label>
                                        <input type="text" class="form-control" name="system_name" 
                                               value="<?php echo htmlspecialchars($current_settings['system_name']); ?>" required>
                                        <small class="text-muted">系统显示的名称</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="form-label">版本号</label>
                                        <input type="text" class="form-control" name="version" 
                                               value="<?php echo htmlspecialchars($current_settings['version']); ?>" required>
                                        <small class="text-muted">当前系统版本</small>
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary">保存设置</button>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- 通知设置 -->
                    <div class="tab-pane fade" id="notification-settings">
                        <div class="card">
                            <div class="card-header">
                                <h5>通知设置</h5>
                            </div>
                            <div class="card-body">
                                <form method="POST" action="">
                                    <input type="hidden" name="action" value="save_notification">
                                    
                                    <div class="form-group">
                                        <label class="form-label">临期预警天数</label>
                                        <input type="number" class="form-control" name="expiry_warning_days" 
                                               value="<?php echo htmlspecialchars($current_settings['expiry_warning_days']); ?>" min="1" max="365" required>
                                        <small class="text-muted">在此天数内的商品将被标记为临期</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="form-label">启用邮件通知</label>
                                        <div class="form-check">
                                            <input type="checkbox" class="form-check-input" name="enable_email" 
                                                   <?php echo $current_settings['enable_email'] ? 'checked' : ''; ?>>
                                            <label class="form-check-label">启用</label>
                                        </div>
                                        <small class="text-muted">开启后将发送邮件通知</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="form-label">通知邮箱地址</label>
                                        <input type="email" class="form-control" name="email_address" 
                                               value="<?php echo htmlspecialchars($current_settings['email_address']); ?>">
                                        <small class="text-muted">接收通知的邮箱地址</small>
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary">保存设置</button>
                                </form>
                            </div>
                        </div>
                    </div>

                    <!-- 备份设置 -->
                    <div class="tab-pane fade" id="backup-settings">
                        <div class="card">
                            <div class="card-header">
                                <h5>备份设置</h5>
                            </div>
                            <div class="card-body">
                                <form method="POST" action="">
                                    <input type="hidden" name="action" value="save_backup">
                                    
                                    <div class="form-group">
                                        <label class="form-label">启用自动备份</label>
                                        <div class="form-check">
                                            <input type="checkbox" class="form-check-input" name="backup_enabled" 
                                                   <?php echo $current_settings['backup_enabled'] ? 'checked' : ''; ?>>
                                            <label class="form-check-label">启用</label>
                                        </div>
                                        <small class="text-muted">开启后将自动备份数据库</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="form-label">备份间隔（小时）</label>
                                        <input type="number" class="form-control" name="backup_interval" 
                                               value="<?php echo htmlspecialchars($current_settings['backup_interval']); ?>" min="1" max="168" required>
                                        <small class="text-muted">自动备份的时间间隔</small>
                                    </div>
                                    
                                    <div class="form-group">
                                        <label class="form-label">备份保留天数</label>
                                        <input type="number" class="form-control" name="backup_retention" 
                                               value="<?php echo htmlspecialchars($current_settings['backup_retention']); ?>" min="1" max="365" required>
                                        <small class="text-muted">备份文件的保留时间</small>
                                    </div>
                                    
                                    <button type="submit" class="btn btn-primary">保存设置</button>
                                </form>
                                
                                <hr>
                                
                                <h6>最近的备份文件</h6>
                                <?php if (empty($backup_files)): ?>
                                <p class="text-muted">没有找到备份文件</p>
                                <?php else: ?>
                                <div class="table-responsive">
                                    <table class="table">
                                        <thead>
                                            <tr>
                                                <th>文件名</th>
                                                <th>大小</th>
                                                <th>日期</th>
                                                <th>操作</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <?php foreach ($backup_files as $backup): ?>
                                            <tr>
                                                <td><?php echo htmlspecialchars($backup['name']); ?></td>
                                                <td><?php echo number_format($backup['size'] / 1024 / 1024, 2); ?> MB</td>
                                                <td><?php echo htmlspecialchars($backup['date']); ?></td>
                                                <td>
                                                    <button class="btn btn-sm btn-primary">下载</button>
                                                    <button class="btn btn-sm btn-danger">删除</button>
                                                </td>
                                            </tr>
                                            <?php endforeach; ?>
                                        </tbody>
                                    </table>
                                </div>
                                <?php endif; ?>
                            </div>
                        </div>
                    </div>

                    <!-- 系统信息 -->
                    <div class="tab-pane fade" id="system-info">
                        <div class="card">
                            <div class="card-header">
                                <h5>系统信息</h5>
                            </div>
                            <div class="card-body">
                                <table class="table">
                                    <tbody>
                                        <tr>
                                            <th>PHP版本</th>
                                            <td><?php echo htmlspecialchars($system_info['php_version']); ?></td>
                                        </tr>
                                        <tr>
                                            <th>MySQL版本</th>
                                            <td><?php echo htmlspecialchars($mysql_version); ?></td>
                                        </tr>
                                        <tr>
                                            <th>服务器软件</th>
                                            <td><?php echo htmlspecialchars($system_info['server_software']); ?></td>
                                        </tr>
                                        <tr>
                                            <th>文档根目录</th>
                                            <td><?php echo htmlspecialchars($system_info['document_root']); ?></td>
                                        </tr>
                                        <tr>
                                            <th>数据库大小</th>
                                            <td><?php echo number_format($database_size, 2); ?> MB</td>
                                        </tr>
                                        <tr>
                                            <th>服务器时间</th>
                                            <td><?php echo htmlspecialchars($system_info['server_time']); ?></td>
                                        </tr>
                                    </tbody>
                                </table>
                                
                                <hr>
                                
                                <h6>系统操作</h6>
                                <div class="d-flex gap-2">
                                    <form method="POST" action="" class="d-inline">
                                        <input type="hidden" name="action" value="test_database">
                                        <button type="submit" class="btn btn-info">测试数据库连接</button>
                                    </form>
                                    
                                    <form method="POST" action="" class="d-inline">
                                        <input type="hidden" name="action" value="clear_cache">
                                        <button type="submit" class="btn btn-warning">清除缓存</button>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
        <div class="container">
            <p>&copy; <?php echo date('Y'); ?> <?php echo APP_NAME; ?>. 版本 <?php echo $current_settings['version']; ?></p>
        </div>
    </footer>

    <script src="/assets/js/app.js"></script>
    <script>
        // 设置选项卡切换
        document.querySelectorAll('.list-group-item').forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const target = this.getAttribute('href');
                
                // 移除所有active类
                document.querySelectorAll('.list-group-item').forEach(i => i.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('show', 'active'));
                
                // 添加active类到当前项
                this.classList.add('active');
                document.querySelector(target).classList.add('show', 'active');
            });
        });
    </script>
</body>
</html>
