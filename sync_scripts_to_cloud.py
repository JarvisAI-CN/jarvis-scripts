import os
import requests
import subprocess
import glob

# 配置
WEBDAV_USER = "13220103449"
WEBDAV_PASS = "ls8h74pb"
WEBDAV_BASE = "https://webdav.123pan.cn/webdav/"
REMOTE_SCRIPT_DIR = "备份/脚本/"
WORKSPACE = "/home/ubuntu/.openclaw/workspace"

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def ensure_remote_dir(path):
    parts = path.strip('/').split('/')
    current = ""
    for part in parts:
        current += part + "/"
        url = f"{WEBDAV_BASE}{current}"
        # 使用 PROPFIND 检查是否存在，或者直接 MKCOL
        res = requests.request("MKCOL", url, auth=(WEBDAV_USER, WEBDAV_PASS))
        # 405 Method Not Allowed 通常意味着目录已存在
    return True

def upload_file(local_path, remote_subpath):
    remote_url = f"{WEBDAV_BASE}{REMOTE_SCRIPT_DIR}{remote_subpath}"
    
    # 确保远程父目录存在
    parent_path = os.path.dirname(f"{REMOTE_SCRIPT_DIR}{remote_subpath}")
    ensure_remote_dir(parent_path)

    print(f"正在上传: {local_path} -> {remote_url}")
    with open(local_path, 'rb') as f:
        res = requests.put(remote_url, data=f, auth=(WEBDAV_USER, WEBDAV_PASS))
    
    if res.status_code in [200, 201, 204]:
        print(f"✅ 上传成功")
    else:
        print(f"❌ 上传失败 (HTTP {res.status_code})")

def main():
    # 1. 上传恢复指南到根目录
    print("上传恢复指南...")
    upload_file(f"{WORKSPACE}/记忆恢复指南.md", "../../记忆恢复指南.md") # 相对路径修正

    # 2. 搜寻并上传脚本
    print("开始同步脚本资产...")
    
    # 获取工作区下的 .sh 和 .py
    scripts = glob.glob(f"{WORKSPACE}/*.sh") + glob.glob(f"{WORKSPACE}/*.py")
    
    # 获取 PARA 下的脚本
    para_scripts = glob.glob(f"{WORKSPACE}/PARA/Projects/*/这个项目的文件/脚本/*")
    
    all_scripts = scripts + para_scripts

    for script in all_scripts:
        if os.path.isdir(script): continue
        
        # 计算远程子路径
        rel_path = os.path.relpath(script, WORKSPACE)
        upload_file(script, rel_path)

    print("--- 同步完成 ---")

if __name__ == "__main__":
    main()
