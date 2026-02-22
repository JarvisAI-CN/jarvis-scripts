#!/bin/bash
# 保质期管理系统 v3.0.0 快速部署脚本
# 在服务器上执行此脚本

echo "🚀 开始部署保质期管理系统 v3.0.0..."

# 进入网站目录
cd /www/wwwroot/pandian.dhmip.cn/public_html/

# 备份旧文件
echo "📦 备份旧文件..."
if [ -f "index.php" ]; then
    cp index.php index_v2.14.2_backup_$(date +%Y%m%d_%H%M%S).php
    echo "✅ 已备份 index.php"
fi

# 创建includes目录
echo "📁 创建includes目录..."
mkdir -p includes

# 下载新文件
echo "⬇️  下载新文件..."

# 下载主要文件
curl -o login.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/login.php
curl -o inventory.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/inventory.php
curl -o history.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/history.php
curl -o logout.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/logout.php
curl -o index.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/index.php

# 下载includes文件
curl -o includes/db.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/includes/db.php
curl -o includes/check_login.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/includes/check_login.php
curl -o includes/header.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/includes/header.php
curl -o includes/footer.php https://raw.githubusercontent.com/JarvisAI-CN/expiry-management-system/master/includes/footer.php

echo ""
echo "✅ 部署完成！"
echo "👉 访问: http://pandian.dhmip.cn/login.php"
echo ""
echo "如果需要回滚，恢复备份文件："
echo "  cp index_v2.14.2_backup_*.php index.php"
