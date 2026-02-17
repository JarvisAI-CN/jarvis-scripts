#!/bin/bash
# 使用宝塔MySQL密码修复数据库

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 修复数据库配置 ==="
echo ""

# 尝试使用宝塔默认MySQL密码
echo "📍 尝试连接MySQL（宝塔默认密码）"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << 'EOF'
# 方法1: 尝试空密码
mysql -uroot -e "SELECT VERSION();" 2>&1 | grep -v "ERROR"
if [ $? -eq 0 ]; then
    echo "✅ MySQL root无密码"
    MYSQL_PASS=""
else
    # 方法2: 尝试宝塔默认密码
    mysql -uroot -pFs159753. -e "SELECT VERSION();" 2>&1 | grep -v "ERROR"
    if [ $? -eq 0 ]; then
        echo "✅ MySQL root密码: Fs159753."
        MYSQL_PASS="Fs159753."
    else
        # 方法3: 从宝塔配置文件读取
        if [ -f /www/server/panel/data/default.db ]; then
            echo "⏳ 尝试从宝塔读取密码..."
            # 这里需要sqlite3
        fi
    fi
fi
EOF

# 创建数据库和用户（使用可能的密码）
echo ""
echo "📍 创建数据库和用户"
for pass in "" "Fs159753." "Fs123456."; do
    echo "尝试密码: $pass"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
mysql -uroot ${pass:+"-p$pass"} -e "
CREATE DATABASE IF NOT EXISTS expiry_system CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;
SHOW DATABASES LIKE 'expiry%';
" 2>&1 | grep -v "Warning"
EOF
    if [ $? -eq 0 ]; then
        echo "✅ 成功！"
        break
    fi
done
echo ""
