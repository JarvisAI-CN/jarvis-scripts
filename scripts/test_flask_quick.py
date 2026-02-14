#!/usr/bin/env python3
"""快速测试Flask应用"""
import requests

try:
    response = requests.get("http://127.0.0.1:5001/", timeout=5)
    print(f"状态码: {response.status_code}")
    print(f"响应长度: {len(response.text)}")
    if "NCM" in response.text:
        print("✅ Flask应用正常")
    else:
        print("❌ 响应内容异常")
        print(response.text[:200])
except Exception as e:
    print(f"❌ 错误: {e}")
