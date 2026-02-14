#!/usr/bin/env python3
import hashlib
import time
import requests
import json

BT_URL = "http://82.157.20.7:8888/fs123456"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

def get_token():
    now = int(time.time())
    token = hashlib.md5((str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()).encode()).hexdigest()
    return now, token

def list_temp_files():
    now, token = get_token()
    url = f"{BT_URL}/files?action=GetFileBody"
    data = {
        "request_time": now,
        "request_token": token,
        "path": "www/wwwroot/yinyue.dhmip.cn/temp"
    }
    
    try:
        r = requests.post(url, data=data, timeout=10)
        
        # 打印原始响应用于调试
        print(f"Status Code: {r.status_code}")
        print(f"Response Text (first 500 chars): {r.text[:500]}")
        
        files_data = r.json()
        
        if 'FILE' in files_data:
            files = files_data['FILE']
            print(f"\n📁 临时目录文件列表 (共{len(files)}个)：")
            print("-" * 80)
            for i, file in enumerate(files, 1):
                size_mb = int(file['size']) / (1024 * 1024)
                print(f"  {i}. {file['name']:<40} ({size_mb:>6}MB)  {file['time']}")
            
            # 查找最新的FLAC文件
            flac_files = [f for f in files if f['name'].endswith('.flac')]
            if flac_files:
                print(f"\n🎵 最新的FLAC文件：")
                for f in flac_files[-3:]:
                    size_mb = int(f['size']) / (1024 * 1024)
                    print(f"  - {f['name']:<40} ({size_mb:>6}MB)  {f['time']}")
            else:
                print("\n⚠️  未找到FLAC文件")
        else:
            print(f"❌ API错误：{files_data}")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 错误：{e}")

if __name__ == "__main__":
    list_temp_files()
