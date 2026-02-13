#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

WP_URL = "https://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

session = requests.Session()

def test_login():
    login_url = f"{WP_URL}/wp-login.php"
    r = session.get(login_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    hidden = {it['name']: it.get('value', '') for it in soup.find_all('input', type='hidden') if it.get('name')}
    data = {'log': WP_ADMIN, 'pwd': WP_PASSWORD, 'wp-submit': '登录', 'testcookie': '1', **hidden}
    r = session.post(login_url, data=data)
    print(f"Status: {r.status_code}")
    print(f"Final URL: {r.url}")
    if "wp-admin" in r.url:
        print("✅ Login Success")
    else:
        print("❌ Login Failed")

if __name__ == "__main__":
    test_login()
