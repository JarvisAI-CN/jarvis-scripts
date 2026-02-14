#!/usr/bin/env python3
"""
点击 yinyue.dhmip.cn 的设置按钮
"""
import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("点击 yinyue.dhmip.cn 的设置按钮")

# 根据截图，yinyue.dhmip.cn 在表格中间位置
# 设置按钮在右侧，大约在 (1050, 400) 位置
pyautogui.click(1050, 400)
time.sleep(2)

print("等待设置菜单打开...")
pyautogui.screenshot('/tmp/bt_settings_menu.png')

print("点击'反向代理'选项")
# 反向代理菜单项大约在 (950, 450) 位置
pyautogui.click(950, 450)
time.sleep(3)

print("等待反向代理设置页面打开...")
pyautogui.screenshot('/tmp/bt_reverse_proxy_settings.png')

print("完成。请检查截图。")
