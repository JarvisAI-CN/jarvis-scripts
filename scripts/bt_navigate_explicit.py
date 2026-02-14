import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

print("Dismissing dialog and navigating...")
# Click 'x' on restore dialog
pyautogui.click(640, 120) 
time.sleep(1)

# Navigate to panel
pyautogui.hotkey('ctrl', 'l')
time.sleep(0.5)
pyautogui.typewrite('http://82.157.20.7:8888/fs123456', interval=0.05)
pyautogui.press('enter')
time.sleep(5)

# Screenshot
pyautogui.screenshot('/tmp/bt_navigated.png')
