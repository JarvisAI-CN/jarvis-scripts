#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贾维斯的自动导航网址发布脚本 (Idle-only version)
"""

import os
import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# 路径配置
WORKSPACE = "/home/ubuntu/.openclaw/workspace"
TASK_FILE = f"{WORKSPACE}/.current_task.json"
QUEUE_FILE = f"{WORKSPACE}/url_queue.json"
LOG_FILE = f"{WORKSPACE}/logs/auto_nav_publish.log"

# WordPress 配置
WP_URL = "http://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")
    print(f"[{timestamp}] {msg}")

def is_busy():
    """检查是否有正在进行的活跃任务"""
    if not os.path.exists(TASK_FILE):
        return False
    try:
        with open(TASK_FILE, "r") as f:
            data = json.load(f)
            return data.get("active_task") is not None
    except:
        return False

def publish_to_wp(item):
    """通过 API 模拟发布到 WordPress"""
    session = requests.Session()
    login_url = f"{WP_URL}/wp-login.php"
    
    # 1. 登录
    try:
        resp = session.get(login_url, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        hidden = {tag.get('name'): tag.get('value', '') for tag in soup.find_all('input', type='hidden') if tag.get('name')}
        
        login_data = {
            'log': WP_ADMIN,
            'pwd': WP_PASSWORD,
            'rememberme': 'forever',
            'wp-submit': '登录',
            **hidden
        }
        session.post(login_url, data=login_data, allow_redirects=True, timeout=15)
        
        if 'wordpress_logged_in' not in session.cookies:
            log("❌ 登录失败")
            return False
            
        # 2. 获取 Nonce
        new_post_url = f"{WP_URL}/wp-admin/post-new.php?post_type=sites"
        resp = session.get(new_post_url, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        nonce = soup.find('input', {'name': '_wpnonce'}).get('value')
        user_id = soup.find('input', {'name': 'user_ID'}).get('value')
        post_id = soup.find('input', {'name': 'post_ID'}).get('value')
        
        # 3. 提交发布 (三位一体标准)
        post_data = {
            '_wpnonce': nonce,
            '_wp_http_referer': "/wp-admin/post-new.php?post_type=sites",
            'user_ID': user_id,
            'action': 'editpost',
            'post_author': user_id,
            'post_type': 'sites',
            'post_ID': post_id,
            'post_title': item['title'],
            'content': item['content'],
            'site_url': item['url'],
            'tax_input[favorites][]': item['category_id'],
            'post_category[]': item['category_id'],
            'post_status': 'publish',
            'publish': '发布',
            # SEO 补全 (基于 OneNav 主题字段)
            'tax_input[sitetag][]': item['tags'],
            'seo_keywords': item['keywords']
        }
        
        publish_url = f"{WP_URL}/wp-admin/post.php"
        resp = session.post(publish_url, data=post_data, timeout=15)
        
        if resp.status_code == 200:
            log(f"✅ 成功发布: {item['title']} (ID: {post_id})")
            return True
        else:
            log(f"❌ 发布请求失败: {resp.status_code}")
            return False
            
    except Exception as e:
        log(f"⚠️ 发生异常: {str(e)}")
        return False

def main():
    if is_busy():
        log("⏸️ 主人正在安排工作，跳过自动发布任务。")
        return

    if not os.path.exists(QUEUE_FILE):
        log("📭 队列文件不存在。")
        return

    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)

    if not queue:
        log("📭 队列已空，请补充网址。")
        # 这里可以加一个 spawn 子代理去搜索新网址的逻辑
        return

    item = queue.pop(0)
    
    if publish_to_wp(item):
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    else:
        # 失败则放回队列末尾
        queue.append(item)
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
