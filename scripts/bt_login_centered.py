import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login(captcha):
    # Box is centered.
    # From image bt_retry.png:
    # Username input is roughly at x=500, y=530
    
    # 1. Click Username
    pyautogui.click(500, 530)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123', interval=0.1)
    
    # 2. Tab to password
    pyautogui.press('tab')
    pyautogui.typewrite('fs123456', interval=0.1)
    
    # 3. Tab twice to bypass dropdown
    pyautogui.press('tab')
    pyautogui.press('tab')
    
    # 4. Type Captcha
    pyautogui.typewrite(captcha, interval=0.1)
    
    # 5. Enter
    pyautogui.press('enter')
    
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_final_centered.png')

if __name__ == "__main__":
    import sys
    login(sys.argv[1])
