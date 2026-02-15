import time
import hashlib
import json
import requests

BT_KEY = "N1WSP3iddQideRInbq515yXC8lOAfCDn"
BT_URL = "http://82.157.20.7:8888"

def get_token():
    now = int(time.time())
    token = hashlib.md5((str(now) + hashlib.md5(BT_KEY.encode()).hexdigest()).encode()).hexdigest()
    return now, token

def test_api():
    now, token = get_token()
    url = f"{BT_URL}/data?action=getDataCount"
    data = {
        "request_time": now,
        "request_token": token
    }
    r = requests.post(url, data=data)
    print(r.text)

if __name__ == "__main__":
    test_api()
