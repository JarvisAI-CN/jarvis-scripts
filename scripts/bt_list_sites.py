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

def list_sites():
    now, token = get_token()
    url = f"{BT_URL}/site?action=GetSiteList"
    data = {
        "request_time": now,
        "request_token": token,
        "p": 1,
        "limit": 50
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    sites = list_sites()
    print(json.dumps(sites, indent=2, ensure_ascii=False))
