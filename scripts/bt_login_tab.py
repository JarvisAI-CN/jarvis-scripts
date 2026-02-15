import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login(captcha):
    username = "fs123"
    password = "fs123456"
    
    # Focus Account field
    pyautogui.click(350, 375)
    time.sleep(0.5)
    pyautogui.write(username)
    
    # Tab to Password
    pyautogui.press('tab')
    pyautogui.write(password)
    
    # Tab twice to bypass the login mode dropdown (guessing)
    # Actually, let's just click the captcha field
    pyautogui.click(280, 525)
    pyautogui.write(captcha)
    
    # Enter
    pyautogui.press('enter')
    
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_dashboard_tab.png')

if __name__ == "__main__":
    import sys
    login(sys.argv[1])
