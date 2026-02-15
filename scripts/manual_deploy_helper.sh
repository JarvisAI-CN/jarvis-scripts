#!/bin/bash
# 保质期管理系统 - 宝塔面板自动部署（bash版本）
export DISPLAY=:1

echo "========================================"
echo "🚀 保质期管理系统 - 自动部署"
echo "========================================"

# 第一步：启动Firefox
echo ""
echo "📍 步骤1: 启动Firefox浏览器..."
firefox http://82.157.20.7:8888/fs123456 &
FIREFOX_PID=$!
echo "✅ Firefox已启动 (PID: $FIREFOX_PID)"
echo "   等待页面加载..."
sleep 10

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_01_browser.png
echo "📸 截图: vnc_01_browser.png"

# 第二步：等待用户手动登录
echo ""
echo "========================================"
echo "📍 步骤2: 请在VNC中登录宝塔面板"
echo "========================================"
echo ""
echo "登录信息："
echo "  用户名: fs123"
echo "  密码: fs123456"
echo ""
echo "登录后，按回车继续..."
read -p ""

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_02_after_login.png
echo "📸 截图: vnc_02_after_login.png"

# 第三步：进入数据库管理
echo ""
echo "========================================"
echo "📍 步骤3: 创建数据库"
echo "========================================"
echo ""
echo "请在宝塔面板中："
echo "1. 点击左侧 '数据库' 菜单"
echo "2. 点击 '添加数据库'"
echo "3. 填写："
echo "   - 数据库名: expiry_system"
echo "   - 用户名: expiry_user"
echo "   - 密码: Expiry@2026System!"
echo "   - 访问权限: 本地服务器"
echo "4. 点击 '提交'"
echo ""
echo "完成后，按回车继续..."
read -p ""

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_03_database.png
echo "📸 截图: vnc_03_database.png"

# 第四步：导入SQL
echo ""
echo "========================================"
echo "📍 步骤4: 导入数据库结构"
echo "========================================"
echo ""
echo "请在宝塔面板中："
echo "1. 点击刚创建的数据库名 'expiry_system'"
echo "2. 点击 '导入' 标签"
echo "3. 点击 '从本地上传'"
echo "4. 选择文件："
echo "   /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/database.sql"
echo "5. 点击 '导入'"
echo ""
echo "完成后，按回车继续..."
read -p ""

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_04_sql_imported.png
echo "📸 截图: vnc_04_sql_imported.png"

# 第五步：上传网站文件
echo ""
echo "========================================"
echo "📍 步骤5: 上传网站文件"
echo "========================================"
echo ""
echo "请在宝塔面板中："
echo "1. 点击左侧 '网站' 菜单"
echo "2. 找到 'ceshi.dhmip.cn'"
echo "3. 点击 '根目录' 按钮"
echo "4. 删除默认的 index.html（如果存在）"
echo "5. 点击 '上传' 按钮"
echo "6. 上传以下2个文件："
echo "   - index.php"
echo "   - db.php"
echo ""
echo "文件位置："
echo "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/"
echo ""
echo "完成后，按回车继续..."
read -p ""

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_05_files_uploaded.png
echo "📸 截图: vnc_05_files_uploaded.png"

# 第六步：测试访问
echo ""
echo "========================================"
echo "📍 步骤6: 测试访问"
echo "========================================"
echo ""
echo "✅ 部署完成！"
echo ""
echo "测试访问："
echo "  http://ceshi.dhmip.cn"
echo ""
echo "测试账号："
echo "  SKU: 6901234567890 → 可口可乐 500ml"
echo "  SKU: 6901234567891 → 康师傅红烧牛肉面"
echo ""
echo "========================================"
echo "🎉 部署流程结束"
echo "========================================"

# 最终截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/vnc_06_complete.png
echo "📸 截图: vnc_06_complete.png"
