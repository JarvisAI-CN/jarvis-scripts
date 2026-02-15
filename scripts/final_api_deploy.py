#!/usr/bin/env python3
"""
保质期管理系统 - 通过宝塔API直接下载部署
"""

import requests
import hashlib
import time

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
    
    print(f"📡 API调用: ExecShell")
    try:
        response = requests.post(url, data=payload, timeout=120)
        result = response.json()
        return result
    except Exception as e:
        return {"status": False, "msg": str(e)}

def main():
    print("="*60)
    print("🚀 保质期管理系统 - API自动部署")
    print("="*60)
    
    # 检查临时文件服务器
    print("\n📍 步骤0: 检查文件服务器...")
    try:
        check = requests.get(f"{FILE_SERVER}/index.php", timeout=5)
        if check.status_code == 200:
            print(f"✅ 文件服务器正常: {FILE_SERVER}")
        else:
            print(f"⚠️ 文件服务器响应: {check.status_code}")
    except:
        print("❌ 文件服务器不可访问，启动中...")
        # 启动文件服务器
        import subprocess
        subprocess.Popen([
            'python3', '-m', 'http.server', '8888',
            '--directory', '/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package'
        ], cwd='/home/ubuntu/.openclaw/workspace', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
    
    # 步骤1: 下载PHP文件
    print("\n📍 步骤1: 下载PHP文件到网站目录...")
    
    commands = [
        f"cd {WEB_ROOT}",
        f"curl -s {FILE_SERVER}/index.php -o index.php",
        f"curl -s {FILE_SERVER}/db.php -o db.php",
        f"chmod 644 {WEB_ROOT}/*.php",
        f"chown www:www {WEB_ROOT}/*.php",
        f"ls -lh {WEB_ROOT}/*.php"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"\n[{i}/{len(commands)}] {cmd[:80]}")
        result = bt_exec(cmd)
        
        if result.get("status"):
            output = result.get("msg", "")
            if output and len(output) > 0:
                print(f"✅ {output[:200]}")
            else:
                print("✅ 执行成功")
        else:
            print(f"⚠️ {result.get('msg', '未知错误')}")
    
    # 测试部署
    print("\n📍 步骤2: 测试部署...")
    try:
        response = requests.get(f"http://{DOMAIN}", timeout=10)
        print(f"✅ HTTP状态: {response.status_code}")
        
        content = response.text
        if "保质期" in content:
            print("✅ 页面内容验证成功！")
            print("\n" + "="*60)
            print("🎉 部署完全成功！")
            print("="*60)
            print(f"🌐 访问地址: http://{DOMAIN}")
            print("")
            print("🧪 测试账号:")
            print("   SKU: 6901234567890 → 可口可乐 500ml")
            print("   SKU: 6901234567891 → 康师傅红烧牛肉面")
            print("="*60)
        elif "index" in content.lower() or "nginx" in content.lower():
            print("⚠️ 仍显示默认页面，等待nginx刷新...")
            time.sleep(5)
            # 重新测试
            response = requests.get(f"http://{DOMAIN}", timeout=10)
            if "保质期" in response.text:
                print("✅ 刷新后验证成功！")
            else:
                print("❌ 仍无法访问，请检查")
        else:
            print("⚠️ 页面内容未知")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    main()
