#!/usr/bin/env python3
"""
保质期管理系统 - 宝塔面板自动部署脚本
使用PyAutoGUI控制浏览器完成部署
"""

import os
# 必须在导入pyautogui之前设置DISPLAY
os.environ['DISPLAY'] = ':1'

import pyautogui
import time
import subprocess

# 安全设置
pyautogui.PAUSE = 0.5  # 每次操作暂停0.5秒
pyautogui.FAILSAFE = True  # 鼠标移到左上角可以终止程序

def take_screenshot(name):
    """截图保存"""
    path = f'/home/ubuntu/.openclaw/workspace/{name}.png'
    pyautogui.screenshot(path)
    print(f'📸 截图保存: {path}')

def press_keys(keys, times=1):
    """按键"""
    for _ in range(times):
        pyautogui.press(keys)
        time.sleep(0.2)

def type_text(text, interval=0.05):
    """输入文本"""
    pyautogui.write(text, interval=interval)

def main():
    print("=" * 60)
    print("🚀 保质期管理系统 - 宝塔面板自动部署")
    print("=" * 60)

    # 第一步：启动Firefox并访问宝塔面板
    print("\n📍 步骤1: 启动浏览器...")
    try:
        # 使用xdotool打开Firefox
        subprocess.Popen(['xdotool', 'search', '--name', 'Firefox', 'windowactivate', 'key', 'Ctrl+l'],
                        stderr=subprocess.DEVNULL)
        time.sleep(1)

        # 启动Firefox（如果没有运行）
        subprocess.Popen(['firefox', 'http://82.157.20.7:8888/fs123456'],
                        env=os.environ.copy(),
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        print("✅ Firefox已启动，正在加载宝塔面板...")
        time.sleep(8)  # 等待页面加载

    except Exception as e:
        print(f"❌ 启动浏览器失败: {e}")
        print("💡 请手动打开Firefox访问: http://82.157.20.7:8888/fs123456")
        return

    take_screenshot('01_browser_started')

    # 第二步：登录宝塔面板
    print("\n📍 步骤2: 登录宝塔面板...")
    print("   用户名: fs123")
    print("   密码: fs123456")

    # 等待登录表单加载
    time.sleep(2)

    # 尝试Tab到用户名输入框（假设是第一个输入框）
    press_keys('tab', 2)  # 跳到用户名框
    time.sleep(0.5)

    # 清空并输入用户名
    press_keys('end')
    pyautogui.hotkey('shift', 'home')  # 选中所有文本
    press_keys('delete')
    type_text('fs123')

    # Tab到密码框
    press_keys('tab')
    time.sleep(0.3)

    # 输入密码
    type_text('fs123456')

    # 回车登录
    press_keys('enter')
    print("✅ 登录信息已输入，等待进入面板...")
    time.sleep(10)  # 等待登录完成

    take_screenshot('02_logged_in')

    # 第三步：进入网站管理
    print("\n📍 步骤3: 进入网站管理...")

    # 点击左侧菜单的"网站"（根据之前截图，大约在(80, 180)位置）
    pyautogui.click(80, 180)
    time.sleep(5)

    take_screenshot('03_website_page')

    # 第四步：找到ceshi.dhmip.cn并进入根目录
    print("\n📍 步骤4: 进入网站根目录...")

    # 点击ceshi.dhmip.cn的根目录按钮（根据位置估计）
    # 通常在表格的右侧
    pyautogui.click(600, 300)
    time.sleep(3)

    take_screenshot('04_file_manager')

    # 第五步：上传文件
    print("\n📍 步骤5: 上传PHP文件...")
    print("   ⚠️ 需要手动选择文件上传")
    print("   文件位置:")
    print("   - /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/index.php")
    print("   - /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/db.php")

    take_screenshot('05_ready_to_upload')

    print("\n" + "=" * 60)
    print("📋 自动化完成，需要手动操作：")
    print("=" * 60)
    print("1. 在文件管理器中，点击'上传'按钮")
    print("2. 选择以下2个文件上传:")
    print("   - index.php")
    print("   - db.php")
    print("3. 删除默认的index.html（如果存在）")
    print("4. 创建数据库:")
    print("   - 数据库名: expiry_system")
    print("   - 用户名: expiry_user")
    print("   - 密码: Expiry@2026System!")
    print("5. 导入SQL文件:")
    print("   - /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/database.sql")
    print("6. 测试访问: http://ceshi.dhmip.cn")
    print("=" * 60)

    print("\n✅ 部署流程准备完成！请在VNC中完成剩余操作。")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("💡 请检查VNC截图以了解当前状态")
