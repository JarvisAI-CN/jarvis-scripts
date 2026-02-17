#!/bin/bash
# 创建数据库和表（如果不存在）

echo "=== 配置保质期系统数据库 ==="

# 远程服务器
REMOTE_HOST="82.157.20.7"
REMOTE_USER="root"
REMOTE_PASS="Fs123456."

echo "📊 步骤1: 创建数据库"
sshpass -p "${REMOTE_PASS}" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
# 连接MySQL并创建数据库和表
mysql -u root -p"Fs159753." << 'EOF'
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS expiry_system DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE expiry_system;

-- 创建items表
CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '物品名称',
    expiry_date DATE NOT NULL COMMENT '过期日期',
    category VARCHAR(100) COMMENT '分类',
    quantity INT DEFAULT 1 COMMENT '数量',
    location VARCHAR(255) COMMENT '存放位置',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_expiry_date (expiry_date),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='保质期物品表';

-- 插入示例数据
INSERT INTO items (name, expiry_date, category, quantity, location) VALUES
('测试物品1', DATE_ADD(CURDATE(), INTERVAL 5 DAY), '食品', 10, '货架A'),
('测试物品2', DATE_ADD(CURDATE(), INTERVAL 15 DAY), '饮料', 20, '货架B'),
('测试物品3', DATE_ADD(CURDATE(), INTERVAL 35 DAY), '日用品', 5, '货架C');

-- 创建用户（如果不存在）
CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry2024!';

-- 授权
GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';
FLUSH PRIVILEGES;

-- 显示表
SHOW TABLES;
SELECT COUNT(*) as item_count FROM items;
EOF
ENDSSH

if [ $? -eq 0 ]; then
    echo "✅ 数据库配置完成"
else
    echo "❌ 数据库配置失败"
fi

echo ""
echo "📋 步骤2: 验证配置"
sshpass -p "${REMOTE_PASS}" ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
echo "=== 数据库列表 ==="
mysql -u expiry_user -p"Expiry2024!" expiry_system -e "SHOW TABLES;"
echo ""
echo "=== 示例数据 ==="
mysql -u expiry_user -p"Expiry2024!" expiry_system -e "SELECT * FROM items LIMIT 5;"
ENDSSH

echo ""
echo "✅ 配置完成！数据库和表已创建，可以运行优化版本代码了。"
