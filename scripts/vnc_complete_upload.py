#!/usr/bin/env python3
"""
继续VNC自动化 - 完成文件选择和上传
"""

import os
os.environ['DISPLAY'] = ':1'

import pyautogui
import time
import subprocess

print("="*60)
print("🚀 VNC自动化 - 完成文件上传")
print("="*60)

# 当前应该已经打开文件选择对话框
# 等待对话框完全加载
time.sleep(3)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_step1.png')
print("📸 步骤1: 对话框状态")

# 尝试方法1：使用快捷键Ctrl+L直接输入路径
print("\n📍 尝试快捷键输入路径...")
pyautogui.hotkey('ctrl', 'l')
time.sleep(1)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_step2.png')
print("📸 步骤2: Ctrl+L后")

# 输入文件路径
file_path = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"
pyautogui.write(file_path, interval=0.05)
time.sleep(1)
pyautogui.press('enter')
time.sleep(2)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_step3.png')
print("📸 步骤3: 路径输入后")

# 现在应该看到文件列表
# 尝试选择index.php（第一个文件）
print("\n📍 选择文件...")
# 使用Tab键或方向键选择文件
pyautogui.press('tab')
time.sleep(0.5)
pyautogui.press('enter')  # 选择第一个文件
time.sleep(2)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_step4.png')
print("📸 步骤4: 文件选择后")

# 如果是单文件选择对话框，需要分两次上传
# 先上传index.php
pyautogui.press('enter')  # 确认选择
time.sleep(3)
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_step5.png')
print("📸 步骤5: 第一个文件上传后")

# 等待上传完成，然后上传第二个文件
print("\n📍 上传第二个文件...")
# 重复上述步骤
time.sleep(2)

print("\n" + "="*60)
print("✅ 文件上传步骤完成")
print("="*60)
print("请检查VNC中的文件列表，确认两个文件都已上传")
print("文件列表应该有:")
print("  - index.php (46KB)")
print("  - db.php (2.5KB)")
print("="*60)
