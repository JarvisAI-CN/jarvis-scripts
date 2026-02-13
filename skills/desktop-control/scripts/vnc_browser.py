import pyautogui
import os
import time

os.environ['DISPLAY'] = ':1'

def setup_browser():
    # 尝试启动 Firefox (GNOME自带)
    pyautogui.hotkey('alt', 'f2')
    time.sleep(1)
    pyautogui.write('firefox', interval=0.1)
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/logs/firefox_check.png')

setup_browser()
