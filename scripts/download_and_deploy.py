#!/usr/bin/env python3
"""
通过HTTP传输文件到宝塔服务器
"""

import requests
import hashlib
import time
import json

# 宝塔配置
BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

# 文件源（我的机器）
FILE_SERVER = "http://10.7.0.5:8888"

# 目标位置
DOMAIN = "ceshi.dhmip.cn"
WEB_ROOT = f"/www/wwwroot/{DOMAIN}"

def get_token():
    """生成宝塔API token"""
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
    
    print(f"📡 执行命令...")
    try:
        response = requests.post(url, data=payload, timeout=60)
        result = response.json()
        return result
    except Exception as e:
        return {"status": False, "msg": str(e)}

def main():
    print("="*60)
    print("🚀 保质期管理系统 - 文件传输部署")
    print("="*60)
    
    # 步骤1: 下载文件
    print("\n📍 步骤1: 从文件服务器下载PHP文件...")
    
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
        print(f"\n$ {cmd}")
        result = bt_exec(cmd)
        if result.get("status"):
            output = result.get("msg", "")
            if output:
                print(f"✅ {output[:200]}")
            else:
                print("✅ 执行成功")
        else:
            print(f"❌ 失败: {result.get('msg')}")
    
    # 步骤2: 导入数据库
    print("\n📍 步骤2: 导入数据库结构...")
    
    db_commands = [
        # 创建数据库（如果不存在）
        f"mysql -u root -e \"CREATE DATABASE IF NOT EXISTS expiry_system DEFAULT CHARACTER SET utf8mb4;\"",
        
        # 创建用户（如果不存在）
        f"mysql -u root -e \"CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry@2026System!';\"",
        
        # 授权
        f"mysql -u root -e \"GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';\"",
        
        # 刷新权限
        f"mysql -u root -e \"FLUSH PRIVILEGES;\"",
        
        # 下载SQL文件
        f"cd /tmp && curl -s {FILE_SERVER}/database.sql -o expiry_system.sql",
        
        # 导入数据
        f"mysql -u expiry_user -pExpiry@2026System! expiry_system < /tmp/expiry_system.sql"
    ]
    
    for cmd in db_commands:
        print(f"\n$ {cmd[:80]}...")
        result = bt_exec(cmd)
        if result.get("status"):
            print("✅ 执行成功")
        else:
            print(f"⚠️  {result.get('msg')}")
    
    # 步骤3: 测试部署
    print("\n📍 步骤3: 测试部署...")
    
    try:
        response = requests.get(f"http://{DOMAIN}", timeout=10)
        print(f"✅ HTTP状态: {response.status_code}")
        
        # 检查页面内容
        if "保质期" in response.text:
            print("✅ 页面内容验证成功！")
        elif "index" in response.text.lower():
            print("⚠️  仍显示默认页面，请手动刷新")
        else:
            print(f"⚠️  页面内容未知")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    print(f"🌐 访问地址: http://{DOMAIN}")
    print("")
    print("🧪 测试SKU：")
    print("   6901234567890 → 可口可乐 500ml")
    print("   6901234567891 → 康师傅红烧牛肉面")
    print("="*60)

if __name__ == "__main__":
    main()
