#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM自动化测试脚本
尝试多种方法测试NCM格式转换
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

NCM_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"
OUTPUT_DIR = "/home/ubuntu/music_test/converted"

def method_1_check_format():
    """方法1: 检查NCM文件格式"""
    print("\n" + "="*60)
    print("📋 方法1: 检查NCM文件格式")
    print("="*60)
    
    with open(NCM_FILE, 'rb') as f:
        header = f.read(20)
    
    magic = header[:4]
    print(f"魔术字: {magic}")
    print(f"十六进制: {header.hex()[:20]}")
    
    if magic == b'CTCN':
        print("✅ 格式: CTCN (老格式)")
        return 'ctcn'
    elif magic == b'CTEN':
        print("✅ 格式: CTEN (新格式)")
        return 'cten'
    else:
        print(f"❌ 未知格式: {magic}")
        return None

def method_2_pipx_install():
    """方法2: 使用pipx安装工具"""
    print("\n" + "="*60)
    print("📦 方法2: 尝试使用pipx安装nc-dump")
    print("="*60)
    
    try:
        # 检查pipx
        result = subprocess.run(
            ["which", "pipx"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ pipx未安装")
            return False
        
        print("✅ pipx已安装")
        
        # 尝试安装
        print("📥 正在安装nc-dump...")
        result = subprocess.run(
            ["pipx", "install", "ncm-dump"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("✅ nc-dump安装成功")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def method_3_try_ncmdump():
    """方法3: 尝试安装并使用ncmdump"""
    print("\n" + "="*60)
    print("📦 方法3: 尝试安装ncmdump")
    print("="*60)
    
    try:
        # 创建虚拟环境
        venv_dir = "/tmp/ncm_venv"
        print(f"📁 创建虚拟环境: {venv_dir}")
        
        subprocess.run(
            ["python3", "-m", "venv", venv_dir],
            check=True,
            capture_output=True
        )
        
        # 安装pycryptodome
        pip_path = f"{venv_dir}/bin/pip3"
        print("📥 安装pycryptodome...")
        
        subprocess.run(
            [pip_path, "install", "pycryptodome"],
            check=True,
            capture_output=True
        )
        print("✅ pycryptodome安装成功")
        
        # 安装ncmdump
        print("📥 安装ncmdump...")
        
        result = subprocess.run(
            [pip_path, "install", "ncmdump"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"❌ ncmdump安装失败: {result.stderr}")
            return False
        
        print("✅ ncmdump安装成功")
        
        # 使用ncmdump转换
        ncmdump_path = f"{venv_dir}/bin/ncmdump"
        output_file = f"{OUTPUT_DIR}/梓渝 - 萤火星球.ncm"
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        print(f"\n🔄 开始转换...")
        print(f"输入: {NCM_FILE}")
        print(f"输出: {output_file}")
        
        result = subprocess.run(
            [ncmdump_path, "-i", NCM_FILE, "-o", output_file],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ ncmdump转换成功！")
            
            # 检查输出文件
            if os.path.exists(output_file):
                size = os.path.getsize(output_file) / (1024 * 1024)
                print(f"📊 输出文件大小: {size:.2f} MB")
                
                # 检查格式
                with open(output_file, 'rb') as f:
                    header = f.read(4)
                
                if header == b'fLaC':
                    print("✅ 格式: FLAC")
                elif header[:3] == b'ID3' or header[:2] == b'\xff\xfb':
                    print("✅ 格式: MP3")
                else:
                    print(f"⚠️  未知格式: {header}")
                
                return True
            else:
                print("❌ 输出文件不存在")
                return False
        else:
            print(f"❌ ncmdump转换失败")
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def method_4_online_api():
    """方法4: 尝试使用在线API"""
    print("\n" + "="*60)
    print("🌐 方法4: 尝试在线转换API")
    print("="*60)
    
    print("⚠️  大多数在线网站不提供公开API")
    print("💡 需要浏览器自动化（Selenium）")
    
    return False

def method_5_decrypt_direct():
    """方法5: 直接尝试解密（测试目的）"""
    print("\n" + "="*60)
    print("🔓 方法5: 直接解密测试（仅用于验证）")
    print("="*60)
    
    try:
        with open(NCM_FILE, 'rb') as f:
            data = f.read()
        
        print(f"📊 文件大小: {len(data) / (1024*1024):.2f} MB")
        print(f"魔术字: {data[:4]}")
        
        if data[:4] == b'CTEN':
            print("✅ CTEN格式确认")
            
            # 尝试读取密钥长度
            if len(data) >= 20:
                offset = 10
                key_len = int.from_bytes(data[offset:offset+4], 'little')
                print(f"密钥长度: {key_len} bytes")
                
                offset += 4
                key_data = data[offset:offset+key_len]
                print(f"加密密钥数据: {key_len} bytes")
                
                offset += key_len
                
                if len(data) >= offset + 4:
                    meta_len = int.from_bytes(data[offset:offset+4], 'little')
                    print(f"元数据长度: {meta_len} bytes")
                    
                    if meta_len > 0 and meta_len < 10000:
                        print("✅ 文件结构看起来有效")
                        print("💡 需要正确的解密密钥才能解密")
                    else:
                        print("⚠️  元数据长度异常")
                        return False
                
                return True
        else:
            print("❌ 不支持的格式")
            return False
            
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        return False

def main():
    print("="*60)
    print("🎵 NCM格式转换自动化测试")
    print("="*60)
    print(f"测试文件: {NCM_FILE}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("="*60)
    
    # 检查文件
    if not os.path.exists(NCM_FILE):
        print(f"\n❌ 文件不存在: {NCM_FILE}")
        return
    
    # 执行各种测试方法
    results = {}
    
    # 方法1: 检查格式
    results['format'] = method_1_check_format()
    
    # 方法2: pipx安装
    results['pipx'] = method_2_pipx_install()
    
    # 方法3: ncmdump
    if results['format'] == 'cten':
        results['ncmdump'] = method_3_try_ncmdump()
    else:
        print("\n⏭️  跳过ncmdump测试（格式不支持）")
    
    # 方法4: 在线API
    results['online_api'] = method_4_online_api()
    
    # 方法5: 直接解密
    results['decrypt'] = method_5_decrypt_direct()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    for method, result in results.items():
        if result:
            print(f"✅ {method}: 成功")
        else:
            print(f"❌ {method}: 失败")
    
    print("\n" + "="*60)
    print("💡 结论:")
    print("="*60)
    
    if results.get('ncmdump'):
        print("✅ ncmdump工具可用，转换成功")
        print(f"📂 转换后的文件在: {OUTPUT_DIR}")
    else:
        print("❌ 所有自动化方法都失败")
        print("\n建议:")
        print("1. 在VNC中手动使用在线工具: https://ncm.kwasu.cc/")
        print("2. 检查NCM文件是否损坏")
        print("3. 尝试其他NCM文件")
        print("4. 联系NCM转换项目维护者")

if __name__ == "__main__":
    main()
