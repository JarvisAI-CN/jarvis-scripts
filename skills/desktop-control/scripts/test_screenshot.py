import pyautogui
import os
from datetime import datetime

try:
    # 设置显示器（针对 VNC :1）
    os.environ['DISPLAY'] = ':1'
    
    # 截图
    screenshot_path = f"/home/ubuntu/.openclaw/workspace/logs/vnc_check_{datetime.now().strftime('%H%M%S')}.png"
    pyautogui.screenshot(screenshot_path)
    print(f"✅ 截图成功: {screenshot_path}")
    
    # 获取屏幕尺寸
    width, height = pyautogui.size()
    print(f"🖥️ 屏幕尺寸: {width}x{height}")
    
except Exception as e:
    print(f"❌ 错误: {str(e)}")
