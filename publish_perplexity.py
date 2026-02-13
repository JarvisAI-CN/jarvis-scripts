#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 自动发布脚本 - 发布 Perplexity AI
"""

import requests
from bs4 import BeautifulSoup
import json
import time

# WordPress 配置
WP_URL = "https://dh.dhmip.cn"
WP_ADMIN = "admin"
WP_PASSWORD = "fs123456"

# 创建会话
session = requests.Session()

def login():
    """登录 WordPress 后台"""
    login_url = f"{WP_URL}/wp-login.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    session.headers.update(headers)
    response = session.get(login_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    hidden_fields = {input_tag['name']: input_tag.get('value', '') for input_tag in soup.find_all('input', type='hidden') if input_tag.get('name')}
    login_data = {
        'log': WP_ADMIN,
        'pwd': WP_PASSWORD,
        'rememberme': 'forever',
        'wp-submit': '登录',
        'redirect_to': f"{WP_URL}/wp-admin/",
        'testcookie': '1',
        **hidden_fields
    }
    response = session.post(login_url, data=login_data, allow_redirects=True)
    if 'wordpress_logged_in' in session.cookies or 'wp-admin' in response.url:
        print("✅ 登录成功")
        return True
    print(f"❌ 登录失败")
    return False

def publish_post():
    """发布网址"""
    title = "Perplexity AI - 智能 AI 问答搜索引擎"
    content = """<h2>Perplexity AI: 重新定义搜索体验</h2>

<p>Perplexity AI 是一款革新性的 AI 问答搜索引擎，它将传统搜索的广泛性与大语言模型的理解能力完美结合。不同于传统的搜索引擎只提供链接列表，Perplexity 直接针对你的问题提供完整、通顺且带有实时信息标注的回答。它是目前市场上最受推崇的“AI 搜索”工具之一。</p>

<h3>核心功能</h3>

<p><strong>实时信息检索</strong>：Perplexity 能够实时访问互联网，这意味着它提供的回答不仅基于训练数据，还包含了最新的新闻、研究和动态。这对于查询近期发生的事件或不断变化的科技信息至关重要。</p>

<p><strong>自动引用来源</strong>：这是 Perplexity 最受好评的功能。它的每一个回答都会附带清晰的脚注和引用链接。用户可以点击这些链接查看原始网页，验证信息的准确性，从根本上减少了 AI 可能出现的“幻觉”问题。</p>

<p><strong>多模型选择（Pro 版）</strong>：对于专业用户，Perplexity Pro 允许在不同的顶级模型之间切换，如 GPT-4o、Claude 3.5 Sonnet 等。这让用户可以根据具体任务（如代码编写或长文分析）选择最适合的“大脑”。</p>

<h3>特色亮点</h3>

<p><strong>Discover 探索频道</strong>：除了搜索，Perplexity 还提供了一个类似信息流的频道，展示全球范围内由 AI 总结的热门话题和深度报道。<strong>多平台支持</strong>：拥有出色的 iOS 和 Android 客户端，以及 Chrome 浏览器扩展，让用户随时随地享受智能搜索的便利。</p>

<h3>适用人群</h3>

<p><strong>研究人员与学生</strong>：需要快速查找资料并核实来源。<strong>开发者</strong>：查找代码片段及最新文档。<strong>内容创作者</strong>：进行背景调研并寻找创作灵感。<strong>任何对传统搜索广告干扰感到厌倦的用户</strong>。</p>

<h3>总结推荐</h3>

<p>Perplexity AI 代表了搜索引擎的未来。它通过“对话即搜索”的方式，极大地缩短了获取准确信息的时间路径。如果你希望在海量信息中快速提取精华，并保持对信息源的可追踪性，Perplexity 是你的必选工具。它正在成为许多专业人士首选的生产力工具。</p>

<p>THE END</p>
"""

    url = "https://www.perplexity.ai/"
    category_id = "9"  # AI 分类 ID

    # 1. 访问添加新网址页面获取 nonce 等信息
    post_new_url = f"{WP_URL}/wp-admin/post-new.php?post_type=sites"
    response = session.get(post_new_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    post_id_input = soup.find('input', {'name': 'post_ID'}) or soup.find('input', {'id': 'post_ID'})
    if not post_id_input:
        print("❌ 无法获取 Post ID")
        return None
    
    post_id = post_id_input.get('value')
    print(f"📌 获取到临时文章 ID: {post_id}")

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
        'site_url': url,
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
            return f"{WP_URL}/sites/{post_id}.html"
        else:
            print("⚠️ 发布状态未知，请手动检查")
            return None
    else:
        print(f"❌ 文章提交失败: HTTP {response.status_code}")
        return None

def main():
    if not login():
        return
    post_url = publish_post()
    if post_url:
        print(f"\n✅ 发布成功！链接: {post_url}")
    else:
        print(f"\n⚠️ 发布可能已提交，请去后台确认")

if __name__ == "__main__":
    main()
