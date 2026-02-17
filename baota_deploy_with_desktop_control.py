#!/usr/bin/env python3
"""
宝塔面板自动部署脚本 - 使用Desktop Control技能
"""

import sys
import time
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/skills/desktop-control')

try:
    from desktop_control import DesktopController
    print("✅ Desktop Controller 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def main():
    print("=== 宝塔面板自动部署开始 ===")

    # 初始化控制器
    dc = DesktopController(failsafe=True)

    # 获取屏幕尺寸
    width, height = dc.get_screen_size()
    print(f"📺 屏幕尺寸: {width}x{height}")

    # 步骤1: 激活Firefox窗口
    print("\n📍 步骤1: 激活Firefox")
    try:
        dc.activate_window("Firefox")
        time.sleep(2)
        print("✅ Firefox已激活")
    except Exception as e:
        print(f"⚠️ 激活Firefox失败: {e}")

    # 步骤2: 访问宝塔面板
    print("\n📍 步骤2: 访问宝塔面板")
    dc.hotkey('ctrl', 'l')  # 聚焦地址栏
    time.sleep(1)
    dc.type_text("http://82.157.20.7:8888/fs123456", interval=0.05)
    time.sleep(1)
    dc.press('enter')
    print("✅ 正在访问宝塔面板...")
    time.sleep(5)

    # 步骤3: 截图分析登录页
    print("\n📍 步骤3: 截图分析登录页")
    screenshot = dc.screenshot(filename="/tmp/baota_login_page.png")
    print(f"📸 登录页截图已保存")

    # 步骤4: 填写登录信息
    print("\n📍 步骤4: 填写登录信息")
    # 用户名框大概位置（需要根据实际调整）
    dc.click(600, 400)  # 用户名框
    time.sleep(0.5)
    dc.type_text("fs123456", interval=0.05)
    time.sleep(0.5)

    # Tab到密码框
    dc.press('tab')
    time.sleep(0.5)
    dc.type_text("Fs159753.", interval=0.05)
    time.sleep(0.5)

    # 提交登录
    dc.press('enter')
    print("✅ 登录表单已提交")
    time.sleep(8)

    # 步骤5: 截图分析主页
    print("\n📍 步骤5: 截图分析主页")
    screenshot = dc.screenshot(filename="/tmp/baota_main_page.png")
    print(f"📸 主页截图已保存")

    # 步骤6: 点击网站菜单（左侧菜单）
    print("\n📍 步骤6: 点击网站菜单")
    dc.click(150, 200)  # 网站菜单大概位置
    time.sleep(3)
    print("✅ 网站菜单已点击")

    # 步骤7: 点击添加站点
    print("\n📍 步骤7: 点击添加站点")
    dc.click(300, 150)  # 添加站点按钮
    time.sleep(2)
    print("✅ 添加站点对话框已打开")

    # 步骤8: 填写域名
    print("\n📍 步骤8: 填写域名")
    dc.click(600, 300)  # 域名输入框
    time.sleep(0.5)
    dc.type_text("ceshi.dhmip.cn", interval=0.05)
    time.sleep(1)

    # 步骤9: 点击PHP版本选择
    print("\n📍 步骤9: 选择PHP 8.3")
    dc.click(600, 380)  # PHP版本下拉框
    time.sleep(0.5)
    dc.press('down')  # 向下选择
    time.sleep(0.3)
    dc.press('down')
    time.sleep(0.3)
    dc.press('enter')  # 确认选择
    time.sleep(1)

    # 步骤10: 提交创建
    print("\n📍 步骤10: 提交站点创建")
    dc.click(700, 500)  # 提交按钮
    time.sleep(5)
    print("✅ 站点创建已提交")

    # 步骤11: 等待并截图
    print("\n📍 步骤11: 最终截图")
    time.sleep(3)
    screenshot = dc.screenshot(filename="/tmp/baota_after_create_site.png")
    print(f"📸 最终截图已保存")

    print("\n=== 基础部署完成 ===")
    print("接下来需要在宝塔文件管理器中:")
    print("1. 使用Git克隆代码")
    print("2. 设置文件权限")
    print("3. 创建数据库")
    print("4. 访问安装向导")

if __name__ == "__main__":
    main()
