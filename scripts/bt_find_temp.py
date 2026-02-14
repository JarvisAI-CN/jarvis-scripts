#!/usr/bin/env python3
import hashlib
import time
import requests

BT_URL = "http://82.157.20.7:8888/fs123456"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

def get_token():
    now = int(time.time())
    token = hashlib.md5((str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()).encode()).hexdigest()
    return now, token

def find_temp_dir():
    # 尝试多个可能的临时文件位置
    paths_to_check = [
        "www/wwwroot/yinyue.dhmip.cn/temp",
        "www/wwwroot/yinyue.dhmip.cn/scripts/temp",
        "www/wwwroot/yinyue.dhmip.cn",
        "var/www/html/yinyue.dhmip.cn/temp",
        "home/ubuntu/.openclaw/workspace/PARA/Projects/ncm-to-flac-web/temp",
        "home/ubuntu/.openclaw/workspace/PARA/Projects/ncm-to-flac-web",
    ]
    
    now, token = get_token()
    
    for path in paths_to_check:
        url = f"{BT_URL}/files?action=GetFileBody"
        data = {
            "request_time": now,
            "request_token": token,
            "path": path
        }
        
        try:
            r = requests.post(url, data=data, timeout=10)
            if r.status_code == 200:
                try:
                    files_data = r.json()
                    if 'FILE' in files_data and len(files_data['FILE']) > 0:
                        print(f"✅ 找到文件位置：{path}")
                        print(f"   文件数量：{len(files_data['FILE'])}")
                        return path, files_data['FILE']
                except:
                    pass
        except:
            pass
    
    return None, None

if __name__ == "__main__":
    print("🔍 正在搜索临时文件目录...")
    result = find_temp_dir()
    
    if result[0]:
        path, files = result
        print(f"\n📁 目录 [{path}] 的内容：")
        print("-" * 80)
        
        # 查找FLAC文件
        flac_files = [f for f in files if f['name'].endswith('.flac')]
        ncms = [f for f in files if f['name'].endswith('.ncm')]
        temps = [f for f in files if not (f['name'].endswith('.flac') or f['name'].endswith('.ncm'))]
        
        print(f"\n📊 文件类型统计：")
        print(f"   FLAC文件: {len(flac_files)}")
        print(f"   NCM文件: {len(ncms)}")
        print(f"   临时文件: {len(temps)}")
        
        if flac_files:
            print(f"\n🎵 最近转换的FLAC文件：")
            for f in flac_files[-5:]:
                size_mb = int(f['size']) / (1024 * 1024)
                print(f"  - {f['name']:<60} ({size_mb:>6}MB)  {f['time']}")
        else:
            print("\n⚠️  未找到FLAC文件")
    else:
        print("\n❌ 未找到有效的临时文件目录")
