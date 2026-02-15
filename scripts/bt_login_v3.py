import os
import pyautogui
import time

os.environ['DISPLAY'] = ':1'

def login():
    # Click username field
    pyautogui.click(350, 380)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('fs123')
    time.sleep(0.5)
    
    # Tab to password
    pyautogui.press('tab')
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('fs123456')
    time.sleep(0.5)
    
    # Tab to captcha
    pyautogui.press('tab')
    pyautogui.write('7NGW')
    time.sleep(0.5)
    
    # Click Login Button (Green)
    pyautogui.click(400, 580)
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_home_result.png')

if __name__ == "__main__":
    login()
