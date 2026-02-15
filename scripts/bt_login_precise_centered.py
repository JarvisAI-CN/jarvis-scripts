import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login(captcha):
    # Precise coordinates from 1920x1200 center-box image
    
    # 1. Close restore bubble
    pyautogui.click(1860, 114) # Based on Chrome bubble at top right
    time.sleep(0.5)
    
    # 2. Account field
    pyautogui.click(500, 530)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123', interval=0.1)
    
    # 3. Password field
    pyautogui.click(500, 580)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123456', interval=0.1)
    
    # 4. Captcha field
    pyautogui.click(450, 680)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(captcha, interval=0.1)
    
    # 5. Login
    pyautogui.click(500, 740)
    
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_dashboard_real.png')

if __name__ == "__main__":
    import sys
    login(sys.argv[1])
