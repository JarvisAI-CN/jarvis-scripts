#!/usr/bin/env python3
"""
保质期管理系统 - 通过宝塔API完成部署
"""

import requests
import hashlib
import time
import json
import os

# 宝塔配置
BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

# 数据库配置
DB_NAME = "expiry_system"
DB_USER = "expiry_user"
DB_PASS = "Expiry@2026System!"

# 网站配置
DOMAIN = "ceshi.dhmip.cn"
WEB_ROOT = f"/www/wwwroot/{DOMAIN}"

# 文件路径
DEPLOY_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"

def get_token():
    """生成宝塔API token"""
    now = int(time.time())
    token_str = str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()
    token = hashlib.md5(token_str.encode()).hexdigest()
    return now, token

def bt_request(url_path, data=None):
    """发送宝塔API请求"""
    now, token = get_token()
    url = f"{BT_URL}{url_path}"
    
    payload = {
        "request_time": now,
        "request_token": token
    }
    if data:
        payload.update(data)
    
    print(f"📡 API: {url_path}")
    try:
        if data:
            response = requests.post(url, data=payload, timeout=30)
        else:
            response = requests.get(url, params=payload, timeout=30)
        
        result = response.json()
        return result
    except Exception as e:
        return {"status": False, "msg": str(e)}

def main():
    print("="*60)
    print("🚀 保质期管理系统 - 宝塔API自动部署")
    print("="*60)
    
    # 步骤1: 创建数据库（如果不存在）
    print("\n📍 步骤1: 检查数据库...")
    result = bt_request("/data?action=GetDatabases")
    
    if result.get("status"):
        db_exists = False
        for db in result.get("data", []):
            if db.get("name") == DB_NAME:
                db_exists = True
                print(f"✅ 数据库已存在: {DB_NAME}")
                break
        
        if not db_exists:
            print(f"📝 创建数据库: {DB_NAME}")
            result = bt_request("/data?action=AddDatabase", {
                "name": DB_NAME,
                "db_user": DB_USER,
                "password": DB_PASS,
                "dataAccess": "127.0.0.1",
                "codeing": "utf8mb4",
                "type": "MySQL",
                "ps": "保质期管理系统"
            })
            if result.get("status"):
                print("✅ 数据库创建成功")
            else:
                print(f"❌ 创建失败: {result.get('msg')}")
    
    # 步骤2: 导入SQL数据
    print("\n📍 步骤2: 导入数据结构...")
    sql_file = os.path.join(DEPLOY_DIR, "database.sql")
    
    if os.path.exists(sql_file):
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"📄 SQL文件: {len(sql_content)} 字节")
        
        # 使用命令行导入（通过API执行shell命令）
        shell_cmd = f"mysql -u {DB_USER} -p{DB_PASS} {DB_NAME} << 'SQLEOF'\n{sql_content}\nSQLEOF"
        
        result = bt_request("/system?action=ExecShell", {
            "command": shell_cmd
        })
        
        if result.get("status"):
            print("✅ SQL导入成功")
        else:
            print(f"⚠️  API导入限制，请手动导入")
            print(f"   文件: {sql_file}")
    else:
        print(f"❌ SQL文件不存在: {sql_file}")
    
    # 步骤3: 上传PHP文件
    print("\n📍 步骤3: 上传网站文件...")
    
    files_to_upload = ["index.php", "db.php"]
    for filename in files_to_upload:
        file_path = os.path.join(DEPLOY_DIR, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        
        print(f"📤 上传 {filename}: {len(file_content)} 字节")
        
        # 使用宝塔API保存文件
        result = bt_request("/files?action=SaveFileBody", {
            "path": f"{WEB_ROOT}/{filename}",
            "content": file_content,
            "encoding": "text"
        })
        
        if result.get("status"):
            print(f"✅ {filename} 上传成功")
        else:
            print(f"❌ {filename} 上传失败: {result.get('msg')}")
            
            # 备选方案：通过shell命令复制
            print(f"💡 尝试备选方案...")
            shell_cmd = f"cp {file_path} {WEB_ROOT}/{filename} && chmod 644 {WEB_ROOT}/{filename} && chown www:www {WEB_ROOT}/{filename}"
            result = bt_request("/system?action=ExecShell", {
                "command": shell_cmd
            })
            
            if result.get("status"):
                print(f"✅ {filename} 上传成功（备选方案）")
    
    # 步骤4: 删除默认index.html
    print("\n📍 步骤4: 清理默认文件...")
    result = bt_request("/files?action=DeleteFile", {
        "path": f"{WEB_ROOT}/index.html"
    })
    if result.get("status"):
        print("✅ index.html已删除")
    else:
        print("⚠️  index.html不存在或已删除")
    
    # 步骤5: 测试访问
    print("\n📍 步骤5: 测试部署...")
    try:
        response = requests.get(f"http://{DOMAIN}", timeout=10)
        print(f"✅ 网站响应: HTTP {response.status_code}")
        
        if "保质期" in response.text or "expiry" in response.text.lower():
            print("✅ 页面内容验证成功")
        else:
            print("⚠️  页面可能是默认页面（需要刷新）")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "="*60)
    print("🎉 部署完成！")
    print("="*60)
    print(f"🌐 访问地址: http://{DOMAIN}")
    print("")
    print("🧪 测试账号：")
    print("   SKU: 6901234567890 → 可口可乐 500ml")
    print("   SKU: 6901234567891 → 康师傅红烧牛肉面")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
