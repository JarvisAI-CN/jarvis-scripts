#!/bin/bash

# 保质期管理系统 v4.0.0 - 部署脚本
# 使用简单可靠的方法

set -e

# 配置变量
FTP_SERVER="211.154.19.189"
FTP_USER="pandian"
FTP_PASS="pandian"
FTP_PORT="21"
REMOTE_DIR="www/wwwroot/pandian.dhmip.cn"
LOCAL_DIR="/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "保质期管理系统 v4.0.0 - 部署脚本"
echo "========================================"
echo ""

# 检查本地目录
if [ ! -d "$LOCAL_DIR" ]; then
    echo -e "${RED}错误: 本地目录不存在${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 本地目录检查通过${NC}"

# 创建简单的部署脚本
FTP_SCRIPT="/tmp/ftp_deploy_$$.py"

cat > "$FTP_SCRIPT" << 'EOFPYTHON'
import ftplib
import os
from pathlib import Path

FTP_SERVER = "211.154.19.189"
FTP_PORT = 21
FTP_USER = "pandian"
FTP_PASS = "pandian"
REMOTE_DIR = "/"
LOCAL_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0"

def upload_file(ftp, local_path, remote_file):
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_file}', f)
        return True
    except Exception as e:
        print(f"上传失败 {local_path}: {e}")
        return False

def ensure_dir(ftp, dir_name):
    try:
        ftp.cwd(dir_name)
        return True
    except:
        try:
            ftp.mkd(dir_name)
            ftp.cwd(dir_name)
            return True
        except Exception as e:
            print(f"无法创建目录 {dir_name}: {e}")
            return False

def main():
    print("连接到FTP服务器...")
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_SERVER, FTP_PORT, timeout=60)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)
        
        print(f"✅ 连接成功, 当前目录: {ftp.pwd()}")
        
        if not ensure_dir(ftp, REMOTE_DIR):
            raise Exception(f"无法访问远程目录 {REMOTE_DIR}")
        
        print(f"✅ 已在远程目录: {ftp.pwd()}")
        
        print("\n开始上传文件...")
        
        # 上传根目录文件
        root_files = ["index.php", "install.php", "README.md"]
        
        for filename in root_files:
            local_path = os.path.join(LOCAL_DIR, filename)
            if os.path.exists(local_path):
                if upload_file(ftp, local_path, filename):
                    print(f"✅ {filename}")
        
        # 上传API目录
        if os.path.exists(os.path.join(LOCAL_DIR, "api")):
            if ensure_dir(ftp, "api"):
                api_files = ["login.php", "overview.php", "logout.php", "get_product.php", "submit-inventory.php"]
                for filename in api_files:
                    local_path = os.path.join(LOCAL_DIR, "api", filename)
                    if os.path.exists(local_path):
                        if upload_file(ftp, local_path, filename):
                            print(f"✅ api/{filename}")
            ftp.cwd('..')
        
        # 上传includes目录
        if os.path.exists(os.path.join(LOCAL_DIR, "includes")):
            if ensure_dir(ftp, "includes"):
                include_files = [
                    "config.php", "db.php", "functions.php", 
                    "check_auth.php", "header.php", "footer.php"
                ]
                for filename in include_files:
                    local_path = os.path.join(LOCAL_DIR, "includes", filename)
                    if os.path.exists(local_path):
                        if upload_file(ftp, local_path, filename):
                            print(f"✅ includes/{filename}")
            ftp.cwd('..')
        
        # 上传pages目录
        if os.path.exists(os.path.join(LOCAL_DIR, "pages")):
            if ensure_dir(ftp, "pages"):
                page_files = ["login.php", "index.php", "new.php", "past.php"]
                for filename in page_files:
                    local_path = os.path.join(LOCAL_DIR, "pages", filename)
                    if os.path.exists(local_path):
                        if upload_file(ftp, local_path, filename):
                            print(f"✅ pages/{filename}")
            ftp.cwd('..')
        
        # 检查上传结果
        print("\n=== 远程目录内容 ===")
        ftp.cwd(REMOTE_DIR)
        files = []
        ftp.retrlines('LIST', files.append)
        for line in files:
            print(line)
        
        ftp.quit()
        print("\n✅ 部署完成")
        
    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        import traceback
        print(f"详细信息: {traceback.format_exc()}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()

EOFPYTHON

echo -e "${YELLOW}开始部署...${NC}"
python3 "$FTP_SCRIPT"

# 检查结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}========================================"
    echo "✅ 部署成功"
    echo "========================================${NC}"
    echo ""
    echo "访问地址: http://pandian.dhmip.cn/"
    echo "安装页面: http://pandian.dhmip.cn/install.php"
    echo ""
    echo "默认登录: admin / fs123456"
else
    echo -e "${RED}部署失败${NC}"
    exit 1
fi

# 清理
rm -f "$FTP_SCRIPT"

exit 0
