import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("Navigating back to panel...")
# Focus browser
pyautogui.click(666, 432)
time.sleep(0.5)

# Go back
pyautogui.hotkey('alt', 'left')
time.sleep(5)

# Screenshot
pyautogui.screenshot('/tmp/bt_after_back.png')
