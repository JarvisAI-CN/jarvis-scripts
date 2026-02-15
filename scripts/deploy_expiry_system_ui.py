import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def deploy_baota():
    bt_url = "http://82.157.20.7:8888/fs123456"
    username = "fs123"
    password = "fs123456"
    domain = "ceshi.dhmip.cn"
    
    print(f"🚀 Starting Baota deployment for {domain}...")
    
    # 1. Launch Chrome and login
    pyautogui.hotkey('alt', 'f2')
    time.sleep(1)
    pyautogui.write('google-chrome --no-sandbox ' + bt_url)
    pyautogui.press('enter')
    time.sleep(10)
    
    # Login process
    pyautogui.press('tab', presses=2)
    pyautogui.write(username)
    pyautogui.press('tab')
    pyautogui.write(password)
    pyautogui.press('enter')
    time.sleep(8)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_logged_in.png')
    
    # 2. Click "Website" (usually first or second menu on left)
    # Based on previous screenshots, menu is on the left.
    # Coordinates for "网站" menu item (estimated)
    pyautogui.click(80, 180) 
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_website_page.png')
    
    # 3. Click "Add Website"
    # Usually a blue button at the top
    pyautogui.click(180, 110)
    time.sleep(3)
    pyautogui.write(domain)
    
    # Fill description (optional)
    pyautogui.press('tab', presses=2)
    pyautogui.write('Expiry System')
    
    # Set PHP version to 7.4 or higher (usually 8.x is better)
    # Usually it's a dropdown.
    
    # Click "Submit" (usually bottom right of dialog)
    pyautogui.click(850, 750) # Estimated submit button location
    time.sleep(10)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_site_added.png')

if __name__ == "__main__":
    deploy_baota()
