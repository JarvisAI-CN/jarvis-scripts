import os
import pyautogui
import time

os.environ['DISPLAY'] = ':1'

def login():
    # Click username
    pyautogui.click(450, 380) # Click inside username field
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('fs123')
    time.sleep(0.5)
    
    # Press Tab to password
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('fs123456')
    time.sleep(0.5)
    
    # Press Tab to captcha
    pyautogui.press('tab')
    # Manually identified captcha from screenshot
    pyautogui.write('3pLG')
    time.sleep(0.5)
    
    # Login
    pyautogui.press('enter')
    time.sleep(8)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/vnc_login_result.png')

if __name__ == "__main__":
    login()
