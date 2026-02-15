#!/usr/bin/env python3
"""
通过宝塔终端自动下载文件并完成部署
"""

import requests
import hashlib
import time
import json

BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

DOMAIN = "ceshi.dhmip.cn"
WEB_ROOT = f"/www/wwwroot/{DOMAIN}"
FILE_SERVER = "http://10.7.0.5:8888"

def get_token():
    now = int(time.time())
    token_str = str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()
    token = hashlib.md5(token_str.encode()).hexdigest()
    return now, token

def bt_exec(command):
    """通过宝塔API执行shell命令"""
    now, token = get_token()
    url = f"{BT_URL}/system?action=ExecShell"
    
    payload = {
        "request_time": now,
        "request_token": token,
        "command": command
    }
    
    try:
        response = requests.post(url, data=payload, timeout=60)
        result = response.json()
        return result
    except Exception as e:
        return {"status": False, "msg": str(e)}

def main():
    print("="*60)
    print("🚀 保质期管理系统 - 自动下载文件部署")
    print("="*60)
    
    # 构建下载命令
    commands = [
        # 下载index.php
        f"cd {WEB_ROOT} && curl -s {FILE_SERVER}/index.php -o index.php",
        
        # 下载db.php
        f"cd {WEB_ROOT} && curl -s {FILE_SERVER}/db.php -o db.php",
        
        # 设置权限
        f"chmod 644 {WEB_ROOT}/*.php",
        f"chown www:www {WEB_ROOT}/*.php",
        
        # 验证文件
        f"ls -lh {WEB_ROOT}/*.php"
    ]
    
    for cmd in commands:
        print(f"\n📡 执行命令...")
        print(f"$ {cmd[:100]}")
        
        result = bt_exec(cmd)
        
        if result.get("status"):
            output = result.get("msg", "")
            if output and len(output) > 100:
                print(f"✅ {output[:100]}")
            elif output:
                print(f"✅ {output}")
            else:
                print("✅ 执行成功")
        else:
            print(f"❌ 失败: {result.get('msg')}")
    
    # 测试访问
    print("\n🧪 测试部署...")
    try:
        response = requests.get(f"http://{DOMAIN}", timeout=10)
        print(f"✅ HTTP状态: {response.status_code}")
        
        if "保质期" in response.text:
            print("✅ 页面内容验证成功！")
        elif "index" in response.text.lower():
            print("⚠️  仍显示默认页面，请刷新")
        else:
            print("⚠️  页面内容未知")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    print(f"🌐 访问地址: http://{DOMAIN}")
    print("")
    print("🧪 测试账号:")
    print("   SKU: 6901234567890 → 可口可乐 500ml")
    print("   SKU: 6901234567891 → 康师傅红烧牛肉面")
    print("="*60)

if __name__ == "__main__":
    main()
