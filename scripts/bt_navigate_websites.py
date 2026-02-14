#!/usr/bin/env python3
"""
导航到网站管理页面
"""
import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("步骤 1: 点击左侧菜单的'网站'")

# 网站菜单位置在左侧，大约在 (100, 180) 位置
# 根据之前的截图，"网站"在左侧菜单中，大约在垂直方向 180 像素位置
pyautogui.click(100, 180)
time.sleep(3)

print("截图保存到 /tmp/bt_websites_list.png")
pyautogui.screenshot('/tmp/bt_websites_list.png')

print("步骤 2: 查找域名 yinyue.dhmip.cn")
# 使用 Ctrl+F 搜索
time.sleep(1)
pyautogui.hotkey('ctrl', 'f')
time.sleep(1)
pyautogui.typewrite('yinyue.dhmip.cn', interval=0.05)
time.sleep(1)
# 按回车跳到第一个结果
pyautogui.press('enter')
time.sleep(1)
# 关闭搜索框
pyautogui.press('escape')

print("截图保存到 /tmp/bt_websites_after_search.png")
time.sleep(2)
pyautogui.screenshot('/tmp/bt_websites_after_search.png')

print("完成。请检查截图。")
