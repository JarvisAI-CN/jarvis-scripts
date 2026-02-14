import requests
import hashlib
import time

BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

def get_token():
    now = int(time.time())
    token = hashlib.md5((str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()).encode()).hexdigest()
    return now, token

def read_file(path):
    now, token = get_token()
    url = f"{BT_URL}/files?action=GetFileBody"
    data = {
        "request_time": now,
        "request_token": token,
        "path": path
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    content = read_file("/www/wwwroot/yinyue.dhmip.cn/scripts/ncm_converter.py")
    print(content.get('data'))
