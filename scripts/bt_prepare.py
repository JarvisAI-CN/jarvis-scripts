import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login():
    username = "fs123"
    password = "fs123456"
    
    # 1. Click to focus browser
    pyautogui.click(500, 500)
    time.sleep(1)
    
    # 2. Refresh to get a fresh captcha
    pyautogui.press('f5')
    time.sleep(5)
    
    # 3. Take screenshot to see captcha
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_login_ready.png')
    
if __name__ == "__main__":
    login()
