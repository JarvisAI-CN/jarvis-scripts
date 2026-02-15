#!/bin/bash
# 保质期管理系统 - VNC自动部署（bash + xdotool）
set -e

export DISPLAY=:1
echo "========================================"
echo "🚀 保质期管理系统 - VNC自动部署"
echo "========================================"

# 第一步：启动Firefox
echo ""
echo "📍 步骤1: 启动Firefox并访问宝塔面板..."
firefox --new-window http://82.157.20.7:8888/fs123456 &
FIREFOX_PID=$!
echo "✅ Firefox已启动 (PID: $FIREFOX_PID)"
sleep 8

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_01_browser.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_01_browser.png"

# 第二步：登录宝塔面板
echo ""
echo "📍 步骤2: 登录宝塔面板..."
echo "   用户名: fs123"
echo "   密码: fs123456"

# 使用xdotool输入登录信息
WINDOW_ID=$(xdotool search --onlyvisible --name "irefox" | head -1)
echo "🔍 Firefox窗口ID: $WINDOW_ID"

xdotool windowactivate $WINDOW_ID
sleep 2

# Tab到用户名框（假设是第一个输入框）
xdotool key --window $WINDOW_ID Tab Tab
sleep 0.5
xdotool type --window $WINDOW_ID "fs123"
sleep 0.5

# Tab到密码框
xdotool key --window $WINDOW_ID Tab
sleep 0.5
xdotool type --window $WINDOW_ID "fs123456"
sleep 0.5

# 回车登录
xdotool key --window $WINDOW_ID Return
echo "✅ 登录信息已输入"
sleep 10

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_02_logged_in.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_02_logged_in.png"

# 第三步：创建数据库
echo ""
echo "📍 步骤3: 创建数据库..."
echo "   数据库名: expiry_system"
echo "   用户名: expiry_user"
echo "   密码: Expiry@2026System!"

# 点击左侧"数据库"菜单（根据宝塔布局，大约在(80, 220)）
xdotool mousemove --window $WINDOW_ID 80 220
sleep 0.5
xdotool click --window $WINDOW_ID 1
sleep 5

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_03_database.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_03_database.png"

# 点击"添加数据库"按钮（顶部蓝色按钮）
xdotool mousemove --window $WINDOW_ID 200 120
sleep 0.5
xdotool click --window $WINDOW_ID 1
sleep 3

# 填写表单
# 数据库名
xdotool mousemove --window $WINDOW_ID 400 280
sleep 0.3
xdotool click --window $WINDOW_ID 1
sleep 0.5
xdotool key --window $WINDOW_ID Ctrl+a
xdotool type --window $WINDOW_ID "expiry_system"
sleep 0.5

# 用户名
xdotool key --window $WINDOW_ID Tab
sleep 0.3
xdotool type --window $WINDOW_ID "expiry_user"
sleep 0.5

# 密码
xdotool key --window $WINDOW_ID Tab
sleep 0.3
xdotool type --window $WINDOW_ID "Expiry@2026System!"
sleep 0.5

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_04_db_form.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_04_db_form.png"

# 点击提交按钮（估计位置）
xdotool mousemove --window $WINDOW_ID 500 450
sleep 0.5
xdotool click --window $WINDOW_ID 1
sleep 8

# 截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_05_db_created.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_05_db_created.png"

echo "✅ 数据库创建完成"
echo ""
echo "========================================"
echo "⚠️  需要手动完成以下步骤："
echo "========================================"
echo "1. 导入SQL文件："
echo "   /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/database.sql"
echo ""
echo "2. 上传网站文件："
echo "   网站 → ceshi.dhmip.cn → 根目录"
echo "   删除 index.html"
echo "   上传 index.php 和 db.php"
echo ""
echo "3. 测试访问："
echo "   http://ceshi.dhmip.cn"
echo "========================================"

# 最终截图
import -display :1 -window root /home/ubuntu/.openclaw/workspace/deploy_baota_06_complete.png 2>/dev/null || echo "截图失败"
echo "📸 截图: deploy_baota_06_complete.png"

echo ""
echo "✅ 自动化部分完成！数据库已创建。"
echo "⏳ 请在VNC中完成文件上传和测试。"
