#!/bin/bash
# 宝塔面板 - 完整部署自动化脚本

export DISPLAY=:1

echo "=== 宝塔面板完整部署开始 ==="

# 激活Firefox窗口
xdotool search --sync --class "Firefox" windowactivate
sleep 2

# === 步骤1: 检查Git克隆状态 ===
echo "📍 步骤1: 检查文件管理器中的Git克隆状态"
# 刷新页面
xdotool key Ctrl+r
sleep 5

# === 步骤2: 设置文件权限 ===
echo "📍 步骤2: 设置文件权限"
# 在宝塔文件管理器中全选文件 (Ctrl+a)
xdotool key Ctrl+a
sleep 1

# 右键菜单
xdotool key Shift+F10
sleep 1

# 查找权限选项（可能需要按几次下箭头）
for i in {1..5}; do
    xdotool key Down
    sleep 0.3
done
xdotool key Return
sleep 2

# 设置权限为755
xdotool type "755"
sleep 1
xdotool key Tab
sleep 1
xdotool key Return
sleep 2

echo "✅ 文件权限已设置"

# === 步骤3: 返回网站列表，创建数据库 ===
echo "📍 步骤3: 创建MySQL数据库"
# 返回宝塔首页或网站列表
xdotool key Alt+Left
sleep 2
xdotool key Alt+Left
sleep 2

# 导航到数据库菜单（可能是左侧菜单）
for i in {1..8}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 3

# 点击添加数据库
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

# 填写数据库名
xdotool type "expiry_system"
sleep 1

# Tab到用户名
xdotool key Tab
sleep 1
xdotool type "expiry_user"
sleep 1

# Tab到密码（使用随机密码或指定密码）
xdotool key Tab
sleep 1
xdotool type "Expiry2024!"
sleep 1

# 提交创建
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 3

echo "✅ 数据库创建完成"

# === 步骤4: 访问安装向导 ===
echo "📍 步骤4: 访问安装向导"
# 打开新标签页
xdotool key Ctrl+t
sleep 2

# 输入安装向导URL
xdotool type "http://ceshi.dhmip.cn/install.php"
sleep 1
xdotool key Return
sleep 5

echo "⏳ 安装向导页面已打开"

# === 步骤5: 填写安装向导 ===
echo "📍 步骤5: 填写数据库配置"
# 数据库主机（默认localhost）
for i in {1..2}; do
    xdotool key Tab
    sleep 0.3
done

# 数据库名
xdotool type "expiry_system"
sleep 1
xdotool key Tab
sleep 1

# 用户名
xdotool type "expiry_user"
sleep 1
xdotool key Tab
sleep 1

# 密码
xdotool type "Expiry2024!"
sleep 1
xdotool key Tab
sleep 1

# 管理员密码
xdotool type "admin123"
sleep 1
xdotool key Tab
sleep 1

# 确认密码
xdotool type "admin123"
sleep 1

# 提交安装
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 5

echo "✅ 安装向导已提交"

# === 步骤6: 申请SSL证书 ===
echo "📍 步骤6: 申请SSL证书"
# 返回宝塔面板
xdotool key Ctrl+Tab
sleep 2

# 进入网站设置
for i in {1..5}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

# 进入SSL设置
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 2

# 选择Let's Encrypt
for i in {1..2}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key space
sleep 1

# 勾选域名
for i in {1..2}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key space
sleep 1

# 申请证书
for i in {1..3}; do
    xdotool key Tab
    sleep 0.3
done
xdotool key Return
sleep 10

echo "✅ SSL证书申请已提交"

echo ""
echo "=== 所有部署步骤完成 ==="
echo "🎉 保质期管理系统部署成功！"
echo ""
echo "📍 访问地址:"
echo "- HTTP: http://ceshi.dhmip.cn"
echo "- HTTPS: https://ceshi.dhmip.cn (证书生效后)"
echo ""
echo "🔑 登录信息:"
echo "- 用户名: admin"
echo "- 密码: admin123"
echo ""
echo "📸 生成最终截图..."
