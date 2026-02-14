import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Close any dialogs
pyautogui.press('esc')
time.sleep(0.5)

# 2. Click and clear account field
print("Clearing account field...")
pyautogui.click(345, 425)
time.sleep(0.5)
for _ in range(20):
    pyautogui.press('backspace')
    pyautogui.press('delete')

# 3. Type username
print("Typing username...")
pyautogui.typewrite('fs123', interval=0.2)
time.sleep(1)

# 4. Tab to password
pyautogui.press('tab')
time.sleep(0.5)

# 5. Type password
print("Typing password...")
pyautogui.typewrite('fs123456', interval=0.2)
time.sleep(1)

# 6. Press Enter
print("Pressing Enter...")
pyautogui.press('enter')
time.sleep(10)

# 7. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_bt_login_step6.png')
