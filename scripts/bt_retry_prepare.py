import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login():
    # 1. Click chrome to focus
    pyautogui.click(100, 100)
    time.sleep(0.5)
    
    # 2. Refresh
    pyautogui.press('f5')
    time.sleep(5)
    
    # 3. Take screenshot
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_retry.png')

if __name__ == "__main__":
    login()
