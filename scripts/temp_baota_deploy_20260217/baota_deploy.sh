#!/bin/bash
# 宝塔面板保质期系统部署自动化脚本

echo "=== 宝塔面板自动化部署 ==="

# 步骤1: 等待宝塔面板加载
echo "⏳ 等待Firefox加载宝塔面板..."
sleep 5

# 步骤2: 使用xdotool模拟鼠标点击和键盘输入
DISPLAY=:1 xdotool search --name "Mozilla Firefox" windowactivate

# 模拟Tab键导航到用户名输入框
echo "📍 定位用户名输入框..."
sleep 2
DISPLAY=:1 xdotool key Tab Tab

# 输入用户名（从PASSWORDS.md获取宝塔用户名）
echo "⌨️ 输入用户名..."
DISPLAY=:1 xdotool type "fs123456"
sleep 1

# Tab到密码框
DISPLAY=:1 xdotool key Tab
sleep 1

# 输入密码
echo "⌨️ 输入密码..."
DISPLAY=:1 xdotool type "Fs159753."
sleep 1

# 提交登录
DISPLAY=:1 xdotool key Return
echo "✅ 登录表单已提交"

# 等待跳转
sleep 5

echo "=== 脚本执行完成 ==="
echo "请在VNC中检查是否登录成功"
