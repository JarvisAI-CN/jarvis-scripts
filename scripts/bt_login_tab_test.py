import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Click center of window
print("Clicking window center...")
pyautogui.click(666, 432)
time.sleep(0.5)

# 2. Try to navigate with Tab
# Esc to clear any popups
pyautogui.press('esc')
time.sleep(0.5)
pyautogui.press('esc')
time.sleep(0.5)

# 3. Use Tab to find the field
# We'll try to Tab 10 times and type "findme" in each
for i in range(15):
    pyautogui.press('tab')
    pyautogui.typewrite(f'pos{i}', interval=0.05)
    time.sleep(0.2)

# 4. Take screenshot to see where text landed
pyautogui.screenshot('/tmp/vnc_screen_tab_test.png')
