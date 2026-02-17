#!/bin/bash
# 宝塔面板 - Git克隆代码

export DISPLAY=:1

echo "=== Git克隆代码开始 ==="

# 激活Firefox窗口
xdotool search --sync --class "Firefox" windowactivate
sleep 2

echo "📍 步骤1: 点击网站列表中的【根目录】链接"
# 模拟点击或Tab导航到网站根目录
for i in {1..10}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 3

echo "📍 步骤2: 进入文件管理器"
# 等待文件管理器加载
sleep 3

echo "📍 步骤3: 点击【远程下载】按钮"
# Tab到远程下载按钮
for i in {1..8}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

echo "📍 步骤4: 选择【Git克隆】"
# 在弹出的对话框中选择Git克隆
xdotool key Tab
sleep 1
xdotool key Return
sleep 2

echo "📍 步骤5: 输入GitHub仓库地址"
# 输入仓库URL
xdotool type "https://github.com/JarvisAI-CN/expiry-management-system.git"
sleep 1

# Tab到确认按钮
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return

echo "✅ Git克隆命令已提交"
echo "⏳ 请等待克隆完成（可能需要1-2分钟）"
sleep 10

echo "=== Git克隆步骤完成 ==="
echo "接下来需要:"
echo "1. 设置文件权限"
echo "2. 配置数据库"
echo "3. 访问安装向导"
