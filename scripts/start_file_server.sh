#!/bin/bash
# 启动临时文件服务器用于传输部署文件
# 在宝塔服务器上可以通过curl下载文件

echo "========================================"
echo "📡 启动临时文件服务器"
echo "========================================"
echo ""
echo "服务器地址: http://10.7.0.5:8888"
echo "文件位置: /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"
echo ""
echo "可用文件："
ls -lh /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/*.php
echo ""
echo "========================================"
echo "📋 在宝塔服务器上下载文件："
echo "========================================"
echo ""
echo "# 方法1：使用curl（推荐）"
echo "cd /www/wwwroot/ceshi.dhmip.cn"
echo "curl http://10.7.0.5:8888/index.php -o index.php"
echo "curl http://10.7.0.5:8888/db.php -o db.php"
echo "chmod 644 *.php"
echo ""
echo "# 方法2：使用wget"
echo "cd /www/wwwroot/ceshi.dhmip.cn"
echo "wget http://10.7.0.5:8888/index.php"
echo "wget http://10.7.0.5:8888/db.php"
echo "chmod 644 *.php"
echo ""
echo "========================================"
echo "💡 文件服务器将持续运行"
echo "按 Ctrl+C 停止服务器"
echo "========================================"

cd /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package
python3 -m http.server 8888
