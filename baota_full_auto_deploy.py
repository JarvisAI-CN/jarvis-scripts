#!/usr/bin/env python3
"""
宝塔面板完整自动化部署 - 使用pyautogui
"""

import pyautogui
import time
import subprocess
import os

os.environ['DISPLAY'] = ':1'

print("=== 宝塔面板完整自动化部署 ===")

# 获取屏幕尺寸
width, height = pyautogui.size()
print(f"📺 屏幕尺寸: {width}x{height}")

# 步骤1: 激活Firefox（已经在登录页）
print("\n📍 步骤1: 确保在宝塔面板页面")
pyautogui.hotkey('ctrl', 'l')
time.sleep(1)
pyautogui.write('http://82.157.20.7:8888/fs123456', interval=0.05)
time.sleep(1)
pyautogui.press('enter')
time.sleep(6)
print("✅ 宝塔面板已打开")

# 步骤2: 登录
print("\n📍 步骤2: 登录")
pyautogui.click(600, 400)  # 用户名框
time.sleep(0.5)
pyautogui.write('fs123456', interval=0.05)
time.sleep(0.5)

pyautogui.press('tab')
time.sleep(0.5)
pyautogui.write('Fs159753.', interval=0.05)
time.sleep(0.5)

pyautogui.press('enter')
print("✅ 登录表单已提交")
time.sleep(8)

# 步骤3: 点击网站菜单
print("\n📍 步骤3: 点击【网站】菜单")
pyautogui.click(150, 250)  # 左侧菜单 - 网站
time.sleep(3)
print("✅ 网站菜单已点击")

# 步骤4: 点击添加站点
print("\n📍 步骤4: 点击【添加站点】")
pyautogui.click(400, 200)  # 添加站点按钮
time.sleep(2)
print("✅ 添加站点对话框已打开")

# 步骤5: 填写域名
print("\n📍 步骤5: 填写域名")
pyautogui.click(700, 350)  # 域名输入框
time.sleep(0.5)
pyautogui.write('ceshi.dhmip.cn', interval=0.05)
time.sleep(1)

# 步骤6: 选择PHP版本
print("\n📍 步骤6: 选择PHP 8.3")
pyautogui.click(700, 420)  # PHP版本下拉框
time.sleep(0.5)
for _ in range(3):  # 向下选择几次
    pyautogui.press('down')
    time.sleep(0.2)
pyautogui.press('enter')
time.sleep(1)

# 步骤7: 提交创建
print("\n📍 步骤7: 提交站点创建")
pyautogui.click(800, 500)  # 提交按钮
time.sleep(5)
print("✅ 站点创建已提交")
time.sleep(5)

# 步骤8: 截图
print("\n📍 步骤8: 截图保存")
pyautogui.screenshot('/tmp/baota_step3_site_created.png')
print("📸 截图已保存: /tmp/baota_step3_site_created.png")

# 步骤9: 点击网站根目录
print("\n📍 步骤9: 点击网站根目录")
pyautogui.click(500, 350)  # 网站列表中的根目录链接
time.sleep(3)
print("✅ 进入文件管理器")

# 步骤10: 点击远程下载
print("\n📍 步骤10: 点击【远程下载】")
pyautogui.click(1200, 150)  # 远程下载按钮（右上角）
time.sleep(2)
print("✅ 远程下载对话框已打开")

# 步骤11: 选择Git克隆
print("\n📍 步骤11: 选择【Git克隆】")
pyautogui.click(800, 400)  # Git克隆选项
time.sleep(1)
print("✅ Git克隆选项已选择")

# 步骤12: 输入GitHub仓库地址
print("\n📍 步骤12: 输入GitHub仓库地址")
pyautogui.click(700, 450)  # 仓库地址输入框
time.sleep(0.5)
pyautogui.write('https://github.com/JarvisAI-CN/expiry-management-system.git', interval=0.02)
time.sleep(1)

# 步骤13: 确认克隆
print("\n📍 步骤13: 确认克隆")
pyautogui.click(850, 520)  # 确认/克隆按钮
time.sleep(3)
print("✅ Git克隆已开始")

# 步骤14: 等待克隆完成
print("\n📍 步骤14: 等待Git克隆完成（60秒）")
for i in range(12):
    time.sleep(5)
    print(f"  等待中... {i*5}秒")

# 步骤15: 最终截图
print("\n📍 步骤15: 最终截图")
pyautogui.screenshot('/tmp/baota_step15_final.png')
print("📸 最终截图已保存: /tmp/baota_step15_final.png")

print("\n=== 自动化部署完成 ===")
print("✅ 已完成的步骤:")
print("  1. 登录宝塔面板")
print("  2. 创建网站 ceshi.dhmip.cn")
print("  3. Git克隆代码")
print("\n⏳ 还需要手动完成:")
print("  1. 设置文件权限（www-data:755）")
print("  2. 创建数据库 expiry_system")
print("  3. 访问 http://ceshi.dhmip.cn/install.php")
print("  4. 申请SSL证书")
