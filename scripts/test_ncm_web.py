#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM转换器Web应用测试脚本
"""

import requests
import os

BASE_URL = "http://localhost:5000"

def test_webpage():
    """测试Web页面"""
    print("="*60)
    print("🌐 测试Web页面")
    print("="*60)
    
    try:
        response = requests.get(BASE_URL)
        
        if response.status_code == 200:
            print("✅ Web页面访问成功")
            print(f"状态码: {response.status_code}")
            print(f"内容长度: {len(response.text)} bytes")
            
            if "NCM转FLAC转换器" in response.text:
                print("✅ 页面标题正确")
            else:
                print("⚠️  页面标题异常")
                
            return True
        else:
            print(f"❌ Web页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")
        return False

def test_conversion():
    """测试NCM转换功能"""
    print("\n" + "="*60)
    print("🎵 测试NCM转换功能")
    print("="*60)
    
    ncm_file = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"
    
    if not os.path.exists(ncm_file):
        print(f"❌ 测试文件不存在: {ncm_file}")
        return False
    
    file_size = os.path.getsize(ncm_file) / (1024 * 1024)
    print(f"📂 测试文件: {os.path.basename(ncm_file)}")
    print(f"📊 文件大小: {file_size:.2f} MB")
    
    try:
        # 上传文件
        print("\n📤 上传文件...")
        with open(ncm_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/convert", files=files, timeout=300)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ 转换成功")
                print(f"输出文件: {data.get('filename')}")
                print(f"文件大小: {data.get('size') / (1024*1024):.2f} MB")
                print(f"格式: {data.get('format')}")
                print(f"文件ID: {data.get('id')}")
                
                # 测试下载
                file_id = data.get('id')
                download_url = f"{BASE_URL}/download/{file_id}"
                
                print(f"\n📥 测试下载: {download_url}")
                download_response = requests.get(download_url, stream=True)
                
                if download_response.status_code == 200:
                    downloaded_size = int(download_response.headers.get('content-length', 0)) / (1024*1024)
                    print(f"✅ 下载成功: {downloaded_size:.2f} MB")
                    return True
                else:
                    print(f"❌ 下载失败: {download_response.status_code}")
                    return False
            else:
                print(f"❌ 转换失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 转换请求失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（5分钟）")
        return False
    except Exception as e:
        print(f"❌ 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*60)
    print("🧪 NCM转换器Web应用测试")
    print("="*60)
    print(f"测试地址: {BASE_URL}")
    print("")
    
    # 测试Web页面
    web_ok = test_webpage()
    
    # 测试转换功能
    convert_ok = test_conversion()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"Web页面: {'✅ 通过' if web_ok else '❌ 失败'}")
    print(f"转换功能: {'✅ 通过' if convert_ok else '❌ 失败'}")
    print("")
    
    if web_ok and convert_ok:
        print("✅ 所有测试通过！")
        print("\n🚀 部署到宝塔面板:")
        print("1. 登录宝塔: http://82.157.20.7:8888/fs123456")
        print("2. 创建网站: ncm.dhmip.cn")
        print("3. 设置反向代理 -> http://127.0.0.1:5000")
        print("4. 启用SSL证书")
    else:
        print("❌ 部分测试失败，请检查日志")
    
    print("="*60)

if __name__ == "__main__":
    main()
