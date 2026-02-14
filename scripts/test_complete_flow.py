#!/usr/bin/env python3
"""
测试完整的上传-转换-下载流程
"""
import requests
import time
import os

BASE_URL_LOCAL = "http://127.0.0.1:5001"
BASE_URL_DOMAIN = "http://yinyue.dhmip.cn"
TEST_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

def test_flask(base_url, name):
    print(f"\n{'='*60}")
    print(f"测试: {name} ({base_url})")
    print(f"{'='*60}")
    
    print(f"\n步骤 1: 上传并转换 NCM 文件")
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {'file': f}
            print("  正在上传...")
            response = requests.post(
                f"{base_url}/convert",
                files=files,
                timeout=60
            )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            file_id = data.get('id')
            
            if file_id:
                print(f"  ✅ 上传成功，file_id: {file_id}")
                
                # 步骤 2: 下载 FLAC 文件
                print(f"\n步骤 2: 下载 FLAC 文件")
                download_response = requests.get(
                    f"{base_url}/download/{file_id}",
                    timeout=60
                )
                
                print(f"  状态码: {download_response.status_code}")
                
                if download_response.status_code == 200:
                    flac_data = download_response.content
                    size = len(flac_data)
                    
                    print(f"  ✅ 下载成功")
                    print(f"  文件大小: {size} 字节 ({size / 1024 / 1024:.2f} MB)")
                    
                    if size > 10 * 1024 * 1024:
                        print(f"  ✅ 文件大小正常（完整的 FLAC 文件）")
                        return True
                    else:
                        print(f"  ❌ 文件大小异常（可能不完整）")
                        return False
                else:
                    print(f"  ❌ 下载失败: {download_response.status_code}")
                    print(f"  响应: {download_response.text[:200]}")
                    return False
            else:
                print(f"  ❌ 转换失败: {data}")
                return False
        else:
            print(f"  ❌ 上传失败: {response.status_code}")
            print(f"  响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

# 测试本地 Flask 应用
local_success = test_flask(BASE_URL_LOCAL, "本地 Flask 应用")

# 测试通过域名访问
domain_success = test_flask(BASE_URL_DOMAIN, "域名 yinyue.dhmip.cn")

# 结论
print(f"\n{'='*60}")
print("测试结论")
print(f"{'='*60}")
print(f"本地 Flask 应用: {'✅ 成功' if local_success else '❌ 失败'}")
print(f"域名访问: {'✅ 成功' if domain_success else '❌ 失败'}")

if local_success and not domain_success:
    print("\n🔍 诊断: 问题出在反向代理配置上")
    print("   建议: 检查 Nginx 反向代理的超时、缓冲、缓存设置")
elif not local_success and not domain_success:
    print("\n🔍 诊断: 问题出在 Flask 应用上")
    print("   建议: 检查 Flask 应用的转换逻辑")
elif local_success and domain_success:
    print("\n🎉 成功: 本地和域名访问都正常工作！")
