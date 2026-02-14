import requests
import time

url_upload = "http://yinyue.dhmip.cn/upload.php"
url_base = "http://yinyue.dhmip.cn/"
file_path = "/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"

session = requests.Session()

print("Uploading...")
with open(file_path, 'rb') as f:
    r = session.post(url_upload, files={'ncm_file': f}, headers={'Accept': 'application/json'})

print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {data}")

if data.get('success'):
    download_url = url_base + data['downloadUrl']
    print(f"Downloading from {download_url}...")
    
    r_dl = session.get(download_url, stream=True)
    print(f"Download Status: {r_dl.status_code}")
    print(f"Download Headers: {r_dl.headers}")
    
    content = r_dl.raw.read(100)
    print(f"First 100 bytes (hex): {content.hex()}")
    print(f"First 100 bytes (text): {content}")
