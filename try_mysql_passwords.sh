#!/bin/bash
# 尝试多种MySQL密码并创建数据库

SERVER="root@82.157.20.7"
PASSWORD="Fs123456."

echo "=== 尝试多种MySQL密码 ==="
echo ""

# 密码列表
PASSWORDS=("admin" "Fs159753." "Fs123456." "" "123456" "password")

for mysql_pass in "${PASSWORDS[@]}"; do
    echo "尝试密码: '$mysql_pass'"
    
    result=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
if [ -z "$mysql_pass" ]; then
    mysql -uroot -e "SELECT VERSION();" 2>&1 | grep -v "ERROR" | grep -v "Warning"
else
    mysql -uroot -p"$mysql_pass" -e "SELECT VERSION();" 2>&1 | grep -v "ERROR" | grep -v "Warning"
fi
EOF
)
    
    if echo "$result" | grep -q "VERSION"; then
        echo "✅ 找到正确密码: '$mysql_pass'"
        
        # 创建数据库
        sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
mysql -uroot ${mysql_pass:+-p"$mysql_pass"} << MYSQLSCRIPT
CREATE DATABASE IF NOT EXISTS expiry_system CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;
MYSQLSCRIPT

cd /www/wwwroot/ceshi.dhmip.cn
mysql -uexpiry_user -pExpiry2024! expiry_system < database.sql 2>&1 | grep -v "Warning"

echo "=== 验证 ==="
mysql -uexpiry_user -pExpiry2024! expiry_system -e "SHOW TABLES;" 2>&1 | grep -v "Warning"
EOF
        
        if [ $? -eq 0 ]; then
            echo "✅ 数据库配置成功！"
            exit 0
        fi
    fi
done

echo "❌ 所有密码都失败了"
