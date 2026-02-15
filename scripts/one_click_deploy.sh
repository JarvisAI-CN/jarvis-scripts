#!/bin/bash
# 保质期管理系统 - 一键部署脚本
# 在宝塔服务器SSH中执行此脚本

set -e

echo "========================================"
echo "🚀 保质期管理系统 - 一键部署"
echo "========================================"

# 配置
DOMAIN="ceshi.dhmip.cn"
DB_NAME="expiry_system"
DB_USER="expiry_user"
DB_PASS="Expiry@2026System!"
WEB_ROOT="/www/wwwroot/$DOMAIN"
DEPLOY_SRC="/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"

echo ""
echo "📋 配置信息："
echo "   域名: $DOMAIN"
echo "   数据库: $DB_NAME"
echo "   用户: $DB_USER"
echo "   网站目录: $WEB_ROOT"
echo "========================================"

# 第一步：创建数据库
echo ""
echo "📍 步骤1: 创建数据库..."
mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF
echo "✅ 数据库创建完成"

# 第二步：导入数据结构
echo ""
echo "📍 步骤2: 导入数据结构..."
if [ -f "$DEPLOY_SRC/database.sql" ]; then
    mysql -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$DEPLOY_SRC/database.sql"
    echo "✅ 数据导入完成"
else
    echo "⚠️  SQL文件不存在，跳过导入"
fi

# 第三步：清理网站目录
echo ""
echo "📍 步骤3: 清理网站目录..."
cd "$WEB_ROOT"
rm -f index.html index.htm
echo "✅ 默认文件已清理"

# 第四步：上传PHP文件
echo ""
echo "📍 步骤4: 上传网站文件..."
cp "$DEPLOY_SRC/index.php" "$WEB_ROOT/"
cp "$DEPLOY_SRC/db.php" "$WEB_ROOT/"
chmod 644 "$WEB_ROOT"/*.php
chown www:www "$WEB_ROOT"/*.php
echo "✅ 文件上传完成"

# 第五步：测试访问
echo ""
echo "📍 步骤5: 测试部署..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 网站响应正常 (HTTP $HTTP_CODE)"
else
    echo "⚠️  网站响应异常 (HTTP $HTTP_CODE)"
fi

# 数据库连接测试
echo ""
echo "📍 步骤6: 测试数据库连接..."
php -r "
\$conn = new mysqli('localhost', '$DB_USER', '$DB_PASS', '$DB_NAME');
if (\$conn->connect_error) {
    exit(1);
}
echo '✅ 数据库连接成功';
\$conn->close();
" 2>/dev/null || echo "⚠️  数据库连接失败"

# 完成
echo ""
echo "========================================"
echo "🎉 部署完成！"
echo "========================================"
echo ""
echo "🌐 访问地址："
echo "   http://$DOMAIN"
echo ""
echo "📊 数据库信息："
echo "   数据库名: $DB_NAME"
echo "   用户名: $DB_USER"
echo "   密码: $DB_PASS"
echo ""
echo "🧪 测试账号："
echo "   SKU: 6901234567890 → 可口可乐 500ml"
echo "   SKU: 6901234567891 → 康师傅红烧牛肉面"
echo ""
echo "========================================"
echo "💡 提示："
echo "   1. 扫码功能需要HTTPS（申请Let's Encrypt证书）"
echo "   2. 管理员密码: $DB_PASS"
echo "   3. 日志位置: 网站日志 → 错误日志"
echo "========================================"
