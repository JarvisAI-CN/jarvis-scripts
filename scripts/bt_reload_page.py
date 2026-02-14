import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("Reloading page...")
# Click somewhere safe
pyautogui.click(666, 432)
time.sleep(0.5)

# Press ESC to close dialogs
pyautogui.press('esc')
time.sleep(0.5)

# Reload
pyautogui.hotkey('ctrl', 'r')
time.sleep(10)

# Screenshot
pyautogui.screenshot('/tmp/bt_reloaded.png')
print("Screenshot saved to /tmp/bt_reloaded.png")
