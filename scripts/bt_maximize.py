import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def maximize_and_clean():
    # 1. Focus Chrome
    pyautogui.click(500, 500)
    time.sleep(0.5)
    
    # 2. Alt+Space then 'x' to maximize (GNOME)
    pyautogui.hotkey('alt', 'space')
    time.sleep(0.5)
    pyautogui.press('x')
    time.sleep(1)
    
    # 3. Screenshot
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_maximized.png')

if __name__ == "__main__":
    maximize_and_clean()
