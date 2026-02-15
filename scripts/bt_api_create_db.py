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

def create_database(db_name, username, password):
    now, token = get_token()
    url = f"{BT_URL}/database?action=AddDatabase"
    data = {
        "request_time": now,
        "request_token": token,
        "name": db_name,
        "db_user": username,
        "password": password,
        "address": "127.0.0.1",
        "ps": "Expiry System Database"
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    # Using specific credentials for the app
    result = create_database("expiry_system", "expiry_user", "Expiry@2026")
    print(json.dumps(result, indent=2, ensure_ascii=False))
