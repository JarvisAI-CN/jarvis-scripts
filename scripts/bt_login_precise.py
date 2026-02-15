import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login(captcha):
    # 1. Close the "Restore" bubble in Chrome
    pyautogui.click(647, 114)
    time.sleep(1)
    
    # 2. Click Account field
    pyautogui.click(350, 375)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123', interval=0.1)
    
    # 3. Click Password field
    pyautogui.click(350, 425)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123456', interval=0.1)
    
    # 4. Click Captcha field
    pyautogui.click(280, 525)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(captcha, interval=0.1)
    
    # 5. Click Login button
    pyautogui.click(330, 575)
    
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_final_attempt.png')

if __name__ == "__main__":
    import sys
    login(sys.argv[1])
