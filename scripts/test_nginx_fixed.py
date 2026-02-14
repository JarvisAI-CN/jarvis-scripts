#!/usr/bin/env python3
"""快速测试修复后的域名访问"""
import requests

BASE_URL = "http://yinyue.dhmip.cn"

print("测试 1: 首页访问")
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"  状态码: {response.status_code}")
    if response.status_code == 200:
        print("  ✅ 首页正常")
except Exception as e:
    print(f"  ❌ 错误: {e}")

print("\n测试 2: POST /convert (模拟文件上传，但实际不传)")
try:
    # 不上传文件，只测试路由是否存在
    response = requests.post(f"{BASE_URL}/convert", timeout=10)
    print(f"  状态码: {response.status_code}")
    if response.status_code == 400:
        print("  ✅ 路由存在（返回400因为缺少文件）")
        print("  → Nginx代理正常工作")
    elif response.status_code == 404:
        print("  ❌ 路由不存在（404）")
        print("  → Nginx代理可能有问题")
except Exception as e:
    print(f"  ❌ 错误: {e}")

print("\n测试完成")
