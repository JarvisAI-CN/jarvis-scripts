#!/bin/bash
# 修复后的SSH部署脚本

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 修复部署：重新克隆代码 ==="
echo ""

# 步骤1: 强制删除并重建目录
echo "📍 步骤1: 清空并重建目录"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 删除整个目录
rm -rf /www/wwwroot/ceshi.dhmip.cn

# 重新创建
mkdir -p /www/wwwroot/ceshi.dhmip.cn

echo "✅ 目录已清空并重建"
ls -la /www/wwwroot/
EOF
echo ""

# 步骤2: 克隆代码
echo "📍 步骤2: 克隆GitHub代码"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn

# 确保目录为空
ls -la

# 克隆代码
git clone https://github.com/JarvisAI-CN/expiry-management-system.git .

echo ""
echo "✅ 克隆完成"
echo ""
echo "文件列表:"
ls -la
EOF
echo ""

# 步骤3: 设置权限（使用www用户）
echo "📍 步骤3: 设置文件权限"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 使用www用户（宝塔默认）
chown -R www:www /www/wwwroot/ceshi.dhmip.cn
chmod -R 755 /www/wwwroot/ceshi.dhmip.cn
find /www/wwwroot/ceshi.dhmip.cn -type f -name "*.php" -exec chmod 644 {} \;

echo "✅ 权限已设置"
ls -la /www/wwwroot/ceshi.dhmip.cn | head -15
EOF
echo ""

# 步骤4: 验证关键文件
echo "📍 步骤4: 验证关键文件"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
echo "=== 检查关键文件 ==="
ls -lh index.php 2>/dev/null && echo "✅ index.php存在" || echo "❌ index.php不存在"
ls -lh install.php 2>/dev/null && echo "✅ install.php存在" || echo "❌ install.php不存在"
ls -lh README.md 2>/dev/null && echo "✅ README.md存在"
echo ""
echo "=== PHP文件数量 ==="
find . -name "*.php" -type f | wc -l
EOF
echo ""

# 步骤5: 测试访问
echo "📍 步骤5: 测试HTTP访问"
sleep 2
curl -I http://ceshi.dhmip.cn 2>&1 | head -10
echo ""

echo "=== 修复部署完成 ==="
echo ""
echo "✅ 代码已部署到 /www/wwwroot/ceshi.dhmip.cn"
echo "✅ 文件权限已设置（www:755）"
echo ""
echo "⏳ 接下来:"
echo "1. 访问 http://ceshi.dhmip.cn/install.php 完成安装"
echo "2. 需要创建MySQL数据库"
