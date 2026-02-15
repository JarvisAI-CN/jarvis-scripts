import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login(captcha):
    username = "fs123"
    password = "fs123456"
    
    # 1. Click Account field
    pyautogui.click(350, 375)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(username)
    
    # 2. Click Password field
    pyautogui.click(350, 425)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(password)
    
    # 3. Click Captcha field
    pyautogui.click(280, 525)
    pyautogui.write(captcha)
    
    # 4. Click Login
    pyautogui.click(330, 575)
    
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_dashboard_after_login.png')

if __name__ == "__main__":
    import sys
    login(sys.argv[1])
