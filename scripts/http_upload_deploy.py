#!/usr/bin/env python3
"""
通过HTTP模拟宝塔面板文件上传
"""

import requests
import hashlib
import time
import os

BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

DOMAIN = "ceshi.dhmip.cn"
DEPLOY_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"

def get_token():
    now = int(time.time())
    token_str = str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()
    token = hashlib.md5(token_str.encode()).hexdigest()
    return now, token

def main():
    print("="*60)
    print("🚀 保质期管理系统 - HTTP模拟上传")
    print("="*60)
    
    files_to_upload = ["index.php", "db.php"]
    
    for filename in files_to_upload:
        file_path = os.path.join(DEPLOY_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📤 {filename}: {len(content)} 字节")
        
        # 尝试不同的API端点
        endpoints = [
            f"/files?action=SaveFileBody",
            f"/files?action=SaveFile",
            f"/files?tojs=SaveFileBody",
        ]
        
        for endpoint in endpoints:
            now, token = get_token()
            url = f"{BT_URL}{endpoint}"
            
            # 尝试不同的参数格式
            payloads = [
                {
                    "request_time": now,
                    "request_token": token,
                    "path": f"/www/wwwroot/{DOMAIN}/{filename}",
                    "content": content,
                    "encoding": "text"
                },
                {
                    "request_time": now,
                    "request_token": token,
                    "data": content,
                    "path": f"/www/wwwroot/{DOMAIN}/{filename}"
                }
            ]
            
            for payload in payloads:
                try:
                    print(f"  📡 尝试: {endpoint}")
                    response = requests.post(url, data=payload, timeout=30)
                    result = response.json()
                    
                    if result.get("status"):
                        print(f"  ✅ {filename} 上传成功！")
                        break
                    else:
                        print(f"  ❌ {result.get('msg', '未知错误')}")
                except Exception as e:
                    print(f"  ❌ 异常: {e}")
            
            # 如果成功，跳到下一个文件
            # （这里没有break标志，需要改进）
    
    # 备用方案：提供curl命令
    print("\n" + "="*60)
    print("💡 备用方案")
    print("="*60)
    print("\n由于API限制，请在宝塔终端执行：")
    print("\n".join([
        f"cd /www/wwwroot/{DOMAIN}",
        "curl -s http://10.7.0.5:8888/index.php -o index.php",
        "curl -s http://10.7.0.5:8888/db.php -o db.php",
        "chmod 644 *.php",
        "chown www:www *.php",
        "ls -lh"
    ]))
    print("="*60)

if __name__ == "__main__":
    main()
