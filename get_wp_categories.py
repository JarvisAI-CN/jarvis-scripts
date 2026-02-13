#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

WP_URL = "http://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

session = requests.Session()

def get_categories():
    login_url = f"{WP_URL}/wp-login.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    session.get(login_url)
    login_data = {'log': WP_ADMIN, 'pwd': WP_PASSWORD, 'wp-submit': '登录'}
    session.post(login_url, data=login_data)
    
    # sites 类型的分类通常在 edit-tags.php?taxonomy=favorites
    cat_url = f"{WP_URL}/wp-admin/edit-tags.php?taxonomy=favorites"
    response = session.get(cat_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("📁 找到的分类列表:")
    # OneNav 或者是普通的 WordPress 分类表
    rows = soup.find_all('tr', id=lambda x: x and x.startswith('tag-'))
    for row in rows:
        name_tag = row.find('a', class_='row-title')
        id_tag = row.find('input', {'name': 'delete_tags[]'})
        if name_tag and id_tag:
            name = name_tag.get_text()
            cat_id = id_tag.get('value')
            print(f"  - {name} (ID: {cat_id})")

if __name__ == "__main__":
    get_categories()
