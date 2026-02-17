#!/bin/bash
# 检查MySQL状态并使用宝塔API创建数据库

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 检查MySQL状态 ==="
echo ""

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 检查MySQL服务
systemctl status mysql 2>/dev/null || systemctl status mariadb 2>/dev/null || echo "MySQL服务未找到"

# 检查MySQL进程
ps aux | grep -E "mysql|mariadb" | grep -v grep | head -5

# 检查MySQL端口
netstat -tlnp | grep 3306 || echo "3306端口未监听"

# 检查宝塔MySQL配置
if [ -f /etc/my.cnf ]; then
    echo "=== MySQL配置文件 ==="
    cat /etc/my.cnf | grep -A5 "client"
fi

# 检查MySQL socket
ls -la /var/run/mysqld/mysqld.sock 2>/dev/null || ls -la /var/lib/mysql/mysql.sock 2>/dev/null || echo "MySQL socket未找到"
EOF

echo ""
echo "=== 测试系统是否实际可用 ==="
curl -s http://ceshi.dhmip.cn 2>&1 | grep -o "保质期管理"

echo ""
echo "=== 检查是否有SQLite数据库 ==="
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
cd /www/wwwroot/ceshi.dhmip.cn
ls -la *.db 2>/dev/null || echo "无SQLite数据库"
ls -la *.sqlite 2>/dev/null || echo "无SQLite文件"
EOF

echo ""
echo "=== 查看系统错误日志 ==="
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 查看Nginx错误日志
tail -20 /www/wwwlogs/ceshi.dhmip.cn.log 2>/dev/null || echo "无Nginx日志"
EOF
