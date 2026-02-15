import os
import time
import pyautogui

os.environ['DISPLAY'] = ':1'

def login_with_captcha(captcha_text):
    username = "fs123"
    password = "fs123456"
    
    # 假设浏览器已经在那儿了
    print(f"Typing login details with captcha: {captcha_text}")
    
    # Click username field
    pyautogui.click(350, 375) # Based on image
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write(username)
    
    # Click password field
    pyautogui.click(350, 425)
    pyautogui.write(password)
    
    # Click captcha field
    pyautogui.click(300, 525)
    pyautogui.write(captcha_text)
    
    # Click Login
    pyautogui.click(350, 575)
    time.sleep(5)
    pyautogui.screenshot('/home/ubuntu/.openclaw/workspace/bt_after_login_attempt.png')

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        login_with_captcha(sys.argv[1])
    else:
        print("Please provide captcha text")
