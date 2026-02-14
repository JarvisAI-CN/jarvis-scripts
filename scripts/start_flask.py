#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# 设置工作目录
WORKSPACE = '/home/ubuntu/.openclaw/workspace'
SCRIPTS_DIR = os.path.join(WORKSPACE, 'scripts')
UPLOAD_DIR = '/tmp/ncm_web_uploads'
OUTPUT_DIR = '/tmp/ncm_web_output'

def check_app():
    """检查Flask应用状态"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:5001/', timeout=2)
        is_running = response.status_code == 200
        return is_running
    except:
        return False

def start_app():
    """启动Flask应用"""
    import subprocess
    
    app_script = os.path.join(SCRIPTS_DIR, 'ncm_web_app.py')
    
    # 检查应用脚本
    if not os.path.exists(app_script):
        print(f"❌ 应用脚本不存在：{app_script}")
        return False
    
    # 创建必要目录
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"🚀 正在启动Flask应用...")
    print(f"   脚本：{app_script}")
    print(f"   上传目录：{UPLOAD_DIR}")
    print(f"   输出目录：{OUTPUT_DIR}")
    
    # 启动应用（后台运行）
    process = subprocess.Popen(
        ['python3', app_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True
    )
    
    # 等待启动
    import time
    time.sleep(3)
    
    # 检查是否运行
    if check_app():
        print("✅ Flask应用已启动")
        print(f"   进程ID：{process.pid}")
        print(f"   访问地址：http://127.0.0.1:5001/")
        print(f"   公网地址：http://yinyue.dhmip.cn/")
        return True
    else:
        print("❌ Flask应用启动失败")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'start':
            start_app()
        elif sys.argv[1] == 'check':
            running = check_app()
            print(f"状态：{'运行中' if running else '未运行'}")
        else:
            print("用法：")
            print("  python3 start_flask.py start  - 启动应用")
            print("  python3 start_flask.py check  - 检查状态")
    else:
        if start_app():
            print("\n⏰ Flask应用已启动，按Ctrl+C停止...")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 应用已停止")
