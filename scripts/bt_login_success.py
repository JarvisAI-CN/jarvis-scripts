import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# 1. Focus the browser by clicking the center
pyautogui.click(666, 432)
time.sleep(0.5)

# 2. ESC to clear any address bar popups
pyautogui.press('esc')
time.sleep(0.5)
pyautogui.press('esc')
time.sleep(0.5)

# 3. Tab to Account Field
# In the test, the first Tab landed in the Account field
pyautogui.press('tab')
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'a')
pyautogui.press('backspace')
pyautogui.typewrite('fs123', interval=0.1)
time.sleep(0.5)

# 4. Tab to Password Field
pyautogui.press('tab')
time.sleep(0.2)
pyautogui.hotkey('ctrl', 'a')
pyautogui.press('backspace')
pyautogui.typewrite('fs123456', interval=0.1)
time.sleep(0.5)

# 5. Tab to Login Button and Press Enter
pyautogui.press('tab') # Should reach the dropdown
time.sleep(0.2)
pyautogui.press('tab') # Should reach Login button
time.sleep(0.2)
pyautogui.press('enter')

# 6. Wait for dashboard
print("Waiting for dashboard...")
time.sleep(15)

# 7. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_bt_dashboard.png')
