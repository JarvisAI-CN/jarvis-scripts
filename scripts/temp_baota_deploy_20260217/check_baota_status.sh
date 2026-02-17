#!/bin/bash
# 检查宝塔面板和网站状态

export DISPLAY=:1

echo "=== 检查宝塔面板状态 ==="

# 激活Firefox
xdotool search --sync --class "Firefox" windowactivate
sleep 2

# 打开新标签访问宝塔面板
xdotool key Ctrl+t
sleep 2
xdotool type "http://82.157.20.7:8888/fs123456"
sleep 1
xdotool key Return
sleep 5

echo "✅ 宝塔面板已打开"
echo "⏳ 等待加载..."

sleep 5

# 截图
ffmpeg -f x11grab -r 1 -s 1920x1080 -i :1 -frames:v 1 /tmp/baota_check.jpg -y 2>&1 | tail -3

echo "📸 截图已保存: /tmp/baota_check.jpg"
echo ""
echo "需要检查:"
echo "1. 网站列表中 ceshi.dhmip.cn 是否存在"
echo "2. 根目录是否有文件"
echo "3. Git克隆是否成功"
