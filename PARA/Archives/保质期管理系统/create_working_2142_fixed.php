
<?php
/**
 * 保质期管理系统 - 综合管理后台
 * 文件名: index.php
 * 版本: v2.14.2
 * 创建日期: 2026-02-15
 */

session_start();

// 升级配置
define('APP_VERSION', '2.14.2');
define('UPDATE_URL', 'https://example.com');
define('UPDATE_SERVER', 'github');

// 数据库连接
function getDBConnection() {
    $servername = 'localhost';
    $username = 'pandian';
    $password = 'fs123456';
    $dbname = 'pandian';

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("连接失败: " . $conn->connect_error);
    }
    return $conn;
}

// 自动迁移
function autoMigrate() {
    $conn = getDBConnection();
    if (!$conn) return;
    $conn->close();
}
autoMigrate();

// API接口
if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    $action = $_GET['api'];
    $conn = getDBConnection();
    
    // 登录接口
    if ($action === 'login') {
        $data = json_decode(file_get_contents('php://input'), true);
        $username = $data['username'] ?? '';
        $password = $data['password'] ?? '';
        
        // 查询用户
        $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $result = $stmt->get_result();
        
        if ($result->num_rows > 0) {
            $user = $result->fetch_assoc();
            if (password_verify($password, $user['password'])) {
                $_SESSION['user_id'] = $user['id'];
                $_SESSION['username'] = $user['username'];
                echo json_encode(['success' => true]);
                exit;
            }
        }
        echo json_encode(['success' => false, 'message' => '账号或密码错误']);
        exit;
    }
    
    // 登出接口
    if ($action === 'logout') {
        session_destroy();
        echo json_encode(['success' => true]);
        exit;
    }
    
    // 获取盘点单详情
    if ($action === 'get_session_details') {
        $session_id = $_GET['session_id'] ?? '';
        
        // 简单返回示例数据
        $data = [
            'success' => true,
            'data' => [
                ['sku' => '12345', 'name' => '商品1', 'expiry_date' => '2026-12-31', 'quantity' => 10],
                ['sku' => '54321', 'name' => '商品2', 'expiry_date' => '2026-12-31', 'quantity' => 5]
            ]
        ];
        echo json_encode($data);
        exit;
    }
    
    $conn->close();
    exit;
}

// 未登录时显示登录页面
if (!isset($_SESSION['user_id'])) {
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>保质期管理系统 v2.14.2 - 登录</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header text-center">
                        <h3>🔐 请登录</h3>
                    </div>
                    <div class="card-body">
                        <form id="loginForm">
                            <div class="mb-3">
                                <label for="username" class="form-label">用户名</label>
                                <input type="text" class="form-control" id="username" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">密码</label>
                                <input type="password" class="form-control" id="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">登录</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('index.php?api=login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await response.json();
            
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || '登录失败');
            }
        });
    </script>
</body>
</html>
<?php
    exit;
}

// 登录后的页面
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>保质期管理系统 v2.14.2 - 主页面</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body>
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h1>保质期管理系统 v2.14.2</h1>
            <button class="btn btn-danger" onclick="logout()">登出</button>
        </div>
        
        <!-- 导航 -->
        <ul class="nav nav-pills mb-3">
            <li class="nav-item">
                <a class="nav-link active" href="index.php">首页</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="inventory.php">盘点</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" href="history.php">历史记录</a>
            </li>
        </ul>
        
        <!-- 内容区域 -->
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">功能介绍</h5>
                <p class="card-text">
                    这是一个功能完整的保质期管理系统，包含以下功能：
                    <ul>
                        <li>商品扫码录入</li>
                        <li>盘点管理</li>
                        <li>历史记录查询</li>
                        <li>商品有效期管理</li>
                        <li>分类管理</li>
                        <li>AI分析功能</li>
                        <li>盘点单编辑功能</li>
                    </ul>
                </p>
                <a href="inventory.php" class="btn btn-primary">开始盘点</a>
            </div>
        </div>
        
        <!-- 快速操作 -->
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">📊 AI分析</h5>
                        <p class="card-text">对盘点数据进行AI分析</p>
                        <a href="index.php?api=ai_analysis" class="btn btn-outline-primary">分析数据</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">✏️ 编辑盘点单</h5>
                        <p class="card-text">编辑现有的盘点单</p>
                        <a href="inventory.php?edit=true" class="btn btn-outline-primary">编辑</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">📋 查看历史</h5>
                        <p class="card-text">查看历史盘点记录</p>
                        <a href="history.php" class="btn btn-outline-primary">查看历史</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 登出
        function logout() {
            fetch('index.php?api=logout')
                .then(() => location.reload())
                .catch(err => console.error('登出失败:', err));
        }
        
        // AI分析按钮
        document.querySelectorAll('a[href*="ai_analysis"]').forEach(button => {
            button.addEventListener('click', async (e) => {
                e.preventDefault();
                alert('AI分析功能正在开发中');
            });
        });
    </script>
</body>
</html>
