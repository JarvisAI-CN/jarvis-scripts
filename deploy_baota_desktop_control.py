#!/usr/bin/env python3
"""
宝塔面板自动部署 - 使用Desktop Control技能
通过VNC桌面浏览器操作宝塔面板
"""

import sys
import os
import time

# 添加技能路径
skill_path = '/home/ubuntu/.openclaw/workspace/skills/desktop-control'
sys.path.insert(0, skill_path)

# 设置DISPLAY环境变量
os.environ['DISPLAY'] = ':1'

try:
    # 导入技能模块
    import subprocess
    print("=== 宝塔面板自动部署 (Desktop Control) ===")

    # 检查VNC是否运行
    result = subprocess.run(['xdotool', 'search', '--name', 'Firefox'],
                          capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ 未找到Firefox窗口，请先启动VNC和Firefox")
        sys.exit(1)

    print("✅ 找到Firefox窗口")

    # 使用ai_agent来控制桌面
    ai_agent_path = os.path.join(skill_path, 'ai_agent.py')

    # 执行桌面控制命令
    print("\n📍 步骤1: 激活Firefox并访问宝塔面板")

    # 使用xdotool作为基础（因为Desktop Control需要图形环境）
    commands = [
        # 激活Firefox
        "xdotool search --name 'Firefox' windowactivate",
        "sleep 2",

        # 聚焦地址栏
        "xdotool key Ctrl+l",
        "sleep 1",

        # 输入宝塔面板地址
        "xdotool type 'http://82.157.20.7:8888/fs123456'",
        "sleep 1",
        "xdotool key Return",
        "sleep 6",

        # 截图
        "import -window root /tmp/baota_step1_login.png || echo '截图失败'",
    ]

    for cmd in commands:
        if cmd.startswith('xdotool') or cmd.startswith('sleep') or cmd.startswith('import'):
            subprocess.run(cmd, shell=True, capture_output=True)

    print("✅ 步骤1完成 - 已访问宝塔面板并截图")

    # 接下来使用图像识别来操作
    print("\n📍 步骤2: 使用Desktop Control进行精确操作")

    # 尝试使用Python的pyautogui进行更精确的控制
    try:
        import pyautogui
        print("✅ pyautogui可用")

        # 获取屏幕尺寸
        width, height = pyautogui.size()
        print(f"📺 屏幕尺寸: {width}x{height}")

        # 移动到用户名框（大概位置）
        print("\n📍 填写登录信息")
        pyautogui.click(600, 400)
        time.sleep(0.5)
        pyautogui.write('fs123456', interval=0.05)
        time.sleep(0.5)

        # Tab到密码框
        pyautogui.press('tab')
        time.sleep(0.5)
        pyautogui.write('Fs159753.', interval=0.05)
        time.sleep(0.5)

        # 提交
        pyautogui.press('enter')
        print("✅ 登录表单已提交")
        time.sleep(8)

        # 截图
        pyautogui.screenshot('/tmp/baota_step2_logged_in.png')
        print("📸 登录后截图已保存")

    except ImportError:
        print("⚠️ pyautogui不可用，使用基础方法")
        print("请手动在VNC中操作，或安装pyautogui")

    print("\n=== 部分自动化完成 ===")
    print("📸 截图已保存到 /tmp/")
    print("⏳ 接下来需要手动在宝塔面板中:")
    print("1. 点击【网站】")
    print("2. 点击【添加站点】")
    print("3. 域名填: ceshi.dhmip.cn")
    print("4. PHP版本: 8.3")
    print("5. 创建数据库: expiry_system")
    print("6. 在文件管理器使用Git克隆:")
    print("   https://github.com/JarvisAI-CN/expiry-management-system.git")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
