#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 自动发布脚本 - 发布 Khanmigo 学习教育助手
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# WordPress 配置
WP_URL = "http://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

# 创建会话
session = requests.Session()

def login():
    """登录 WordPress 后台"""
    login_url = f"{WP_URL}/wp-login.php"

    # 设置 User-Agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    session.headers.update(headers)

    # 获取登录页面
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取 hidden 字段
    hidden_fields = {}
    for input_tag in soup.find_all('input', type='hidden'):
        if input_tag.get('name'):
            hidden_fields[input_tag['name']] = input_tag.get('value', '')

    print(f"🔍 找到的隐藏字段: {list(hidden_fields.keys())}")

    # 构建登录数据
    login_data = {
        'log': WP_ADMIN,
        'pwd': WP_PASSWORD,
        'rememberme': 'forever',
        'wp-submit': '登录',
        'redirect_to': f"{WP_URL}/wp-admin/",
        'testcookie': '1',
        **hidden_fields
    }

    # 提交登录
    response = session.post(login_url, data=login_data, allow_redirects=True)

    # 检查是否登录成功
    if 'wordpress_logged_in' in session.cookies or 'wp-admin' in response.url or 'dashboard' in response.text.lower():
        print("✅ 登录成功")
        return True

    print(f"❌ 登录失败")
    return False

def publish_post():
    """发布网址"""

    # Khanmigo 内容
    title = "Khanmigo - 可汗学院 AI 智能学习辅导助手"
    content = """<h2>可汗学院 AI 智能学习助手</h2>

<p>Khanmigo 是由全球知名的非营利教育机构可汗学院（Khan Academy）推出的 AI 辅导工具。它基于先进的大语言模型，旨在为每一位学生提供全天候的个性化导师，同时为教师提供强大的教学辅助支持。Khanmigo 的设计初衷不是为了替代教师，而是为了通过技术手段实现教育的公平与高效。</p>

<h3>核心功能</h3>

<p><strong>学生个性化辅导</strong>：Khanmigo 涵盖了数学、科学、人文、编程等多个学科。它最显著的特点是<strong>“启发式教学”</strong>——当学生遇到难题时，它不会直接给出答案，而是通过提问引导学生逐步思考，培养解决问题的能力。它还能与学生一起进行创意写作，或者扮演历史人物进行模拟对话。</p>

<p><strong>教师助手功能</strong>：Khanmigo 大大减轻了教师的行政负担。它能协助教师<strong>编写个性化教案</strong>、设计课堂讨论题目、撰写学生反馈，甚至帮助设计复杂的教学评估。它能根据学生的掌握情况，为教师提供针对性的教学建议。</p>

<h3>特色亮点</h3>

<p><strong>教育导向的安全设计</strong>：Khanmigo 严格遵循教育安全标准。它具有内置的内容过滤器，确保对话始终保持在学术和安全的范围内。此外，家长和教师可以查看对话摘要，确保 AI 的使用符合教育目标。其<strong>“不直接给出答案”</strong>的算法逻辑，从根本上防止了学术作弊，鼓励深度学习。</p>

<h3>适用人群</h3>

<p><strong>学生</strong>：需要课后辅导、备考支持或希望提升自学能力的所有阶段学生。<strong>教师</strong>：希望优化课堂设计、提高教学效率并实施差异化教学的教育工作者。<strong>家长</strong>：希望为孩子提供高质量、安全的辅助学习工具的家庭。</p>

<h3>总结推荐</h3>

<p>Khanmigo 是目前教育领域最成熟、最符合教学逻辑的 AI 应用之一。它将可汗学院丰富的教育资源与 AI 技术的交互性完美结合。虽然它是付费订阅服务（部分地区合作伙伴除外），但其提供的导师级体验对于追求卓越学习效果的用户来说，是极具价值的选择。它是“人工智能+教育”的标杆性作品。</p>

<p>THE END</p>

<h2>访问建议</h2>

<p>建议通过浏览器访问 Khanmigo 官方页面获取最新功能信息和订阅指南。在部分网络环境下，访问可能需要稳定的国际连接。推荐使用最新版本的谷歌 Chrome、微软 Edge 或 Safari 浏览器，以确保互动功能的流畅运行。</p>
"""

    url = "https://www.khanacademy.org/khanmigo"
    category_id = "34"  # 学习教育分类 ID

    # 1. 访问添加新网址页面获取 nonce 等信息
    post_new_url = f"{WP_URL}/wp-admin/post-new.php?post_type=sites"
    response = session.get(post_new_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取 post_ID
    post_id_input = soup.find('input', {'name': 'post_ID'})
    if not post_id_input:
        post_id_input = soup.find('input', {'id': 'post_ID'})
    
    if not post_id_input:
        print("❌ 无法获取 Post ID")
        return None
    
    post_id = post_id_input.get('value')
    print(f"📌 获取到临时文章 ID: {post_id}")

    # 提取 nonce
    nonce = soup.find('input', {'name': '_wpnonce'}).get('value')
    user_id = soup.find('input', {'name': 'user_ID'}).get('value')
    post_type = soup.find('input', {'name': 'post_type'}).get('value')
    original_post_status = soup.find('input', {'name': 'original_post_status'}).get('value')

    print(f"📝 准备发布文章: {title}")

    # 构建发布数据
    post_data = {
        '_wpnonce': nonce,
        '_wp_http_referer': f"/wp-admin/post-new.php?post_type=sites",
        'user_ID': user_id,
        'action': 'editpost',
        'originalaction': 'editpost',
        'post_author': user_id,
        'post_type': post_type,
        'post_ID': post_id,
        'original_post_status': original_post_status,
        'auto_draft': '1',
        'post_title': title,
        'content': content,
        'site_url': url,  # OneNav 核心自定义字段
        'tax_input[favorites][]': category_id,
        'post_category[]': category_id,
        'post_status': 'publish',
        'publish': '发布',
        'original_publish': '发布',
        'save': ''
    }

    # 提交发布
    publish_url = f"{WP_URL}/wp-admin/post.php"
    response = session.post(publish_url, data=post_data, allow_redirects=True)

    if response.status_code == 200:
        if "文章已发布" in response.text or f"post.php?post={post_id}" in response.url:
            print("✅ 文章提交成功")
            final_url = f"{WP_URL}/sites/{post_id}.html"
            return final_url
        else:
            print("⚠️ 发布状态未知，请手动检查")
            return None
    else:
        print(f"❌ 文章提交失败: HTTP {response.status_code}")
        return None

def main():
    print("=" * 60)
    print("🚀 WordPress 自动发布脚本 - Khanmigo")
    print("=" * 60)

    # 登录
    if not login():
        return

    # 发布文章
    post_url = publish_post()

    if post_url:
        print(f"\n✅ 发布成功！")
        print(f"🔗 预览链接 (可能需要根据固定链接调整): {post_url}")
    else:
        print(f"\n⚠️ 发布可能已提交，请去后台确认")

    print("=" * 60)

if __name__ == "__main__":
    main()
