#!/bin/bash
# 处理.user.ini锁定问题

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 解除.user.ini锁定并重新部署 ==="
echo ""

# 步骤1: 解除文件属性锁定
echo "📍 步骤1: 解除.user.ini的不可变属性"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 使用chattr解除不可变属性
chattr -i .user.ini 2>/dev/null
rm -f .user.ini

# 删除所有内容（包括隐藏文件）
rm -rf .[!.]* * 2>/dev/null

# 验证目录为空
ls -la

echo "✅ 目录已清空"
EOF
echo ""

# 步骤2: 克隆代码
echo "📍 步骤2: 克隆代码到空目录"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 确保目录完全为空
ls -la

# 克隆代码
git clone https://github.com/JarvisAI-CN/expiry-management-system.git .

echo ""
echo "✅ 克隆完成"
echo ""
echo "文件列表:"
ls -la | head -20
EOF
echo ""

# 步骤3: 设置权限
echo "📍 步骤3: 设置文件权限"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 设置所有者
chown -R www:www .

# 设置权限
chmod -R 755 .
find . -type f -name "*.php" -exec chmod 644 {} \;

echo "✅ 权限已设置"
ls -la | head -15
EOF
echo ""

# 步骤4: 验证
echo "📍 步骤4: 验证部署"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

echo "=== 关键文件检查 ==="
ls -lh index.php 2>/dev/null && echo "✅ index.php" || echo "❌ index.php不存在"
ls -lh install.php 2>/dev/null && echo "✅ install.php" || echo "❌ install.php不存在"
ls -lh api/ 2>/dev/null && echo "✅ api目录" || echo "❌ api目录不存在"

echo ""
echo "=== PHP文件统计 ==="
find . -name "*.php" -type f | wc -l

echo ""
echo "=== 目录大小 ==="
du -sh .
EOF
echo ""

# 步骤5: 测试访问
echo "📍 步骤5: 测试HTTP访问"
sleep 2
curl -I http://ceshi.dhmip.cn 2>&1 | head -10
curl http://ceshi.dhmip.cn 2>&1 | head -20
echo ""

echo "=== 部署完成 ==="
