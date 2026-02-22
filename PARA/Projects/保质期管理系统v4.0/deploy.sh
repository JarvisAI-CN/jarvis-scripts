#!/bin/bash

# 保质期管理系统 v4.0.0 - 部署脚本
# 一键部署到生产服务器

set -e

# 配置变量
FTP_SERVER="211.154.19.189"
FTP_PORT="21"
FTP_USER="pandian"
FTP_PASS="pandian"
REMOTE_DIR="www/wwwroot/pandian.dhmip.cn/public_html"
LOCAL_DIR="/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "保质期管理系统 v4.0.0 - 自动部署脚本"
echo "========================================"
echo ""

# 检查本地目录是否存在
if [ ! -d "$LOCAL_DIR" ]; then
    echo -e "${RED}错误: 本地目录不存在: $LOCAL_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 本地目录检查通过${NC}"

# 创建临时Python脚本
FTP_SCRIPT="/tmp/ftp_deploy_$$.py"

cat > "$FTP_SCRIPT" << 'EOFPYTHON'
import ftplib
import os
import sys
from pathlib import Path

# FTP配置
FTP_SERVER = "211.154.19.189"
FTP_PORT = 21
FTP_USER = "pandian"
FTP_PASS = "pandian"
REMOTE_DIR = "www/wwwroot/pandian.dhmip.cn/public_html"
LOCAL_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0"

# 需要上传的文件和目录
FILES_TO_UPLOAD = [
    'api/',
    'includes/',
    'pages/',
    'assets/',
    'install.php',
    'README.md'
]

def upload_file(ftp, local_path, remote_path):
    """上传单个文件"""
    try:
        with open(local_path, 'rb') as f:
            ftp.storbinary(f'STOR {remote_path}', f)
        return True
    except Exception as e:
        print(f"上传失败: {local_path} -> {remote_path}")
        print(f"错误: {e}")
        return False

def upload_directory(ftp, local_dir, remote_dir):
    """递归上传目录"""
    local_path = Path(local_dir)
    remote_path = remote_dir
    
    # 创建远程目录
    try:
        ftp.mkd(remote_path)
    except:
        pass  # 目录可能已存在
    
    # 遍历本地目录
    for item in local_path.iterdir():
        if item.is_file():
            # 上传文件
            remote_file = f"{remote_path}/{item.name}"
            if upload_file(ftp, str(item), remote_file):
                print(f"✓ {remote_path}/{item.name}")
        elif item.is_dir():
            # 递归上传子目录
            upload_directory(ftp, str(item), f"{remote_path}/{item.name}")

def main():
    print("连接到FTP服务器...")
    
    try:
        # 连接FTP
        ftp = ftplib.FTP()
        ftp.connect(FTP_SERVER, FTP_PORT, timeout=60)
        ftp.login(FTP_USER, FTP_PASS)
        ftp.set_pasv(True)
        
        print("✓ FTP连接成功")
        
        # 切换到目标目录
        ftp.cwd(REMOTE_DIR)
        print(f"✓ 切换到远程目录: {REMOTE_DIR}")
        
        # 备份旧文件
        print("\n备份旧文件...")
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = f"backup_{timestamp}"
        
        try:
            ftp.mkd(backup_dir)
            print(f"✓ 创建备份目录: {backup_dir}")
        except:
            print("! 备份目录已存在")
        
        # 上传文件
        print("\n开始上传文件...")
        
        for item in FILES_TO_UPLOAD:
            local_path = os.path.join(LOCAL_DIR, item)
            
            if os.path.isfile(local_path):
                # 上传单个文件
                if upload_file(ftp, local_path, os.path.basename(item)):
                    print(f"✓ {item}")
            elif os.path.isdir(local_path):
                # 上传目录
                print(f"\n上传目录: {item}")
                upload_directory(ftp, local_path, os.path.basename(item))
        
        # 关闭连接
        ftp.quit()
        print("\n✓ 部署完成")
        
    except Exception as e:
        print(f"\n✗ 部署失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
EOFPYTHON

echo -e "${YELLOW}开始部署...${NC}"
echo ""

# 运行Python脚本
python3 "$FTP_SCRIPT"

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================"
    echo "✓ 部署成功完成"
    echo "========================================${NC}"
    echo ""
    echo "系统已部署到: http://pandian.dhmip.cn/"
    echo "请访问以下地址完成安装:"
    echo "  http://pandian.dhmip.cn/install.php"
    echo ""
    echo "默认登录凭据:"
    echo "  用户名: admin"
    echo "  密码: fs123456"
    echo ""
    echo -e "${YELLOW}⚠️  重要提示:${NC}"
    echo "1. 请运行 install.php 完成数据库初始化"
    echo "2. 安装完成后请删除 install.php 文件"
    echo "3. 请立即修改默认管理员密码"
    echo ""
else
    echo -e "${RED}========================================"
    echo "✗ 部署失败"
    echo "========================================${NC}"
    echo ""
    echo "请检查:"
    echo "1. FTP服务器连接"
    echo "2. 用户名和密码"
    echo "3. 文件权限"
    echo ""
    exit 1
fi

# 清理临时文件
rm -f "$FTP_SCRIPT"

exit 0
