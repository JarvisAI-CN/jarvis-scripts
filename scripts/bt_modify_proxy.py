#!/usr/bin/env python3
"""
修改反向代理配置
"""
import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("步骤 1: 修改目标URL")

# 点击目标URL输入框（大约在 850, 300 位置，在URL末尾）
pyautogui.click(850, 300)
time.sleep(0.5)

# 三击选中URL末尾的5000
pyautogui.tripleClick(850, 300)
time.sleep(0.5)

# 按两次退格删除 5000
pyautogui.press('backspace')
pyautogui.press('backspace')
pyautogui.press('backspace')
pyautogui.press('backspace')
time.sleep(0.5)

# 输入新端口号 5001
pyautogui.typewrite('5001', interval=0.1)
time.sleep(1)

print("步骤 2: 取消'开启缓存'勾选")
# 缓存复选框大约在 (560, 550) 位置
pyautogui.click(560, 550)
time.sleep(0.5)

print("截图保存到 /tmp/bt_before_save.png")
pyautogui.screenshot('/tmp/bt_before_save.png')

print("步骤 3: 点击保存按钮")
# 保存按钮在右下角，大约在 (900, 650) 位置
pyautogui.click(900, 650)
time.sleep(2)

print("等待保存完成...")
pyautogui.screenshot('/tmp/bt_after_save.png')

print("完成。请检查截图确认修改是否成功。")
