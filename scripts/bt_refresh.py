import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Focus Chrome and Reload
pyautogui.click(666, 432)
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'r')
print("Page reloaded.")
time.sleep(5)

# 2. ESC to close any popups
pyautogui.press('esc')
time.sleep(1)

# 3. Take screenshot
pyautogui.screenshot('/tmp/bt_captcha_new.png')
print("Screenshot saved to /tmp/bt_captcha_new.png")
