#!/usr/bin/env python3
"""
测试尝试登录，看看验证码是否仍然存在
"""
import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("测试: 刷新登录页面，检查验证码状态")

# 1. 激活窗口并刷新
pyautogui.click(666, 432)
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'shift', 'r')  # 强制刷新，忽略缓存
print("页面已刷新 (Ctrl+Shift+R)")
time.sleep(8)  # 等待页面完全加载

# 2. 截图
pyautogui.screenshot('/tmp/bt_test_captcha_status.png')
print("截图已保存到 /tmp/bt_test_captcha_status.png")

# 3. 检查验证码区域
# 验证码通常在 (720, 480) 附近
# 让我们检查那个区域的像素颜色
try:
    from PIL import Image
    img = Image.open('/tmp/bt_test_captcha_status.png')
    
    # 检查验证码区域的几个点
    test_points = [
        (720, 480),
        (740, 480),
        (720, 470),
        (740, 470),
    ]
    
    print("\n验证码区域像素检查:")
    for x, y in test_points:
        r, g, b = img.getpixel((x, y))
        print(f"  ({x}, {y}): RGB({r}, {g}, {b})")
        
except Exception as e:
    print(f"像素检查失败: {e}")

print("\n请查看截图确认验证码是否存在")
