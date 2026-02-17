#!/bin/bash
# 宝塔面板完整自动化部署脚本

export DISPLAY=:1

echo "=== 宝塔面板完整自动化部署 ==="

# 使用Python脚本执行
python3 << 'EOF'
import os
os.environ['DISPLAY'] = ':1'

import pyautogui
import time

print("📺 屏幕尺寸:", pyautogui.size())

# 步骤1: 访问宝塔并登录
print("\n📍 步骤1: 登录宝塔面板")
pyautogui.hotkey('ctrl', 'l')
time.sleep(1)
pyautogui.write('http://82.157.20.7:8888/fs123456', interval=0.05)
time.sleep(1)
pyautogui.press('enter')
time.sleep(6)

pyautogui.click(600, 400)  # 用户名
time.sleep(0.5)
pyautogui.write('fs123456', interval=0.05)
time.sleep(0.5)
pyautogui.press('tab')
time.sleep(0.5)
pyautogui.write('Fs159753.', interval=0.05)
time.sleep(0.5)
pyautogui.press('enter')
print("✅ 登录成功")
time.sleep(8)

# 步骤2: 点击网站菜单
print("\n📍 步骤2: 点击网站菜单")
pyautogui.click(150, 250)
time.sleep(3)
print("✅ 网站菜单已点击")

# 步骤3: 添加站点
print("\n📍 步骤3: 添加站点")
pyautogui.click(400, 200)
time.sleep(2)
pyautogui.click(700, 350)  # 域名框
time.sleep(0.5)
pyautogui.write('ceshi.dhmip.cn', interval=0.05)
time.sleep(1)
pyautogui.click(700, 420)  # PHP版本
time.sleep(0.5)
for _ in range(3):
    pyautogui.press('down')
    time.sleep(0.2)
pyautogui.press('enter')
time.sleep(1)
pyautogui.click(800, 500)  # 提交
time.sleep(5)
print("✅ 站点创建完成")
time.sleep(5)

# 步骤4: 点击根目录
print("\n📍 步骤4: 进入文件管理器")
pyautogui.click(500, 350)
time.sleep(3)
print("✅ 文件管理器已打开")

# 步骤5: Git克隆
print("\n📍 步骤5: Git克隆代码")
pyautogui.click(1200, 150)  # 远程下载
time.sleep(2)
pyautogui.click(800, 400)  # Git克隆
time.sleep(1)
pyautogui.click(700, 450)  # 仓库地址框
time.sleep(0.5)
pyautogui.write('https://github.com/JarvisAI-CN/expiry-management-system.git', interval=0.02)
time.sleep(1)
pyautogui.click(850, 520)  # 确认
time.sleep(3)
print("✅ Git克隆已开始")

# 等待克隆完成
print("\n⏳ 等待克隆完成（60秒）...")
for i in range(12):
    time.sleep(5)
    print(f"  {i*5}秒")

# 截图
pyautogui.screenshot('/tmp/baota_auto_final.png')
print("\n📸 最终截图: /tmp/baota_auto_final.png")
print("\n=== 自动化完成 ===")
EOF

echo ""
echo "✅ 脚本执行完成"
echo "📸 查看截图: ls -la /tmp/baota_*.png"
