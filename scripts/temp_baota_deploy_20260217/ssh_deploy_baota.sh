#!/bin/bash
# 宝塔服务器SSH部署脚本

echo "=== 通过SSH直接部署保质期系统到宝塔服务器 ==="

SERVER="ubuntu@82.157.20.7"
PASSWORD="Fs123456."
DOMAIN="ceshi.dhmip.cn"
REPO="https://github.com/JarvisAI-CN/expiry-management-system.git"

# 使用sshpass自动输入密码
if ! command -v sshpass &> /dev/null; then
    echo "安装sshpass..."
    sudo apt-get install -y sshpass
fi

echo ""
echo "📍 步骤1: 测试SSH连接"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "echo '✅ SSH连接成功' && hostname && whoami"

echo ""
echo "📍 步骤2: 创建网站目录"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 创建网站根目录
sudo mkdir -p /www/wwwroot/ceshi.dhmip.cn
echo "✅ 目录已创建"

# 检查目录
ls -la /www/wwwroot/ | grep ceshi
EOF

echo ""
echo "📍 步骤3: 克隆GitHub代码"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 如果目录不为空，先清空
if [ "$(ls -A)" ]; then
    echo "⚠️ 目录不为空，清空中..."
    sudo rm -rf *
fi

# 克隆代码
echo "正在克隆代码..."
sudo git clone https://github.com/JarvisAI-CN/expiry-management-system.git .

echo "✅ 代码克隆完成"
ls -la
EOF

echo ""
echo "📍 步骤4: 设置文件权限"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 设置所有者和权限
sudo chown -R www-data:www-data /www/wwwroot/ceshi.dhmip.cn
sudo chmod -R 755 /www/wwwroot/ceshi.dhmip.cn

# PHP文件设为644
sudo find /www/wwwroot/ceshi.dhmip.cn -type f -name "*.php" -exec chmod 644 {} \;

echo "✅ 文件权限已设置"
ls -la /www/wwwroot/ceshi.dhmip.cn | head -10
EOF

echo ""
echo "📍 步骤5: 检查Git克隆状态"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
echo "=== Git状态 ==="
git status
git log -1 --oneline

echo ""
echo "=== 文件列表 ==="
ls -la
EOF

echo ""
echo "=== SSH部署完成 ==="
echo ""
echo "⏳ 接下来需要在宝塔面板中:"
echo "1. 创建网站 ceshi.dhmip.cn（如果还没有）"
echo "2. 创建MySQL数据库: expiry_system"
echo "3. 访问安装向导: http://ceshi.dhmip.cn/install.php"
echo "4. 申请SSL证书"
echo ""
echo "🌐 测试访问:"
curl -I http://ceshi.dhmip.cn 2>&1 | head -5
