#!/bin/bash
# 宝塔面板完整部署自动化 v2

echo "=== 开始宝塔面板自动化部署 ==="

export DISPLAY=:1

# 等待页面加载
sleep 3

# 激活Firefox窗口
xdotool search --sync --class "Firefox" windowactivate
sleep 2

echo "📍 步骤1: 点击【网站】菜单"
# 使用Tab键导航到侧边栏的"网站"菜单
for i in {1..10}; do
    xdotool key Tab
    sleep 0.3
done
# 按Enter进入
xdotool key Return
sleep 3

echo "📍 步骤2: 点击【添加站点】"
# Tab到添加站点按钮
for i in {1..5}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

echo "📍 步骤3: 填写域名"
# 输入域名
xdotool type "ceshi.dhmip.cn"
sleep 1

# Tab到PHP版本选择
xdotool key Tab
sleep 1

# 选择PHP 8.3（按几次下箭头）
for i in {1..3}; do
    xdotool key Down
    sleep 0.3
done

echo "📍 步骤4: 提交表单"
# Tab到提交按钮
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 3

echo "✅ 操作完成！请检查VNC中的状态"

# 再次截图
ffmpeg -f x11grab -r 1 -s 1920x1080 -i :1 -frames:v 1 /tmp/vnc_after.jpg -y 2>&1 | tail -3
echo "📸 新截图已保存: /tmp/vnc_after.jpg"
