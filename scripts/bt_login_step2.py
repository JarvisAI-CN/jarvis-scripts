import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Click and Type Username
print("Typing username...")
pyautogui.click(345, 425)
time.sleep(0.5)
pyautogui.typewrite('fs123', interval=0.1)

# 2. Click and Type Password
print("Typing password...")
pyautogui.click(345, 475)
time.sleep(0.5)
pyautogui.typewrite('fs123456', interval=0.1)

# 3. Click Login
print("Clicking login...")
pyautogui.click(345, 580)
time.sleep(5)

# 4. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_after_login.png')
print("Screenshot saved to /tmp/vnc_screen_after_login.png")
