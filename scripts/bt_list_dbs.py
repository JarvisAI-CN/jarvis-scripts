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

def get_db_list():
    now, token = get_token()
    url = f"{BT_URL}/database?action=GetDatabaseList"
    data = {
        "request_time": now,
        "request_token": token,
        "p": 1,
        "limit": 100
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    dbs = get_db_list()
    print(json.dumps(dbs, indent=2, ensure_ascii=False))
