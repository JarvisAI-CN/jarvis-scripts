import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login():
    username = "fs123"
    password = "fs123456"
    
    # Refresh
    pyautogui.click(500, 500)
    pyautogui.press('f5')
    time.sleep(5)
    
    # Capture captcha
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_captcha_tab.png')
    
if __name__ == "__main__":
    login()
