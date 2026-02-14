#!/usr/bin/env python3
"""测试简化后的Nginx配置"""
import requests

BASE_URL = "http://yinyue.dhmip.cn"

print("测试 1: GET 首页")
try:
    response = requests.get(f"{BASE_URL}/", timeout=10)
    print(f"  状态码: {response.status_code}")
except Exception as e:
    print(f"  错误: {e}")

print("\n测试 2: POST /convert（无文件）")
try:
    response = requests.post(f"{BASE_URL}/convert", timeout=10)
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.text[:100]}")
except Exception as e:
    print(f"  错误: {e}")

print("\n测试 3: 直接Flask POST")
try:
    response = requests.post("http://127.0.0.1:5001/convert", timeout=10)
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.text[:100]}")
except Exception as e:
    print(f"  错误: {e}")
