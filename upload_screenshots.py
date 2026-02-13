import os
import requests
import datetime
import glob

# 配置
LOCAL_SCREENSHOT_DIR = "/home/ubuntu/.openclaw/media/browser/"
REMOTE_WEBDAV_URL = "https://webdav.123pan.cn/webdav/截图日志/"
WEBDAV_USER = "13220103449"
WEBDAV_PASS = "ls8h74pb"

def upload_screenshots():
    # 获取所有图片文件
    files = glob.glob(os.path.join(LOCAL_SCREENSHOT_DIR, "*.jpg")) + glob.glob(os.path.join(LOCAL_SCREENSHOT_DIR, "*.png"))
    
    if not files:
        print("没有发现需要上传的截图。")
        return

    for local_path in files:
        filename = os.path.basename(local_path)
        remote_path = f"{REMOTE_WEBDAV_URL}{filename}"
        
        print(f"正在上传 {filename} 到 123 盘...")
        
        try:
            with open(local_path, 'rb') as f:
                response = requests.put(
                    remote_path,
                    data=f,
                    auth=(WEBDAV_USER, WEBDAV_PASS),
                    timeout=30
                )
            
            if response.status_code in [200, 201, 204]:
                print(f"✅ 上传成功: {filename}")
                # 上传成功后可以考虑删除本地文件，或者保留
            else:
                print(f"❌ 上传失败: {filename} (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"❌ 上传异常 {filename}: {e}")

if __name__ == "__main__":
    upload_screenshots()
