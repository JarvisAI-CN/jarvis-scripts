import pyautogui
import os
import sys
import json
from datetime import datetime

# 设置显示器
os.environ['DISPLAY'] = ':1'

def take_snapshot():
    path = f"/home/ubuntu/.openclaw/workspace/logs/desktop_snapshot.png"
    pyautogui.screenshot(path)
    return path

def execute_action(action_type, params):
    try:
        if action_type == "click":
            pyautogui.click(params.get('x'), params.get('y'), button=params.get('button', 'left'))
        elif action_type == "type":
            pyautogui.write(params.get('text'), interval=0.1)
        elif action_type == "press":
            pyautogui.press(params.get('key'))
        elif action_type == "hotkey":
            pyautogui.hotkey(*params.get('keys'))
        elif action_type == "move":
            pyautogui.moveTo(params.get('x'), params.get('y'))
        
        snapshot = take_snapshot()
        print(json.dumps({"status": "ok", "snapshot": snapshot}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
        execute_action(data.get('action'), data.get('params', {}))
    else:
        # 默认只截图
        path = take_snapshot()
        print(json.dumps({"status": "ok", "snapshot": path}))
