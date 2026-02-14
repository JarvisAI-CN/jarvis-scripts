import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Close dialogs
print("Closing dialogs...")
pyautogui.press('esc')
time.sleep(1)
pyautogui.click(639, 122) # Click 'x' of restore dialog
time.sleep(1)

# 2. Click account field to ensure focus
# Top-left of window is (35, 25)
# Inside the login box:
# Field "账号" center is roughly (345, 425)
print("Clicking account field...")
pyautogui.click(345, 425)
time.sleep(1)

# 3. Select all and type username
pyautogui.hotkey('ctrl', 'a')
pyautogui.press('backspace')
pyautogui.typewrite('fs123', interval=0.1)
time.sleep(1)

# 4. Tab to password
pyautogui.press('tab')
time.sleep(0.5)
pyautogui.typewrite('fs123456', interval=0.1)
time.sleep(1)

# 5. Press Enter
print("Pressing Enter...")
pyautogui.press('enter')
time.sleep(10)

# 6. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_login_attempt.png')
print("Screenshot saved to /tmp/vnc_screen_login_attempt.png")
