#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re

WP_URL = "https://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

session = requests.Session()

def login():
    login_url = f"{WP_URL}/wp-login.php"
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    hidden_fields = {input_tag['name']: input_tag.get('value', '') for input_tag in soup.find_all('input', type='hidden') if input_tag.get('name')}
    login_data = {'log': WP_ADMIN, 'pwd': WP_PASSWORD, 'wp-submit': '登录', 'testcookie': '1', **hidden_fields}
    session.post(login_url, data=login_data)

def get_cat_id(search_name):
    cat_url = f"{WP_URL}/wp-admin/edit-tags.php?taxonomy=favorites"
    response = session.get(cat_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for row in soup.find_all('tr', id=lambda x: x and x.startswith('tag-')):
        name = row.find('a', class_='row-title').get_text(strip=True)
        if search_name.lower() in name.lower():
            cat_id = row.find('input', {'name': 'delete_tags[]'})['value']
            print(f"Found Category: {name} (ID: {cat_id})")
            return cat_id
    return None

if __name__ == "__main__":
    login()
    get_cat_id("AI")
    get_cat_id("学习")
