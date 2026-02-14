#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM转换在线工具测试
在浏览器中打开NCM转换网站并测试
"""

import subprocess
import time
import os

NCM_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"
ONLINE_TOOLS = [
    "https://ncm.kwasu.cc/",
    "https://tools.liumingye.cn/music/",
    "https://gitncm.github.io/"
]

def check_file():
    """检查NCM文件"""
    if os.path.exists(NCM_FILE):
        size = os.path.getsize(NCM_FILE) / (1024 * 1024)
        print(f"✅ NCM文件存在: {NCM_FILE}")
        print(f"📊 文件大小: {size:.2f} MB")
        return True
    else:
        print(f"❌ NCM文件不存在: {NCM_FILE}")
        return False

def start_chrome_with_tool(url):
    """启动Chrome浏览器访问转换工具"""
    print(f"\n🌐 访问在线工具: {url}")
    
    # 启动Chrome（在VNC环境中）
    chrome_cmd = [
        "/opt/google/chrome/chrome",
        "--no-sandbox",
        "--disable-gpu",
        f"--remote-debugging-port=9222",
        url,
        f"--user-data-dir=/tmp/chrome_ncm_test"
    ]
    
    try:
        process = subprocess.Popen(
            chrome_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                "DISPLAY": ":1",  # VNC显示
                **subprocess.os.environ
            }
        )
        
        print(f"✅ Chrome已启动 (PID: {process.pid})")
        print(f"📝 提示: 在VNC中查看浏览器窗口")
        print(f"🔧 VNC访问: http://服务器IP:6080/vnc.html")
        print("")
        print("📋 手动操作步骤:")
        print("   1. 在浏览器中找到上传按钮")
        print("   2. 选择NCM文件进行上传")
        print("   3. 等待转换完成")
        print("   4. 下载转换后的文件")
        print("")
        print(f"💾 文件路径: {NCM_FILE}")
        
        return True
    except Exception as e:
        print(f"❌ Chrome启动失败: {str(e)}")
        return False

def main():
    print("="*60)
    print("🎵 NCM在线转换工具测试")
    print("="*60)
    print("")
    
    # 检查文件
    if not check_file():
        return
    
    print("")
    print("🌐 在线转换工具列表:")
    for i, tool in enumerate(ONLINE_TOOLS, 1):
        print(f"   {i}. {tool}")
    print("")
    
    # 启动第一个工具（最常用）
    print("🚀 启动Chrome浏览器...")
    success = start_chrome_with_tool(ONLINE_TOOLS[0])
    
    if success:
        print("\n" + "="*60)
        print("✅ 浏览器已启动")
        print("="*60)
        print("")
        print("💡 如果第一个工具不行，可以尝试其他工具:")
        for tool in ONLINE_TOOLS[1:]:
            print(f"   - {tool}")
        print("")
        print("⏳ 等待你在VNC中完成测试...")
        print("   测试完成后告诉我结果")
    else:
        print("\n" + "="*60)
        print("❌ 无法启动浏览器")
        print("="*60)
        print("")
        print("🔧 手动访问:")
        for tool in ONLINE_TOOLS:
            print(f"   {tool}")
        print("")
        print("📝 文件位置:")
        print(f"   {NCM_FILE}")

if __name__ == "__main__":
    main()
