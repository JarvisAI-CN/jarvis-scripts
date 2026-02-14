import pyautogui
import time
import os

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

# Credentials
USERNAME = 'fs123'
PASSWORD = 'fs123456'
TARGET_DOMAIN = 'yinyue.dhmip.cn'

def main():
    print("Step 1: Focus browser and close popups")
    pyautogui.click(666, 432) # Click window center
    time.sleep(0.5)
    pyautogui.press('esc')
    time.sleep(0.5)
    pyautogui.press('esc')
    time.sleep(1)

    print("Step 2: Navigate to fields and login")
    # First TAB usually lands in the address bar or a popup. 
    # Let's try to click the first input field directly if possible, or Tab until we see something.
    # In the test, Tab 1 landed in Account.
    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(USERNAME, interval=0.1)
    time.sleep(0.5)

    pyautogui.press('tab')
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite(PASSWORD, interval=0.1)
    time.sleep(0.5)

    # Login
    pyautogui.press('tab') # Dropdown
    time.sleep(0.2)
    pyautogui.press('tab') # Login button
    time.sleep(0.2)
    pyautogui.press('enter')
    
    print("Waiting for dashboard...")
    time.sleep(15)
    pyautogui.screenshot('/tmp/bt_dash.png')

    print("Step 3: Navigate to Websites")
    # Left menu "网站" is usually the second or third item.
    # Keyboard shortcut for search is often '/' or 's'.
    # Let's click on the left sidebar area.
    pyautogui.click(100, 200) 
    time.sleep(2)
    
    # Take screenshot of Sidebar
    pyautogui.screenshot('/tmp/bt_sidebar.png')
    
    # Try to find the "网站" link. It's usually at the top of the menu.
    # Let's try to click it.
    pyautogui.click(100, 120) 
    time.sleep(5)
    pyautogui.screenshot('/tmp/bt_websites.png')

    print("Step 4: Find and click target domain")
    # Search for the domain in the page.
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(1)
    pyautogui.typewrite(TARGET_DOMAIN, interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('esc') # Close search bar
    
    # The browser should have scrolled to the domain.
    # The domain is a link. We can try to click it.
    # Or just use the search box in Baota if it has one.
    # Baota usually has a search input for websites at the top right of the table.
    
    # Let's take a look at the websites list first.
    # We'll stop here and check the screenshots.

if __name__ == "__main__":
    main()
