#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试NCM文件格式
"""

import sys

ncm_file = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

with open(ncm_file, 'rb') as f:
    header = f.read(20)

print(f"文件头（十六进制）: {header.hex()}")
print(f"文件头（ASCII）: {header[:10]}")
print(f"魔术字: {header[:4]}")

# 检查是否是NCM
if header[:4] == b'CTCN':
    print("✅ 这是NCM文件（CTCN格式）")
elif header[:4] == b'CTEN':
    print("✅ 这是NCM文件（CTEN格式）")
else:
    print("❌ 这不是NCM文件")
    print(f"未知格式: {header[:4]}")

# 文件大小
import os
file_size = os.path.getsize(ncm_file)
print(f"文件大小: {file_size / (1024*1024):.2f} MB")
