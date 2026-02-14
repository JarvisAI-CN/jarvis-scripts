#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM音乐文件下载和转换测试

目标：
1. 从123盘WebDAV下载NCM文件
2. 测试NCM格式转换功能
3. 验证转换是否正常工作
"""

import os
import sys
import requests
from pathlib import Path
from urllib.parse import quote

# 配置
WEBDAV_BASE = "https://webdav.123pan.cn/webdav"
SHARED_RESOURCE = "/共享资源"
LOCAL_DIR = Path("/home/ubuntu/music_test")
LOCAL_DIR.mkdir(parents=True, exist_ok=True)


def download_from_webdav(remote_path: str, local_path: Path) -> bool:
    """从WebDAV下载文件"""
    try:
        # URL编码路径
        encoded_path = quote(remote_path)

        # WebDAV URL
        url = f"{WEBDAV_BASE}{encoded_path}"

        print(f"📥 下载文件: {remote_path}")
        print(f"🔗 URL: {url}")

        # 读取密码
        with open('/home/ubuntu/.openclaw/workspace/PASSWORDS.md', 'r') as f:
            content = f.read()
            # 提取WebDAV密码（简化）
            import re
            match = re.search(r'123盘.*?password[:\s]*([^\n]+)', content, re.IGNORECASE)
            if match:
                password = match.group(1).strip()
            else:
                password = "fs123456"  # 默认密码

        # 下载文件
        response = requests.get(
            url,
            auth=requests.auth.HTTPBasicAuth("u8967344", password),
            stream=True,
            timeout=60
        )

        if response.status_code == 200:
            # 写入文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = local_path.stat().st_size / (1024 * 1024)
            print(f"✅ 下载成功: {local_path.name} ({file_size:.2f} MB)")
            return True
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 下载异常: {str(e)}")
        return False


def list_ncm_files() -> list:
    """列出123盘共享资源中的NCM文件"""
    try:
        import requests
        from lxml import etree

        url = f"{WEBDAV_BASE}{SHARED_RESOURCE}/"

        with open('/home/ubuntu/.openclaw/workspace/PASSWORDS.md', 'r') as f:
            content = f.read()
            import re
            match = re.search(r'123盘.*?password[:\s]*([^\n]+)', content, re.IGNORECASE)
            if match:
                password = match.group(1).strip()
            else:
                password = "fs123456"

        # PROPFIND请求
        response = requests.request(
            "PROPFIND",
            url,
            auth=requests.auth.HTTPBasicAuth("u8967344", password),
            headers={"Depth": "1"}
        )

        if response.status_code == 207:
            # 解析XML
            root = etree.fromstring(response.content)

            ncm_files = []
            for elem in root.iter():
                href = elem.find("{DAV:}href")
                if href is not None and href.text:
                    filename = href.text.split("/")[-1]
                    if filename.endswith(".ncm"):
                        ncm_files.append(filename)

            return ncm_files
        else:
            print(f"❌ 列出文件失败: HTTP {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ 列出文件异常: {str(e)}")
        return []


def test_ncm_conversion(ncm_file: Path) -> dict:
    """测试NCM转换功能"""
    result = {
        "file": str(ncm_file),
        "success": False,
        "error": None,
        "output_file": None
    }

    print(f"\n🧪 测试NCM转换: {ncm_file.name}")

    try:
        # 方法1: 尝试使用ncm-dump（如果安装了）
        try:
            import subprocess
            output_file = ncm_file.with_suffix('.mp3')

            cmd = [
                "ncm-dump",
                "-i", str(ncm_file),
                "-o", str(output_file)
            ]

            result_run = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result_run.returncode == 0:
                result["success"] = True
                result["output_file"] = str(output_file)
                print(f"✅ ncm-dump转换成功")
                return result
            else:
                print(f"⚠️  ncm-dump不可用或失败: {result_run.stderr}")

        except FileNotFoundError:
            print(f"⚠️  ncm-dump未安装")
        except subprocess.TimeoutExpired:
            print(f"❌ ncm-dump转换超时")

        # 方法2: 尝试使用unlock-music（Python库）
        try:
            from Crypto.Cipher import AES
            print(f"✅ 找到pycryptodome库，尝试解密")

            # 这里需要具体的NCM解密逻辑
            # NCM格式比较复杂，需要专门的库
            print(f"⚠️  NCM解密需要专门的库（如ncm-dump）")

        except ImportError:
            print(f"⚠️  pycryptodome未安装")

        # 方法3: 检查是否有转换项目
        conversion_projects = [
            "/home/ubuntu/.openclaw/workspace/PARA/Projects/NCM-Converter",
            "/home/ubuntu/.openclaw/workspace/ncm-converter",
            "/home/ubuntu/ncm-converter"
        ]

        for project_path in conversion_projects:
            if Path(project_path).exists():
                print(f"✅ 找到转换项目: {project_path}")
                # 可以调用项目中的转换脚本
                result["project_found"] = project_path

        result["error"] = "没有找到可用的NCM转换工具"
        print(f"❌ {result['error']}")
        print(f"\n💡 建议:")
        print(f"   1. 安装ncm-dump: pip3 install ncm-dump")
        print(f"   2. 或使用在线工具: https://ncm.kwasu.cc/")
        print(f"   3. 或使用项目: https://github.com/5han/covertMusic")

    except Exception as e:
        result["error"] = str(e)
        print(f"❌ 转换异常: {str(e)}")

    return result


def main():
    """主函数"""
    print("="*60)
    print("🎵 NCM音乐文件下载和转换测试")
    print("="*60)

    # 1. 列出NCM文件
    print("\n📋 步骤1: 列出123盘共享资源中的NCM文件")
    ncm_files = list_ncm_files()

    if not ncm_files:
        print("⚠️  未找到NCM文件，使用已知文件测试")
        ncm_files = ["梓渝 - 萤火星球.ncm"]

    print(f"✅ 找到 {len(ncm_files)} 个NCM文件")

    # 2. 下载文件
    print(f"\n📥 步骤2: 下载NCM文件到本地")
    downloaded_files = []

    for ncm_file in ncm_files:
        remote_path = f"{SHARED_RESOURCE}/{ncm_file}"
        local_path = LOCAL_DIR / ncm_file

        if local_path.exists():
            print(f"⏭️  文件已存在: {local_path.name}")
            downloaded_files.append(local_path)
        else:
            success = download_from_webdav(remote_path, local_path)
            if success:
                downloaded_files.append(local_path)

    if not downloaded_files:
        print("❌ 没有下载到任何文件")
        return

    # 3. 测试转换
    print(f"\n🧪 步骤3: 测试NCM格式转换")
    results = []

    for ncm_file in downloaded_files:
        result = test_ncm_conversion(ncm_file)
        results.append(result)

    # 4. 总结报告
    print(f"\n" + "="*60)
    print(f"📊 测试总结报告")
    print(f"="*60)

    success_count = sum(1 for r in results if r["success"])
    print(f"✅ 成功转换: {success_count}/{len(results)}")
    print(f"❌ 转换失败: {len(results) - success_count}/{len(results)}")

    for i, result in enumerate(results, 1):
        status = "✅" if result["success"] else "❌"
        print(f"\n{status} 文件{i}: {Path(result['file']).name}")
        if result["success"]:
            print(f"   输出: {Path(result['output_file']).name}")
        else:
            print(f"   错误: {result['error']}")

    print(f"\n" + "="*60)

    # 5. 建议
    if success_count == 0:
        print(f"\n💡 解决方案:")
        print(f"   1. 安装NCM转换工具:")
        print(f"      pip3 install ncm-dump")
        print(f"      pip3 install pycryptodome")
        print(f"\n   2. 或使用在线转换工具:")
        print(f"      https://ncm.kwasu.cc/")
        print(f"      https://tools.liumingye.cn/music/")
        print(f"\n   3. 或在浏览器中测试音乐转换项目:")

    print(f"\n📂 下载的文件位置: {LOCAL_DIR}")
    print(f"="*60 + "\n")


if __name__ == "__main__":
    main()
