#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebDAV文件下载工具
"""

import requests
from urllib.parse import quote
import os

# WebDAV配置
WEBDAV_BASE = "https://webdav.123pan.cn/webdav"
USERNAME = "13220103449"
PASSWORD = "ls8h74pb"

# 文件路径
REMOTE_FILE = "/共享资源/梓渝 - 萤火星球.ncm"
LOCAL_DIR = "/home/ubuntu/music_test"
LOCAL_FILE = f"{LOCAL_DIR}/梓渝 - 萤火星球.ncm"

def download_file():
    """下载文件"""
    # 创建本地目录
    os.makedirs(LOCAL_DIR, exist_ok=True)

    # URL编码路径
    encoded_path = quote(REMOTE_FILE)
    url = f"{WEBDAV_BASE}{encoded_path}"

    print(f"📥 下载文件: {REMOTE_FILE}")
    print(f"🔗 URL: {url}")
    print(f"💾 保存到: {LOCAL_FILE}")

    try:
        # 下载文件
        response = requests.get(
            url,
            auth=(USERNAME, PASSWORD),
            stream=True,
            timeout=120
        )

        if response.status_code == 200:
            # 获取文件大小
            file_size = int(response.headers.get('content-length', 0))
            file_size_mb = file_size / (1024 * 1024)

            print(f"✅ 连接成功，文件大小: {file_size_mb:.2f} MB")
            print(f"⏳ 正在下载...")

            # 写入文件
            with open(LOCAL_FILE, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # 显示进度
                        if downloaded % (1024 * 1024) == 0:  # 每MB显示一次
                            progress = (downloaded / file_size) * 100
                            print(f"   进度: {progress:.1f}%")

            print(f"✅ 下载完成: {LOCAL_FILE}")
            print(f"📊 文件大小: {file_size_mb:.2f} MB")
            return True

        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return False

    except Exception as e:
        print(f"❌ 下载异常: {str(e)}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("🎵 WebDAV文件下载工具")
    print("="*60)

    success = download_file()

    print("="*60)

    if success:
        print(f"✅ 下载成功！")
        print(f"📂 文件位置: {LOCAL_FILE}")
        print(f"💡 下一步: 测试NCM格式转换")
    else:
        print(f"❌ 下载失败")
        print(f"💡 建议: 检查WebDAV配置和网络连接")

    print("="*60)
