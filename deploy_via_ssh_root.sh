#!/bin/bash
# 通过SSH部署保质期系统到宝塔服务器（使用root用户）

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."
DOMAIN="ceshi.dhmip.cn"
REPO="https://github.com/JarvisAI-CN/expiry-management-system.git"

echo "=== 通过SSH部署到宝塔服务器 ==="
echo ""

# 步骤1: 测试连接
echo "📍 步骤1: 确认SSH连接"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "echo '✅ 连接成功' && hostname && whoami"
echo ""

# 步骤2: 创建网站目录
echo "📍 步骤2: 创建网站目录"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 创建网站根目录
mkdir -p /www/wwwroot/ceshi.dhmip.cn
echo "✅ 目录已创建: /www/wwwroot/ceshi.dhmip.cn"
ls -la /www/wwwroot/
EOF
echo ""

# 步骤3: 克隆代码
echo "📍 步骤3: 从GitHub克隆代码"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 清空目录（如果有内容）
rm -rf .[!.]* *
echo "正在克隆代码..."
git clone https://github.com/JarvisAI-CN/expiry-management-system.git .

echo "✅ 克隆完成"
echo ""
echo "文件列表:"
ls -la
EOF
echo ""

# 步骤4: 设置权限
echo "📍 步骤4: 设置文件权限"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 设置所有者为www-data
chown -R www-data:www-data /www/wwwroot/ceshi.dhmip.cn

# 设置权限
chmod -R 755 /www/wwwroot/ceshi.dhmip.cn
find /www/wwwroot/ceshi.dhmip.cn -type f -name "*.php" -exec chmod 644 {} \;

echo "✅ 权限已设置"
echo ""
echo "目录权限:"
ls -la /www/wwwroot/ceshi.dhmip.cn | head -15
EOF
echo ""

# 步骤5: 检查关键文件
echo "📍 步骤5: 检查关键文件"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
echo "=== index.php ==="
ls -lh index.php 2>/dev/null || echo "❌ index.php不存在"
echo ""
echo "=== install.php ==="
ls -lh install.php 2>/dev/null || echo "❌ install.php不存在"
echo ""
echo "=== config.php ==="
ls -lh config.php 2>/dev/null || echo "❌ config.php不存在（未安装）"
EOF
echo ""

# 步骤6: 测试HTTP访问
echo "📍 步骤6: 测试HTTP访问"
curl -I http://ceshi.dhmip.cn 2>&1 | head -10
echo ""

echo "=== 部署完成 ==="
echo ""
echo "✅ 已完成:"
echo "1. 代码已克隆到 /www/wwwroot/ceshi.dhmip.cn"
echo "2. 文件权限已设置（www-data:755）"
echo ""
echo "⏳ 接下来需要:"
echo "1. 在宝塔面板添加网站 ceshi.dhmip.cn（如果还没有）"
echo "2. 创建MySQL数据库: expiry_system"
echo "3. 访问安装向导: http://ceshi.dhmip.cn/install.php"
echo "4. 完成安装后申请SSL证书"
