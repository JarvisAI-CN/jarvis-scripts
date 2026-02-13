import pyautogui
import os
import time

# Set display
os.environ['DISPLAY'] = ':1'

# Start Chrome
os.system('google-chrome --no-sandbox https://login.live.com/ &')
time.sleep(10)

# Take screenshot
screenshot = pyautogui.screenshot()
screenshot.save('vnc_chrome_outlook.png')
print("Screenshot saved to vnc_chrome_outlook.png")
