import os
import subprocess
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def test_website():
    url = "http://yinyue.dhmip.cn"
    print(f"Opening {url} in Chrome...")
    
    # Launch Chrome
    chrome_proc = subprocess.Popen(['google-chrome', '--no-sandbox', '--start-maximized', url])
    
    # Wait for loading
    time.sleep(10)
    
    # Capture screenshot
    screenshot_path = '/home/ubuntu/.openclaw/workspace/music_web_test.png'
    pyautogui.screenshot(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")
    
    # Give it some more time
    time.sleep(2)
    
    # Optional: try to click something to ensure interactivity
    # But for a basic "test", a screenshot is good enough.
    
    # Clean up (optional)
    # chrome_proc.terminate()

if __name__ == "__main__":
    test_website()
