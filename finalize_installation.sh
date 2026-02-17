#!/bin/bash
# 完成保质期系统安装 - 最终版本

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 完成保质期系统安装 ==="
echo ""

# 步骤1: 创建数据库
echo "📍 步骤1: 创建MySQL数据库"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
mysql -uroot -e "
CREATE DATABASE IF NOT EXISTS expiry_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;
"
echo "✅ 数据库创建完成"
mysql -uroot -e "SHOW DATABASES LIKE 'expiry%';"
EOF
echo ""

# 步骤2: 导入数据库结构
echo "📍 步骤2: 导入数据库结构"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
mysql -uexpiry_user -pExpiry2024! expiry_system < database.sql
echo "✅ 数据库结构已导入"
mysql -uexpiry_user -pExpiry2024! expiry_system -e "SHOW TABLES;"
EOF
echo ""

# 步骤3: 创建配置文件
echo "📍 步骤3: 创建配置文件"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
cat > config.php << 'PHPCONFIG'
<?php
define('DB_HOST', 'localhost');
define('DB_NAME', 'expiry_system');
define('DB_USER', 'expiry_user');
define('DB_PASS', 'Expiry2024!');
define('DB_CHARSET', 'utf8mb4');
define('SITE_NAME', '保质期管理系统');
define('VERSION', '2.7.3-alpha');
date_default_timezone_set('Asia/Shanghai');
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('session.cookie_httponly', 1);
ini_set('session.use_only_cookies', 1);
?>
PHPCONFIG
chown www:www config.php
chmod 644 config.php
echo "✅ 配置文件已创建"
ls -lh config.php
EOF
echo ""

# 步骤4: 删除安装文件
echo "📍 步骤4: 删除安装文件（安全）"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
rm -f install.php
echo "✅ install.php已删除"
EOF
echo ""

# 步骤5: 测试访问
echo "📍 步骤5: 测试系统访问"
sleep 2
echo "首页HTTP状态:"
curl -I http://ceshi.dhmip.cn 2>&1 | head -5
echo ""
echo "首页内容（前20行）:"
curl -s http://ceshi.dhmip.cn 2>&1 | head -20
echo ""

echo "=== 🎉 安装完成 ==="
echo ""
echo "✅ 数据库: expiry_system"
echo "✅ 用户: expiry_user / Expiry2024!"
echo "✅ 配置: config.php"
echo "✅ 系统版本: 2.7.3-alpha"
echo ""
echo "🌐 访问地址:"
echo "  http://ceshi.dhmip.cn"
echo ""
echo "🔑 登录信息:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "⏳ 后续任务:"
echo "1. 在宝塔面板申请SSL证书（Let's Encrypt）"
echo "2. 登录系统修改默认密码"
echo "3. 测试所有功能"
