import pyautogui
import os

# Set display
os.environ['DISPLAY'] = ':1'

# Take screenshot
screenshot = pyautogui.screenshot()
screenshot.save('screenshot_vnc.png')
print("Screenshot saved to screenshot_vnc.png")
