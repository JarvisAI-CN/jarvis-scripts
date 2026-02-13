import pyautogui
import os
import time

os.environ['DISPLAY'] = ':1'

def launch_chrome():
    # 尝试使用快捷键启动 Chrome
    pyautogui.hotkey('alt', 'f2')
    time.sleep(1)
    pyautogui.write('google-chrome', interval=0.1)
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/logs/chrome_launch_check.png')
    print("Chrome launch command sent.")

if __name__ == "__main__":
    launch_chrome()
