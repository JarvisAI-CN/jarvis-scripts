#!/bin/bash
# 完成保质期系统安装

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 完成保质期系统安装 ==="
echo ""

# 步骤1: 创建数据库
echo "📍 步骤1: 创建MySQL数据库"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 登录MySQL并创建数据库
mysql -uroot -e "
CREATE DATABASE IF NOT EXISTS expiry_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;
SHOW DATABASES LIKE 'expiry_system';
SELECT User, Host FROM mysql.user WHERE User='expiry_user';
"
echo "✅ 数据库创建完成"
EOF
echo ""

# 步骤2: 导入数据库结构
echo "📍 步骤2: 导入数据库结构"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 检查SQL文件
ls -lh database.sql

# 导入数据库
mysql -uexpiry_user -pExpiry2024! expiry_system < database.sql

echo "✅ 数据库结构已导入"
echo ""
echo "=== 数据库表 ==="
mysql -uexpiry_user -pExpiry2024! expiry_system -e "SHOW TABLES;"
EOF
echo ""

# 步骤3: 创建配置文件
echo "📍 步骤3: 创建配置文件"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

cat > config.php << 'PHPCONFIG'
<?php
// 数据库配置
define('DB_HOST', 'localhost');
define('DB_NAME', 'expiry_system');
define('DB_USER', 'expiry_user');
define('DB_PASS', 'Expiry2024!');
define('DB_CHARSET', 'utf8mb4');

// 系统配置
define('SITE_NAME', '保质期管理系统');
define('VERSION', '2.7.3-alpha');

// 时区设置
date_default_timezone_set('Asia/Shanghai');

// 错误报告（生产环境设为0）
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Session配置
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
?>
PHPCONFIG

# 设置权限
chown www:www config.php
chmod 644 config.php

echo "✅ 配置文件已创建"
ls -lh config.php
EOF
echo ""

# 步骤4: 测试访问
echo "📍 步骤4: 测试系统访问"
sleep 2
echo "访问首页:"
curl -I http://ceshi.dhmip.cn 2>&1 | head -10
echo ""
echo "访问内容（前30行）:"
curl http://ceshi.dhmip.cn 2>&1 | head -30
echo ""

echo "=== 安装完成 ==="
echo ""
echo "✅ 数据库: expiry_system"
echo "✅ 数据库用户: expiry_user"
echo "✅ 配置文件: config.php"
echo ""
echo "🌐 访问地址:"
echo "  http://ceshi.dhmip.cn"
echo ""
echo "🔑 默认登录:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "⏳ 后续步骤:"
echo "1. 在宝塔面板申请SSL证书"
echo "2. 修改默认密码"
echo "3. 测试所有功能"
