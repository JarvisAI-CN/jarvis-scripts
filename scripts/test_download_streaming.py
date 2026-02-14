#!/usr/bin/env python3
"""
测试完整的上传-转换-下载流程（更长超时）
"""
import requests
import time
import os

BASE_URL_LOCAL = "http://127.0.0.1:5001"
BASE_URL_DOMAIN = "http://yinyue.dhmip.cn"
TEST_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

def test_flask(base_url, name, timeout=300):
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
                print(f"\n步骤 2: 下载 FLAC 文件（超时 {timeout} 秒）")
                download_response = requests.get(
                    f"{base_url}/download/{file_id}",
                    timeout=timeout,
                    stream=True  # 流式下载
                )
                
                print(f"  状态码: {download_response.status_code}")
                
                if download_response.status_code == 200:
                    # 流式下载，避免内存问题
                    total_size = 0
                    start_time = time.time()
                    
                    with open(f'/tmp/test_download_{file_id[:8]}.flac', 'wb') as f:
                        for chunk in download_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                total_size += len(chunk)
                                
                                # 每下载 10 MB 打印一次进度
                                if total_size % (10 * 1024 * 1024) < 8192:
                                    elapsed = time.time() - start_time
                                    speed = total_size / elapsed / 1024 / 1024
                                    print(f"    已下载: {total_size / 1024 / 1024:.1f} MB ({speed:.1f} MB/s)")
                    
                    elapsed = time.time() - start_time
                    speed = total_size / elapsed / 1024 / 1024
                    
                    print(f"  ✅ 下载成功")
                    print(f"  文件大小: {total_size} 字节 ({total_size / 1024 / 1024:.2f} MB)")
                    print(f"  下载时间: {elapsed:.1f} 秒")
                    print(f"  平均速度: {speed:.2f} MB/s")
                    
                    if total_size > 10 * 1024 * 1024:
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
            
    except requests.exceptions.Timeout:
        print(f"  ❌ 超时错误（>{timeout} 秒）")
        return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

# 测试本地 Flask 应用（5 分钟超时）
local_success = test_flask(BASE_URL_LOCAL, "本地 Flask 应用", timeout=300)

# 测试通过域名访问（5 分钟超时）
domain_success = test_flask(BASE_URL_DOMAIN, "域名 yinyue.dhmip.cn", timeout=300)

# 结论
print(f"\n{'='*60}")
print("测试结论")
print(f"{'='*60}")
print(f"本地 Flask 应用: {'✅ 成功' if local_success else '❌ 失败'}")
print(f"域名访问: {'✅ 成功' if domain_success else '❌ 失败'}")

if local_success and not domain_success:
    print("\n🔍 诊断: 问题出在 Nginx 反向代理配置上")
    print("   建议: 检查 Nginx 的超时、缓冲、缓存设置")
elif not local_success and not domain_success:
    print("\n🔍 诊断: 问题出在 Flask 应用上")
    print("   建议: 检查 Flask 应用的下载逻辑（send_from_directory 性能）")
elif local_success and domain_success:
    print("\n🎉 成功: 本地和域名访问都正常工作！")
