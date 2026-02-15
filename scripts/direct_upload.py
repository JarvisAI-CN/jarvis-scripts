#!/usr/bin/env python3
"""
通过curl直接向宝塔面板发送文件上传请求
"""

import requests
import hashlib
import time
import os
import base64

BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

DOMAIN = "ceshi.dhmip.cn"
WEB_ROOT = f"/www/wwwroot/{DOMAIN}"

DEPLOY_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"

def get_token():
    now = int(time.time())
    token_str = str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()
    token = hashlib.md5(token_str.encode()).hexdigest()
    return now, token

def main():
    print("="*60)
    print("🚀 直接文件上传到宝塔服务器")
    print("="*60)
    
    # 读取PHP文件
    files_to_upload = ["index.php", "db.php"]
    
    for filename in files_to_upload:
        file_path = os.path.join(DEPLOY_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📤 {filename}: {len(content)} 字节")
        
        # 方法1：尝试直接POST到文件上传API
        now, token = get_token()
        
        # 方法2：使用files API保存文件内容
        try:
            # 编码文件内容
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # 使用SaveFileBody API
            url = f"{BT_URL}/files?action=SaveFileBody"
            payload = {
                "request_time": now,
                "request_token": token,
                "path": f"{WEB_ROOT}/{filename}",
                "content": encoded_content,
                "encoding": "base64"
            }
            
            print(f"📡 上传到: {url}")
            response = requests.post(url, data=payload, timeout=60)
            result = response.json()
            
            if result.get("status"):
                print(f"✅ {filename} 上传成功")
            else:
                print(f"❌ {filename} 上传失败: {result.get('msg')}")
                
                # 备用方案：创建临时文件让宝塔服务器下载
                print(f"💡 使用备用方案...")
                # 启动临时HTTP服务器
                import subprocess
                subprocess.Popen(['python3', '-m', 'http.server', '8889'],
                              cwd=DEPLOY_DIR,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
                time.sleep(2)
                
                # 通知用户使用curl下载
                print(f"\n⚠️  请在宝塔终端执行:")
                print(f"cd {WEB_ROOT}")
                print(f"curl http://10.7.0.5:8889/{filename} -o {filename}")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    # 验证
    print("\n🧪 验证部署...")
    try:
        response = requests.get(f"http://{DOMAIN}", timeout=10)
        print(f"HTTP状态: {response.status_code}")
        
        if response.status_code == 200 and "保质期" in response.text:
            print("✅ 部署成功！")
        else:
            print("⚠️  需要验证")
    except Exception as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
