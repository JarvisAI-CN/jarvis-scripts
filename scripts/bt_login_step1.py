import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# Screen size
width, height = pyautogui.size()
print(f"Screen size: {width}x{height}")

# 1. Click to close the "Restore" dialog if it exists
# Based on the screenshot, the 'x' for the dialog is around (635, 120) relative to the window?
# Or the blue button "恢复" is around (620, 190)?
# Let's try to click the 'x' at roughly (640, 120) if the window is positioned there.
# Actually, the window top-left seems to be around (40, 40).
# Dialog is around (480, 90) to (650, 230).
# Close button 'x' is at roughly (640, 125).
pyautogui.click(640, 125)
time.sleep(1)

# 2. Wait for page load
print("Waiting for page load...")
time.sleep(10)

# 3. Take screenshot
pyautogui.screenshot('/tmp/vnc_screen_after_load.png')
print("Screenshot saved to /tmp/vnc_screen_after_load.png")
