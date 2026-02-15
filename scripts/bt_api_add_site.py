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

def add_site(domain, path):
    now, token = get_token()
    url = f"{BT_URL}/site?action=AddSite"
    # Baota AddSite requires webname, path, type, version, port
    data = {
        "request_time": now,
        "request_token": token,
        "webname": json.dumps({"domain": domain, "domainlist": [], "count": 0}),
        "path": path,
        "type": "PHP",
        "version": "82", # PHP 8.2
        "port": "80",
        "ps": "Expiry System",
        "ftp": "false",
        "sql": "true", # Create DB too?
        "dataBaseName": "expiry_system",
        "dataBaseUser": "expiry_user",
        "dataBasePass": "Expiry@2026"
    }
    r = requests.post(url, data=data)
    return r.json()

if __name__ == "__main__":
    result = add_site("ceshi.dhmip.cn", "/www/wwwroot/ceshi.dhmip.cn")
    print(json.dumps(result, indent=2, ensure_ascii=False))
