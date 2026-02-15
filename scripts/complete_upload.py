#!/usr/bin/env python3
"""
完成VNC自动化部署 - 上传文件阶段
"""

import os
os.environ['DISPLAY'] = ':1'

import pyautogui
import time

print("="*60)
print("🚀 完成文件上传...")
print("="*60)

# 当前应该已经打开文件上传对话框
# 等待一下让对话框完全加载
time.sleep(2)

# 截图当前状态
pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_upload_before.png')
print("📸 截图: vnc_upload_before.png")

# 接下来需要：
# 1. 在文件选择对话框中导航到文件位置
# 2. 选择 index.php
# 3. 点击打开/上传
# 4. 重复步骤选择 db.py

print("\n当前状态：文件上传对话框应该已打开")
print("文件位置: /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/")
print("\n⚠️  需要手动选择文件并上传")
print("或者我可以继续尝试自动化...")
print("="*60)
