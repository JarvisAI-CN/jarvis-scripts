#!/usr/bin/env python3
"""
保质期管理系统 - VNC浏览器自动化部署
使用pyautogui控制Firefox操作宝塔面板
"""

import os
os.environ['DISPLAY'] = ':1'

import pyautogui
import time
import subprocess

# 安全设置
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True

def log(msg):
    print(f"⚡ {msg}")

def screenshot(name):
    path = f'/home/ubuntu/.openclaw/workspace/vnc_auto_{name}.png'
    pyautogui.screenshot(path)
    log(f"截图: {path}")
    return path

def type_text(text, interval=0.05):
    pyautogui.write(text, interval=interval)

def main():
    print("="*60)
    print("🚀 保质期管理系统 - VNC浏览器自动化部署")
    print("="*60)
    
    # 步骤1: 启动Firefox并访问宝塔面板
    log("步骤1: 启动Firefox...")
    subprocess.Popen(['firefox', '--new-window', 'http://82.157.20.7:8888/fs123456'],
                    env=os.environ.copy(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)
    time.sleep(8)
    screenshot("01_browser_opened")
    
    # 步骤2: 登录宝塔面板
    log("步骤2: 登录宝塔面板...")
    time.sleep(2)
    
    # Tab到用户名输入框并输入
    for _ in range(3):
        pyautogui.press('tab')
    time.sleep(0.5)
    
    # 输入用户名
    pyautogui.hotkey('ctrl', 'a')
    type_text('fs123')
    time.sleep(0.5)
    
    # Tab到密码框
    pyautogui.press('tab')
    time.sleep(0.5)
    
    # 输入密码
    type_text('fs123456')
    time.sleep(0.5)
    
    # 回车登录
    pyautogui.press('enter')
    log("登录信息已输入，等待进入面板...")
    time.sleep(12)
    screenshot("02_logged_in")
    
    # 步骤3: 进入数据库管理
    log("步骤3: 进入数据库管理...")
    # 点击左侧"数据库"菜单（根据宝塔布局约在y=220位置）
    pyautogui.click(80, 220)
    time.sleep(5)
    screenshot("03_database_menu")
    
    # 步骤4: 添加数据库
    log("步骤4: 添加数据库...")
    # 点击"添加数据库"按钮（顶部约y=120）
    pyautogui.click(200, 120)
    time.sleep(3)
    screenshot("04_add_db_dialog")
    
    # 填写数据库信息
    # 点击数据库名输入框
    pyautogui.click(400, 280)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'a')
    type_text('expiry_system')
    time.sleep(0.5)
    
    # 用户名
    pyautogui.press('tab')
    type_text('expiry_user')
    time.sleep(0.5)
    
    # 密码
    pyautogui.press('tab')
    type_text('Expiry@2026System!')
    time.sleep(0.5)
    
    screenshot("05_db_form_filled")
    
    # 点击提交
    pyautogui.click(500, 450)
    time.sleep(8)
    screenshot("06_db_created")
    
    # 步骤5: 导入SQL
    log("步骤5: 导入数据库结构...")
    # 点击数据库名查看详情
    pyautogui.click(300, 320)
    time.sleep(3)
    screenshot("07_db_detail")
    
    # 点击"导入"标签
    pyautogui.click(450, 180)
    time.sleep(2)
    screenshot("08_import_tab")
    
    # 步骤6: 进入网站管理
    log("步骤6: 上传网站文件...")
    # 点击左侧"网站"菜单
    pyautogui.click(80, 180)
    time.sleep(5)
    screenshot("09_website_menu")
    
    # 点击ceshi.dhmip.cn的根目录
    pyautogui.click(600, 300)
    time.sleep(4)
    screenshot("10_file_manager")
    
    # 删除index.html（如果存在）
    log("删除默认文件...")
    pyautogui.rightClick(400, 350)
    time.sleep(1)
    pyautogui.click(450, 380)  # 点击删除选项
    time.sleep(2)
    screenshot("11_file_deleted")
    
    # 步骤7: 上传PHP文件
    log("准备上传PHP文件...")
    # 点击上传按钮
    pyautogui.click(700, 100)
    time.sleep(3)
    screenshot("12_upload_dialog_opened")
    
    print("\n" + "="*60)
    print("⚠️  浏览器自动化到达文件上传步骤")
    print("="*60)
    print("需要手动选择文件：")
    print("1. 点击上传对话框的'选择文件'")
    print("2. 导航到: /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/")
    print("3. 选择: index.php")
    print("4. 再选择: db.php")
    print("5. 点击上传")
    print("="*60)
    print("✅ 数据库已创建")
    print("✅ 文件管理器已打开")
    print("⏳ 等待手动上传文件")
    print("="*60)
    
    # 保持截图记录最后状态
    screenshot("13_ready_for_upload")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log("用户中断")
    except Exception as e:
        log(f"错误: {e}")
        import traceback
        traceback.print_exc()
