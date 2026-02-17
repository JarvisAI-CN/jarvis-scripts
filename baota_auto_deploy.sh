#!/bin/bash
# 宝塔面板完整部署自动化

DISPLAY=:1

echo "=== 开始宝塔面板自动化部署 ==="

# 等待页面加载
sleep 3

# 激活Firefox窗口
$DISPLAY xdotool search --sync --class "Firefox" windowactivate
sleep 2

echo "📍 步骤1: 点击【网站】菜单"
# 使用Tab键导航到侧边栏的"网站"菜单
for i in {1..10}; do
    $DISPLAY xdotool key Tab
    sleep 0.3
done
# 按Enter进入
$DISPLAY xdotool key Return
sleep 3

echo "📍 步骤2: 点击【添加站点】"
# Tab到添加站点按钮
for i in {1..5}; do
    $DISPLAY xdotool key Tab
    sleep 0.3
done
$DISPLAY xdotool key Return
sleep 2

echo "📍 步骤3: 填写域名"
# 输入域名
$DISPLAY xdotool type "ceshi.dhmip.cn"
sleep 1

# Tab到PHP版本选择
$DISPLAY xdotool key Tab
sleep 1

# 选择PHP 8.3（按几次下箭头）
for i in {1..3}; do
    $DISPLAY xdotool key Down
    sleep 0.3
done

echo "📍 步骤4: 提交表单"
# Tab到提交按钮
for i in {1..3}; do
    $DISPLAY xdotool key Tab
    sleep 0.3
done
$DISPLAY xdotool key Return
sleep 3

echo "✅ 站点创建完成！"
echo ""
echo "⏳ 接下来需要:"
echo "1. 上传代码文件"
echo "2. 配置数据库"
echo "3. 申请SSL证书"
echo ""
echo "请在VNC中确认当前状态，然后告诉我下一步操作"

# 保存当前Firefox窗口的URL供检查
$DISPLAY xdotool key Ctrl+l
sleep 1
$DISPLAY xdotool key Ctrl+c
