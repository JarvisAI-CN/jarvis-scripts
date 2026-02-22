<?php
/**
 * ========================================
 * 保质期管理系统 - 测试版 (v1.0.0)
 * 文件名: test_index.php
 * ========================================
 */

// 初始化
define('APP_VERSION', '1.0.0');
session_start();

// 模拟DB
$users = [
    'admin' => password_hash('fs123456', PASSWORD_DEFAULT)
];

// API路由处理
if (isset($_GET['api'])) {
    header('Content-Type: application/json');
    
    if ($_GET['api'] === 'login') {
        $data = json_decode(file_get_contents('php://input'), true);
        $username = $data['username'] ?? '';
        $password = $data['password'] ?? '';
        
        if ($username && $password) {
            if (isset($users[$username]) && password_verify($password, $users[$username])) {
                $_SESSION['user_id'] = 1;
                $_SESSION['username'] = $username;
                echo json_encode(['success'=>true]);
                exit;
            }
        }
        
        echo json_encode(['success'=>false, 'message'=>'账号或密码错误']);
        exit;
    }
    
    if ($_GET['api'] === 'logout') {
        session_destroy();
        echo json_encode(['success'=>true]);
        exit;
    }
    
    exit;
}

?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>保质期管理系统</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 2rem;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #666;
        }
        .form-group input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
            box-sizing: border-box;
        }
        .btn {
            width: 100%;
            padding: 0.75rem;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
        }
        .btn:hover {
            background: #0056b3;
        }
        .alert {
            padding: 1rem;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .main-content {
            text-align: center;
        }
        .logout-btn {
            background: #dc3545;
        }
        .logout-btn:hover {
            background: #c82333;
        }
    </style>
</head>
<body>
    <div class="container">
        <?php if (!isset($_SESSION['user_id'])): ?>
            <h1>🔐 请登录</h1>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">用户名</label>
                    <input type="text" id="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">密码</label>
                    <input type="password" id="password" required>
                </div>
                
                <button type="submit" class="btn">进入系统</button>
            </form>
            
            <div id="errorMessage" style="display: none;" class="alert alert-danger"></div>
        <?php else: ?>
            <div class="main-content">
                <h1>保质期管理系统</h1>
                <p>欢迎回来，<?php echo $_SESSION['username']; ?>！</p>
                
                <div class="form-group">
                    <p>这是一个测试版本，用于验证登录功能。</p>
                </div>
                
                <button id="logoutBtn" class="btn logout-btn">退出登录</button>
            </div>
        <?php endif; ?>
    </div>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            // 登录功能
            const loginForm = document.getElementById('loginForm');
            if (loginForm) {
                loginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    
                    const errorDiv = document.getElementById('errorMessage');
                    
                    try {
                        const response = await fetch('?api=login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                username,
                                password
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            // 登录成功，刷新页面
                            location.reload();
                        } else {
                            errorDiv.textContent = data.message || '登录失败';
                            errorDiv.style.display = 'block';
                        }
                    } catch (error) {
                        errorDiv.textContent = '网络错误，请稍后再试';
                        errorDiv.style.display = 'block';
                    }
                });
            }
            
            // 退出登录功能
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', async () => {
                    await fetch('?api=logout');
                    location.reload();
                });
            }
        });
    </script>
</body>
</html>
