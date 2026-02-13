import pyautogui
import os
import time

os.environ['DISPLAY'] = ':1'

def inspect():
    # 启动 Chrome 并访问域名
    pyautogui.hotkey('alt', 'f2')
    time.sleep(1)
    pyautogui.write('google-chrome http://dh.dhmip.cn', interval=0.1)
    pyautogui.press('enter')
    
    # 等待页面加载
    time.sleep(10)
    
    # 截图
    save_path = '/home/ubuntu/.openclaw/workspace/PARA/Projects/网址导航网站维护项目/这个项目的文件/日志/site_inspection_2012.png'
    pyautogui.screenshot(save_path)
    print(f"Inspection screenshot saved to: {save_path}")

if __name__ == "__main__":
    inspect()
