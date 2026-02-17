#!/bin/bash
# 从宝塔配置读取MySQL密码并创建数据库

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 从宝塔读取MySQL密码 ==="
echo ""

sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 从宝塔数据库读取MySQL root密码
MYSQL_PASS=$(sqlite3 /www/server/panel/data/default.db "SELECT mysql_root FROM config LIMIT 1" 2>/dev/null | sed 's/^M$//')

if [ -z "$MYSQL_PASS" ]; then
    # 如果读取失败，尝试宝塔默认密码
    MYSQL_PASS="Fs159753."
fi

echo "MySQL root密码: $MYSQL_PASS"

# 使用读取到的密码创建数据库
mysql -uroot -p"$MYSQL_PASS" << MYSQLSCRIPT
CREATE DATABASE IF NOT EXISTS expiry_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;
MYSQLSCRIPT

if [ $? -eq 0 ]; then
    echo "✅ 数据库创建成功"
    
    # 导入数据库结构
    cd /www/wwwroot/ceshi.dhmip.cn
    mysql -uexpiry_user -pExpiry2024! expiry_system < database.sql
    
    if [ $? -eq 0 ]; then
        echo "✅ 数据库结构导入成功"
    else
        echo "⚠️ 数据库结构导入失败"
    fi
    
    # 验证
    echo ""
    echo "=== 数据库列表 ==="
    mysql -uroot -p"$MYSQL_PASS" -e "SHOW DATABASES LIKE 'expiry%';"
    
    echo ""
    echo "=== expiry_system 表 ==="
    mysql -uexpiry_user -pExpiry2024! expiry_system -e "SHOW TABLES;"
else
    echo "❌ 数据库创建失败"
fi
EOF

echo ""
echo "=== 完成 ==="
