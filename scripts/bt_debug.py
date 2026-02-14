import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def bt_login():
    bt_url = "http://82.157.20.7:8888/fs123456"
    username = "fs123"
    password = "fs123456"
    
    print(f"Logging into BT panel at {bt_url}...")
    
    # Launch Chrome
    pyautogui.hotkey('alt', 'f2')
    time.sleep(1)
    pyautogui.write('google-chrome --no-sandbox ' + bt_url)
    pyautogui.press('enter')
    
    # Wait for page to load
    time.sleep(10)
    
    # Take a screenshot to see where we are
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_login_step1.png')
    
    # Click username field (estimating coordinates, or using TAB)
    # Usually the first field is username.
    pyautogui.press('tab', presses=2) # Adjust based on screenshot
    pyautogui.write(username)
    pyautogui.press('tab')
    pyautogui.write(password)
    pyautogui.press('enter')
    
    # Wait for login
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_dashboard.png')
    
    # Go to File Manager
    # Usually there is a "文件" or "Files" link.
    # I will try to navigate directly if possible, or just look at the dashboard.

if __name__ == "__main__":
    bt_login()
