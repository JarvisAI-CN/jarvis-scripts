import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

USERNAME = 'fs123'
PASSWORD = 'fs123456'
CAPTCHA = 'K8rR'

def main():
    print("Step 2: Login with CAPTCHA")
    # Click center of window to focus
    pyautogui.click(666, 432)
    time.sleep(0.5)

    # 1. TAB to account
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(USERNAME, interval=0.1)
    time.sleep(0.5)

    # 2. TAB to password
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(PASSWORD, interval=0.1)
    time.sleep(0.5)

    # 3. TAB to dropdown
    pyautogui.press('tab')
    time.sleep(0.2)

    # 4. TAB to captcha
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.typewrite(CAPTCHA, interval=0.1)
    time.sleep(0.5)

    # 5. TAB to login button
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.press('enter')
    
    print("Waiting for dashboard...")
    time.sleep(15)
    pyautogui.screenshot('/tmp/bt_dash_final.png')

if __name__ == "__main__":
    main()
