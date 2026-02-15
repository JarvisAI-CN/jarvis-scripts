import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def refresh_and_shot():
    pyautogui.press('f5')
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_new_captcha.png')

if __name__ == "__main__":
    refresh_and_shot()
