#!/usr/bin/env python3
"""发布播客文章 - 简化版本"""
import requests
import subprocess
import json

# 直接调用之前创建的发布脚本
result = subprocess.run(
    ['python3', '/home/ubuntu/.openclaw/workspace/publish_podcast_post.py'],
    capture_output=True,
    text=True
)

print("STDOUT:")
print(result.stdout)
print("\nSTDERR:")
print(result.stderr)
print(f"\n返回码: {result.returncode}")
