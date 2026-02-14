#!/usr/bin/env python3
"""直接测试Flask应用的/convert路由"""
import requests

try:
    # 直接访问Flask应用
    response = requests.post("http://127.0.0.1:5001/convert", timeout=10)
    print(f"直接访问Flask: {response.status_code}")
    if response.status_code == 400:
        print("✅ Flask应用的/convert路由存在")
        print("→ 问题可能在Nginx配置")
    else:
        print(f"响应: {response.text[:100]}")
except Exception as e:
    print(f"❌ 错误: {e}")
