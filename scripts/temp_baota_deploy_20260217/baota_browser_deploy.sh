#!/bin/bash
# 宝塔面板自动化部署 - 通过VNC浏览器

export DISPLAY=:1

echo "=== 宝塔面板自动化部署开始 ==="

# 步骤1: 打开/激活Firefox并访问宝塔面板
echo "📍 步骤1: 访问宝塔面板"
firefox --new-tab http://82.157.20.7:8888/fs123456 &
sleep 5

# 激活Firefox窗口
xdotool search --sync --class "Firefox" windowactivate
sleep 2

# 步骤2: 登录宝塔面板
echo "📍 步骤2: 输入登录信息"

# Tab到用户名输入框并输入
for i in {1..3}; do
    xdotool key Tab
    sleep 0.2
done
xdotool type "fs123456"
sleep 1

# Tab到密码框并输入
xdotool key Tab
sleep 1
xdotool type "Fs159753."
sleep 1

# 提交登录
xdotool key Return
echo "✅ 登录表单已提交"
sleep 8

# 步骤3: 导航到网站菜单
echo "📍 步骤3: 点击【网站】菜单"
# 使用Alt+快捷键或Tab导航
xdotool key Alt+Left
sleep 1
for i in {1..5}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 3

# 步骤4: 添加站点
echo "📍 步骤4: 点击【添加站点】"
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

# 步骤5: 填写域名
echo "📍 步骤5: 填写域名 ceshi.dhmip.cn"
xdotool type "ceshi.dhmip.cn"
sleep 1

# 步骤6: 选择PHP版本
xdotool key Tab
sleep 1
for i in {1..2}; do
    xdotool key Down
    sleep 0.3
done

# 步骤7: 提交表单
echo "📍 步骤6: 提交站点创建"
for i in {1..5}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 5

echo "=== 基础步骤完成 ==="
echo "⏳ 接下来需要:"
echo "1. 在宝塔文件管理器中使用Git克隆"
echo "2. 配置数据库"
echo "3. 申请SSL证书"
echo ""
echo "请在VNC中查看当前状态，然后告诉我继续"
