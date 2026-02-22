<?php
/**
 * 保质期管理系统 - v4.0.0 登录页面
 * 用户身份验证入口
 */

define('APP_NAME', '保质期管理系统');
define('DEBUG_MODE', true);
session_start();

// 检查是否已登录
if (isset($_SESSION['user_id']) && isset($_SESSION['username'])) {
    header('Location: /index.php');
    exit;
}

// 设置页面信息
$pageTitle = '登录 - 保质期管理系统';
$pageName = 'login';
?>

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="保质期管理系统登录页面">
    <meta name="keywords" content="保质期管理,登录">
    
    <title><?php echo htmlEscape($pageTitle); ?></title>
    
    <!-- Bootstrap 5.3 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    
    <!-- Custom Styles -->
    <link rel="stylesheet" href="/assets/css/login.css">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    
    <!-- Security Headers -->
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="Referrer-Policy" content="no-referrer-when-downgrade">
</head>
<body class="bg-gradient-login">
    <div class="container-fluid h-100">
        <div class="row h-100 justify-content-center align-items-center">
            <!-- Left Side - Branding -->
            <div class="col-lg-6 d-none d-lg-flex flex-column justify-content-center align-items-center bg-gradient-branding">
                <div class="login-brand">
                    <div class="brand-icon">
                        <i class="bi bi-calendar-check"></i>
                    </div>
                    <h1 class="brand-title">保质期管理系统</h1>
                    <p class="brand-subtitle">专业的商品保质期管理系统</p>
                </div>
                
                <div class="features">
                    <div class="feature-item">
                        <i class="bi bi-scan text-primary"></i>
                        <h3>快速扫描</h3>
                        <p>支持二维码扫描，快速录入商品信息</p>
                    </div>
                    
                    <div class="feature-item">
                        <i class="bi bi-clock-history text-primary"></i>
                        <h3>历史记录</h3>
                        <p>完整记录所有盘点历史，支持查询和导出</p>
                    </div>
                    
                    <div class="feature-item">
                        <i class="bi bi-shield-check text-primary"></i>
                        <h3>数据安全</h3>
                        <p>完善的权限管理和数据备份机制</p>
                    </div>
                </div>
            </div>
            
            <!-- Right Side - Login Form -->
            <div class="col-lg-6 d-flex justify-content-center align-items-center">
                <div class="login-card">
                    <div class="card shadow-lg border-0 rounded-4">
                        <div class="card-body p-4 p-md-5">
                            <div class="text-center mb-4">
                                <div class="d-inline-flex align-items-center justify-content-center mb-3" style="width: 70px; height: 70px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 50%;">
                                    <i class="bi bi-calendar-check text-white h2"></i>
                                </div>
                                <h2 class="h4 fw-bold text-primary mb-1">保质期管理系统</h2>
                                <p class="text-muted">专业的商品保质期管理系统</p>
                                <span class="badge bg-primary-subtle text-primary small">v4.0.0</span>
                            </div>
                            
                            <!-- Alert Container -->
                            <div id="alert-container" class="mb-4"></div>
                            
                            <form id="loginForm">
                                <div class="mb-3">
                                    <label for="username" class="form-label">用户名</label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light border-end-0">
                                            <i class="bi bi-person-circle text-muted"></i>
                                        </span>
                                        <input type="text" id="username" 
                                               class="form-control form-control-lg bg-light border-start-0" 
                                               placeholder="请输入用户名" 
                                               required
                                               autofocus>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="password" class="form-label">密码</label>
                                    <div class="input-group">
                                        <span class="input-group-text bg-light border-end-0">
                                            <i class="bi bi-lock text-muted"></i>
                                        </span>
                                        <input type="password" id="password" 
                                               class="form-control form-control-lg bg-light border-start-0" 
                                               placeholder="请输入密码" 
                                               required>
                                        <button class="btn btn-outline-secondary bg-light border-start-0" type="button" id="togglePassword">
                                            <i class="bi bi-eye-slash"></i>
                                        </button>
                                    </div>
                                </div>
                                
                                <div class="mb-4 form-check">
                                    <input type="checkbox" id="remember" 
                                           class="form-check-input">
                                    <label class="form-check-label" for="remember">
                                        记住我 (7天)
                                    </label>
                                </div>
                                
                                <button type="submit" id="loginBtn" 
                                        class="btn btn-primary btn-lg w-100">
                                    <span id="loginBtnText">
                                        <i class="bi bi-box-arrow-in-right"></i>
                                        登录系统
                                    </span>
                                </button>
                            </form>
                            
                            <!-- Loading State -->
                            <div id="loadingState" class="d-none text-center py-4">
                                <div class="spinner-border text-primary" role="status">
                                    <span class="visually-hidden">登录中...</span>
                                </div>
                                <p class="mt-2 text-muted">正在验证您的身份...</p>
                            </div>
                            
                            <!-- Demo Info -->
                            <div class="mt-4 text-center">
                                <div class="text-muted small">
                                    <p>📌 演示账号:</p>
                                    <p class="mb-1">用户名: <code class="text-primary">admin</code></p>
                                    <p class="mb-0">密码: <code class="text-primary">fs123456</code></p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="text-center mt-4">
                        <p class="text-muted small">
                            <i class="bi bi-shield-check"></i>
                            © <?php echo date('Y'); ?> 保质期管理系统 - 专业的商品保质期管理系统
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script src="/assets/js/login.js"></script>
    
    <script>
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化登录表单
            const loginForm = document.getElementById('loginForm');
            const loginBtn = document.getElementById('loginBtn');
            const loginBtnText = document.getElementById('loginBtnText');
            const loadingState = document.getElementById('loadingState');
            const alertContainer = document.getElementById('alert-container');
            
            // 密码显示/隐藏
            document.getElementById('togglePassword').addEventListener('click', function() {
                const passwordInput = document.getElementById('password');
                const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
                passwordInput.setAttribute('type', type);
                
                const icon = this.querySelector('i');
                icon.classList.toggle('bi-eye-slash');
                icon.classList.toggle('bi-eye');
            });
            
            // 登录表单提交
            loginForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                // 显示加载状态
                loginBtn.disabled = true;
                loginBtnText.style.display = 'none';
                loadingState.classList.remove('d-none');
                alertContainer.innerHTML = '';
                
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const remember = document.getElementById('remember').checked;
                
                try {
                    const response = await fetch('/api/login.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            username: username.trim(),
                            password: password.trim(),
                            remember: remember
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        // 登录成功
                        showAlert('登录成功！正在跳转...', 'success');
                        
                        // 延迟跳转
                        setTimeout(() => {
                            window.location.href = '/index.php';
                        }, 1000);
                    } else {
                        // 登录失败
                        showAlert(result.message || '登录失败', 'danger');
                        
                        // 重置状态
                        loginBtn.disabled = false;
                        loginBtnText.style.display = 'inline';
                        loadingState.classList.add('d-none');
                    }
                } catch (error) {
                    showAlert('网络错误，请稍后再试', 'danger');
                    
                    // 重置状态
                    loginBtn.disabled = false;
                    loginBtnText.style.display = 'inline';
                    loadingState.classList.add('d-none');
                }
            });
            
            // 显示通知
            function showAlert(message, type) {
                const alertDiv = document.createElement('div');
                alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
                alertDiv.setAttribute('role', 'alert');
                
                const icon = {
                    'success': 'bi-check-circle-fill',
                    'danger': 'bi-exclamation-triangle-fill',
                    'warning': 'bi-exclamation-triangle-fill',
                    'info': 'bi-info-circle-fill'
                };
                
                alertDiv.innerHTML = `
                    <i class="bi ${icon[type]}"></i>
                    <span class="ms-2">${message}</span>
                    <button type="button" class="btn-close" 
                            data-bs-dismiss="alert" 
                            aria-label="Close"></button>
                `;
                
                alertContainer.appendChild(alertDiv);
                
                // 自动关闭
                if (type === 'success') {
                    setTimeout(() => {
                        alertDiv.classList.add('fade');
                        setTimeout(() => alertDiv.remove(), 300);
                    }, 2000);
                }
            }
        });
    </script>
</body>
</html>
