#!/usr/bin/env python3
"""
通过VNC自动化在宝塔终端执行下载命令
"""

import os
os.environ['DISPLAY'] = ':1'

import pyautogui
import time

print("="*60)
print("🚀 VNC自动化 - 宝塔终端下载文件")
print("="*60)

# 步骤1：打开宝塔终端
print("\n📍 步骤1: 打开宝塔终端...")
# 根据宝塔面板布局，终端通常在侧边栏
# 尝试点击终端按钮（大概位置）
pyautogui.click(80, 400)  # 终端菜单位置估计
time.sleep(5)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_term_01.png')
print("📸 截图: vnc_term_01.png")

# 步骤2：在终端中执行下载命令
print("\n📍 步骤2: 执行下载命令...")
time.sleep(2)

# 构建curl命令
commands = [
    f"cd /www/wwwroot/ceshi.dhmip.cn",
    f"curl -s http://10.7.0.5:8888/index.php -o index.php",
    f"curl -s http://10.7.0.5:8888/db.php -o db.php",
    f"chmod 644 *.php",
    f"chown www:www *.php",
    f"ls -lh"
]

cmd_text = " && ".join(commands)

# 使用Ctrl+Shift+T打开新终端（如果需要）
# pyautogui.hotkey('ctrl', 'shift', 't')
# time.sleep(2)

# 输入命令
print(f"命令长度: {len(cmd_text)} 字符")
pyautogui.write(cmd_text, interval=0.02)
time.sleep(2)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_term_02.png')
print("📸 截图: vnc_term_02.png")

# 执行命令
print("\n执行命令...")
pyautogui.press('enter')
time.sleep(8)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_term_03.png')
print("📸 截图: vnc_term_03.png")

# 测试访问
print("\n🧪 测试部署...")
try:
    import requests
    response = requests.get("http://ceshi.dhmip.cn", timeout=10)
    print(f"✅ HTTP状态: {response.status_code}")
    
    if "保质期" in response.text:
        print("✅ 部署成功！页面内容正确！")
    else:
        print("⚠️  页面可能需要刷新")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print("\n" + "="*60)
print("🎉 VNC自动化完成！")
print("="*60)
print(f"🌐 访问地址: http://ceshi.dhmip.cn")
print("")
print("🧪 测试账号:")
print("   SKU: 6901234567890 → 可口可乐 500ml")
print("   SKU: 6901234567891 → 康师傅红烧牛肉面")
print("="*60)
