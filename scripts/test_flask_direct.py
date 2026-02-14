#!/usr/bin/env python3
import requests
import time

# 直接访问Flask应用
FLASK_URL = "http://127.0.0.1:5001"
TEST_FILE = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

def test_conversion():
    """测试完整转换流程"""
    print(f"🧪 测试文件：{os.path.basename(TEST_FILE)}")
    
    # 1. 上传
    print("\n📤 步骤1：上传文件...")
    upload_url = f"{FLASK_URL}/convert"
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (os.path.basename(TEST_FILE), f)}
        
        try:
            response = requests.post(upload_url, files=files, timeout=60)
            print(f"   状态码：{response.status_code}")
            print(f"   响应内容：{response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if data.get('success') and data.get('id'):
                        file_id = data.get('id')
                        print(f"   ✅ 上传成功，文件ID：{file_id}")
                        
                        # 下载链接格式：/download/<id>
                        download_url = f"{FLASK_URL}/download/{file_id}"
                        
                        print(f"\n📥 步骤2：下载文件...")
                        print(f"   下载链接：{download_url}")
                        
                        # 尝试下载
                        dl_response = requests.get(download_url, timeout=30)
                        print(f"   状态码：{dl_response.status_code}")
                        print(f"   Content-Type：{dl_response.headers.get('Content-Type')}")
                        print(f"   Content-Length：{dl_response.headers.get('Content-Length')}")
                        
                        if dl_response.status_code == 200:
                            content = dl_response.content
                            file_size = len(content)
                            file_size_mb = file_size / 1024 / 1024
                            
                            print(f"   实际下载大小：{file_size:,} 字节 ({file_size_mb:.2f} MB)")
                            
                            # 检查文件头
                            if content[:4] == b'fLaC':
                                print("   ✅ 文件格式正确（FLAC）")
                            else:
                                print(f"   ❌ 文件格式错误：{content[:20].hex()}")
                            
                            if file_size > 1_000_000:  # > 1MB
                                print("   ✅✅✅ 下载成功！文件大小正常！")
                                return True
                            else:
                                print(f"   ❌ 文件太小：只收到{file_size}字节")
                                return False
                        else:
                            print(f"   ❌ 下载失败：HTTP {dl_response.status_code}")
                            print(f"   响应内容：{dl_response.text[:200]}")
                            return False
                    else:
                        error = data.get('error', 'Unknown error')
                        print(f"   ❌ 转换失败：{error}")
                        return False
                except Exception as e:
                    print(f"   ❌ 响应解析失败：{e}")
                    return False
            else:
                print(f"   ❌ 上传失败：HTTP {response.status_code}")
                print(f"   响应内容：{response.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ 上传异常：{e}")
            return False

if __name__ == "__main__":
    import os
    success = test_conversion()
    if success:
        print("\n" + "="*60)
        print("✅✅✅ 测试成功！文件转换和下载都正常工作")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌❌❌ 测试失败")
        print("="*60)
