import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def bt_go_to_files():
    # Assuming already logged in from previous script
    # Click "Files" on the left sidebar (guessing coordinates)
    print("Navigating to Files...")
    pyautogui.click(100, 280) # Adjust based on BT layout
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_files_list.png')
    
    # Enter the path directly if there's a path input
    # Usually BT has a path input at the top.
    # I'll try to click it. (Guessing x=400, y=100)
    pyautogui.click(500, 110)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('/www/wwwroot/yinyue.dhmip.cn')
    pyautogui.press('enter')
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_site_files.png')

if __name__ == "__main__":
    bt_go_to_files()
