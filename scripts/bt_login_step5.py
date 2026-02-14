import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Close dialog
pyautogui.press('esc')
time.sleep(0.5)

# 2. Click Account Field (Double click to ensure focus)
print("Clicking account field...")
pyautogui.click(345, 425, clicks=2, interval=0.2)
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'a')
pyautogui.press('backspace')
time.sleep(0.5)
pyautogui.typewrite('fs123', interval=0.1)
time.sleep(1)

# 3. Click Password Field
print("Clicking password field...")
pyautogui.click(345, 475, clicks=2, interval=0.2)
time.sleep(0.5)
pyautogui.hotkey('ctrl', 'a')
pyautogui.press('backspace')
time.sleep(0.5)
pyautogui.typewrite('fs123456', interval=0.1)
time.sleep(1)

# 4. Click Green Login Button
print("Clicking login button...")
pyautogui.click(345, 580)
time.sleep(10)

# 5. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_bt_login_step5.png')
