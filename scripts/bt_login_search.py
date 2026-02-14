import pyautogui
import time
import os
from PIL import Image

os.environ['DISPLAY'] = ':1'
pyautogui.FAILSAFE = False

def find_green_button():
    img = pyautogui.screenshot()
    width, height = img.size
    for x in range(0, width, 5):
        for y in range(0, height, 5):
            r, g, b = img.getpixel((x, y))
            # Search for the green login button color
            if r < 50 and g > 150 and b < 80:
                return x, y
    return None

def find_input_box():
    img = pyautogui.screenshot()
    width, height = img.size
    # Search for the white input box color inside the dark grey area
    for x in range(300, 1000, 5):
        for y in range(300, 600, 5):
            r, g, b = img.getpixel((x, y))
            if r > 250 and g > 250 and b > 250:
                return x, y
    return None

print("Searching for elements...")
green_pos = find_green_button()
input_pos = find_input_box()

if input_pos:
    print(f"Found input area at {input_pos}")
    # The first white box is Account, second is Password.
    # Let's click the first one.
    pyautogui.click(input_pos[0] + 10, input_pos[1] + 10)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123', interval=0.1)
    
    # Click 50 pixels below for password
    pyautogui.click(input_pos[0] + 10, input_pos[1] + 60)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.typewrite('fs123456', interval=0.1)
    
    if green_pos:
        print(f"Clicking green button at {green_pos}")
        pyautogui.click(green_pos)
    else:
        pyautogui.press('enter')
else:
    print("Could not find input area.")

time.sleep(10)
pyautogui.screenshot('/tmp/vnc_screen_search_click.png')
