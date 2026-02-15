import requests
import hashlib
import time
import json

BT_URL = "http://82.157.20.7:8888"
BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"

def get_token():
    now = int(time.time())
    token = hashlib.md5((str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()).encode()).hexdigest()
    return now, token

def get_dir(path):
    now, token = get_token()
    url = f"{BT_URL}/files?action=GetDir"
    data = {
        "request_time": now,
        "request_token": token,
        "path": path
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    files = get_dir("/www/wwwroot/ceshi.dhmip.cn")
    print(json.dumps(files, indent=2, ensure_ascii=False))
