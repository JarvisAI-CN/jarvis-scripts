#!/bin/bash
# 保质期管理系统 - 一键完成脚本
# 在宝塔终端中执行此脚本

echo "========================================"
echo "🚀 保质期管理系统 - 一键部署"
echo "========================================"
echo ""
echo "📡 从文件服务器下载..."
echo ""

# 进入网站目录
cd /www/wwwroot/ceshi.dhmip.cn || exit 1

# 下载文件
echo "📥 下载 index.php..."
curl -s http://10.7.0.5:8888/index.php -o index.php
echo "✅ index.php"

echo "📥 下载 db.php..."
curl -s http://10.7.0.5:8888/db.php -o db.php
echo "✅ db.php"

# 设置权限
echo ""
echo "🔧 设置权限..."
chmod 644 *.php
chown www:www *.php
echo "✅ 权限设置完成"

# 验证
echo ""
echo "📋 文件列表:"
ls -lh *.php

echo ""
echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo "🌐 访问: http://ceshi.dhmip.cn"
echo ""
echo "🧪 测试:"
echo "   SKU: 6901234567890 → 可口可乐"
echo "========================================"
