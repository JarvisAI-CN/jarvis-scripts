#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐格式转换项目测试

目标：在浏览器中测试音乐格式转换项目
"""

import subprocess
import time
from pathlib import Path

# 音乐文件位置
MUSIC_DIR = Path("/home/ubuntu/music_test")
MUSIC_DIR.mkdir(parents=True, exist_ok=True)

# 音乐转换项目URL（常见的在线工具）
CONVERSION_URLS = [
    "https://ncm.kwasu.cc/",  # NCM在线转换
    "https://tools.liumingye.cn/music/",  # 音乐工具
    "http://82.157.20.7:8000/",  # 本地可能有部署的项目
]


def start_chrome_with_music_project():
    """启动Chrome浏览器访问音乐转换项目"""
    print("="*60)
    print("🎵 启动音乐格式转换项目测试")
    print("="*60)

    # 1. 尝试本地项目
    print("\n📋 步骤1: 检查本地音乐转换项目")
    local_projects = [
        "/home/ubuntu/.openclaw/workspace/PARA/Projects/*音乐*",
        "/home/ubuntu/*music*",
        "/home/ubuntu/*ncm*"
    ]

    found_project = None
    for pattern in local_projects:
        try:
            result = subprocess.run(
                ["bash", "-c", f"ls -d {pattern} 2>/dev/null"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                found_project = result.stdout.strip().split('\n')[0]
                print(f"✅ 找到本地项目: {found_project}")
                break
        except:
            continue

    # 2. 启动Chrome浏览器
    print(f"\n🌐 步骤2: 启动Chrome浏览器")

    if found_project:
        # 如果找到本地项目，访问它
        print(f"📂 访问本地项目")
        # 这里需要根据项目类型确定URL
        url = "http://localhost:8000"  # 假设
    else:
        # 否则访问在线工具
        print(f"🌍 访问在线NCM转换工具")
        url = CONVERSION_URLS[0]

    # 启动Chrome（在VNC环境中）
    chrome_cmd = [
        "/opt/google/chrome/chrome",
        "--no-sandbox",
        "--disable-gpu",
        f"--remote-debugging-port=9222",
        url,
        f"--user-data-dir=/tmp/chrome_music_test"
    ]

    print(f"🚀 启动命令: {' '.join(chrome_cmd)}")

    try:
        # 在后台启动Chrome
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

        # 等待几秒
        time.sleep(3)

        # 检查进程状态
        if process.poll() is None:
            print(f"✅ Chrome运行正常")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Chrome启动失败")
            print(f"stderr: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"❌ 启动Chrome异常: {str(e)}")
        return False


def test_music_file_upload():
    """测试音乐文件上传"""
    print(f"\n📤 步骤3: 测试音乐文件上传")
    print(f"⚠️  需要手动在浏览器中:")
    print(f"   1. 点击上传按钮")
    print(f"   2. 选择NCM文件")
    print(f"   3. 等待转换完成")
    print(f"   4. 下载转换后的文件")
    print(f"\n📂 测试文件位置: {MUSIC_DIR}")
    print(f"💡 提示: 由于WebDAV问题，需要手动复制NCM文件到该目录")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎵 音乐格式转换项目测试脚本")
    print("="*60)
    print(f"目标: 在VNC图形桌面的浏览器中测试音乐格式转换")
    print(f"="*60)

    # 1. 检查VNC
    print(f"\n🖥️  检查VNC服务")
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )

        vnc_running = "Xtigervnc" in result.stdout or "Xvnc" in result.stdout
        if vnc_running:
            print(f"✅ VNC服务正在运行")
            print(f"   端口: 5901 (localhost)")
            print(f"   访问: http://服务器IP:6080/vnc.html")
        else:
            print(f"❌ VNC服务未运行")
            print(f"   启动命令: vncserver :1")
            return

    except Exception as e:
        print(f"❌ 检查VNC失败: {str(e)}")
        return

    # 2. 启动Chrome
    chrome_started = start_chrome_with_music_project()

    if not chrome_started:
        print(f"\n❌ 无法启动Chrome浏览器")
        print(f"💡 建议:")
        print(f"   1. 检查Chrome是否安装: which google-chrome")
        print(f"   2. 检查VNC是否运行: ps aux | grep vnc")
        print(f"   3. 检查显示环境: echo $DISPLAY")
        return

    # 3. 测试上传
    test_music_file_upload()

    # 4. 总结
    print(f"\n" + "="*60)
    print(f"📊 测试总结")
    print(f"="*60)
    print(f"✅ Chrome浏览器已启动")
    print(f"🌐 已访问音乐转换项目")
    print(f"📝 需要手动操作:")
    print(f"   1. 在VNC中查看浏览器窗口")
    print(f"   2. 上传NCM文件进行转换测试")
    print(f"   3. 验证转换是否成功")
    print(f"\n💡 如果转换失败，可能原因:")
    print(f"   - 项目代码有bug")
    print(f"   - 缺少必要的依赖库")
    print(f"   - 文件格式不支持")
    print(f"   - 浏览器兼容性问题")
    print(f"="*60 + "\n")


if __name__ == "__main__":
    main()
