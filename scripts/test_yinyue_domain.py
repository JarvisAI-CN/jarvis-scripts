#!/usr/bin/env python3
"""
测试通过 yinyue.dhmip.cn 的 NCM 转换功能
"""
import requests
import time

BASE_URL = "http://yinyue.dhmip.cn"
TEST_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

print(f"测试 1: 访问首页")
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)} 字符")
    if response.status_code == 200:
        print("✅ 首页访问成功")
    else:
        print(f"❌ 首页访问失败: {response.status_code}")
except Exception as e:
    print(f"❌ 首页访问错误: {e}")

print(f"\n测试 2: 上传并转换 NCM 文件")
try:
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/convert",
            files=files,
            timeout=30
        )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 转换成功")
        print(f"  FLAC文件名: {data.get('filename', 'N/A')}")
        print(f"  文件大小: {data.get('size', 'N/A')} 字节")
        
        # 检查文件大小是否正常（应该 > 10MB）
        size = int(data.get('size', 0))
        if size > 10 * 1024 * 1024:
            print(f"  ✅ 文件大小正常 ({size / 1024 / 1024:.2f} MB)")
        else:
            print(f"  ❌ 文件大小异常 ({size} 字节)")
    else:
        print(f"❌ 转换失败: {response.status_code}")
        print(f"响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 转换错误: {e}")

print("\n测试完成。")
