#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress 自动发布脚本 - 发布 Notion AI 写作助手
"""

import requests
from bs4 import BeautifulSoup
import json

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

    print(f"📝 登录数据: {list(login_data.keys())}")

    # 提交登录（不自动重定向）
    response = session.post(login_url, data=login_data, allow_redirects=False)

    # 调试信息
    print(f"📍 第一次响应状态码: {response.status_code}")
    print(f"📍 第一次响应Cookies: {list(session.cookies.keys())}")

    # 如果是重定向，跟随它
    if response.status_code in [302, 303]:
        location = response.headers.get('Location', '')
        print(f"📍 重定向到: {location}")

        # 跟随重定向
        response = session.get(location, allow_redirects=True)

    # 最终检查
    print(f"📍 最终状态码: {response.status_code}")
    print(f"📍 最终URL: {response.url}")
    print(f"📍 最终Cookies: {list(session.cookies.keys())}")

    # 检查是否登录成功
    if 'wordpress_logged_in' in session.cookies:
        print("✅ 登录成功（通过 cookie）")
        return True

    if 'wp-admin' in response.url:
        print("✅ 登录成功（通过 URL）")
        return True

    # 检查页面内容
    if 'dashboard' in response.text.lower():
        print("✅ 登录成功（通过页面内容）")
        return True

    print(f"❌ 登录失败")
    return False

    # 检查 cookies
    if 'wordpress_logged_in' in session.cookies:
        print("✅ 登录成功（通过 cookie）")
        return True

    # 检查响应内容
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        error_div = soup.find('div', {'id': 'login_error'})
        if error_div:
            print(f"❌ 登录失败: {error_div.get_text().strip()}")
        else:
            print(f"❌ 登录失败: 未知错误")
            print(f"📍 最终URL: {response.url}")
    else:
        print(f"❌ 登录失败: HTTP {response.status_code}")

    return False

def get_post_nonce():
    """获取发布文章所需的 nonce"""
    # 访问发布页面
    post_new_url = f"{WP_URL}/wp-admin/post-new.php"
    response = session.get(post_new_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取 nonce
    nonce_input = soup.find('input', {'name': '_wpnonce'})
    if nonce_input:
        return nonce_input.get('value')
    return None

def publish_post():
    """发布文章"""

    # Notion AI 文章内容
    title = "Notion AI - AI智能写作与文档管理平台"
    content = """<h2>AI智能写作与文档管理平台</h2>

<p>Notion AI 是一款集成在 Notion 工作空间中的强大AI助手，它不仅仅是一个写作工具，更是一个完整的AI工作平台。与大多数只停留在创意阶段的AI工具不同，Notion AI 能够帮你完成从构思到成稿的全流程工作。</p>

<h3>核心功能</h3>

<p>Notion AI 提供了多样化的智能服务。它支持<strong>自动生成会议纪要</strong>，并能进行<strong>深入研究</strong>来创建详细的文档和报告。<strong>内容生成与编辑</strong>功能让创作更加流畅，还能<strong>自动填充数据库</strong>的摘要和洞察。<strong>多语言翻译</strong>、<strong>流程图和图表生成</strong>、<strong>智能搜索</strong>以及<strong>数据库设置</strong>功能，都能显著提升工作效率。</p>

<h3>特色亮点</h3>

<p>安全性方面，Notion AI 采用了业界领先的数据保护措施。平台<strong>承诺不会使用客户数据训练模型</strong>，所有数据传输都采用TLS 1.2+加密，并提供细粒度的权限控制。平台已通过<strong>GDPR、CCPA、SOC 2 Type 2和ISO 27001</strong>等多项国际安全认证，确保数据安全得到最高级别的保护。此外，LLM提供商不会存储任何数据，企业版还支持<strong>零数据保留政策</strong>。</p>

<h3>适用人群</h3>

<p>Notion AI 适合各类用户群体。<strong>知识工作者</strong>可以用于笔记管理和文档协作，<strong>创作者</strong>能够获得灵感激发和内容生成支持，<strong>产品经理</strong>可以用它来构建知识库，<strong>企业团队</strong>则能利用AI进行深度研究和报告生成。对于<strong>学生和研究人员</strong>，它同样是强大的学习和研究工具。</p>

<h3>总结推荐</h3>

<p>Notion AI 的核心优势在于<strong>深度整合到Notion工作空间</strong>，实现了"一个平台完成所有工作"的理念。它支持<strong>GPT-4.1、Claude 4</strong>等多种AI模型，并通过<strong>MCP协议</strong>连接第三方应用。<strong>AI会议笔记</strong>功能可以帮助团队轻松转录会议内容并提取关键信息。定价方面，Business和Enterprise计划已包含Notion AI功能，其他计划提供有限的试用额度。对于寻求一体化AI工作平台的用户来说，Notion AI是值得投资的选择。</p>

<p>THE END</p>

<h2>访问建议</h2>

<p>为确保最佳使用体验，建议通过浏览器访问 Notion AI 官网。微信或QQ可能会屏蔽相关链接，请使用浏览器直接访问。推荐使用未屏蔽网址的浏览器，如苹果设备自带的Safari浏览器、谷歌Chrome或微软Edge等主流浏览器。如果遇到访问问题，请检查网络连接或使用VPN切换到更稳定的运营商网络。</p>
"""

    url = "https://www.notion.so/product/ai"
    categories = "AI"  # 需要设置为 AI 分类

    # 访问添加新文章页面
    post_url = f"{WP_URL}/wp-admin/post-new.php"
    response = session.get(post_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 获取所有必要的 hidden 字段
    hidden_fields = {}
    for input_tag in soup.find_all('input', type='hidden'):
        if input_tag.get('name'):
            hidden_fields[input_tag['name']] = input_tag.get('value', '')

    print(f"📝 准备发布文章: {title}")
    print(f"🔗 链接: {url}")
    print(f"📁 分类: {categories}")

    # 构建文章数据
    post_data = {
        'post_title': title,
        'content': content,
        'post_url': url,  # 假设这是自定义字段
        'tax_input[category][]': categories,
        'post_category[]': categories,
        'post_status': 'publish',
        'publish': '发布',
        **hidden_fields
    }

    # 提交文章
    response = session.post(post_url, data=post_data, allow_redirects=True)

    if response.status_code == 200:
        print("✅ 文章提交成功")

        # 尝试从响应中提取文章URL
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找成功消息
        message_div = soup.find('div', {'id': 'message'})
        if message_div:
            print(f"📢 {message_div.get_text().strip()}")

        # 查找文章链接
        link_tag = soup.find('a', {'id': 'sample-permalink'})
        if link_tag:
            post_url = link_tag.get('href')
            print(f"🔗 文章链接: {post_url}")
            return post_url
        else:
            print("⚠️ 未能提取文章链接，请手动查看")
            return None
    else:
        print(f"❌ 文章提交失败: {response.status_code}")
        return None

def main():
    print("=" * 60)
    print("🚀 WordPress 自动发布脚本 - Notion AI")
    print("=" * 60)

    # 登录
    if not login():
        return

    # 发布文章
    post_url = publish_post()

    if post_url:
        print(f"\n✅ 发布成功！")
        print(f"🔗 文章链接: {post_url}")
    else:
        print(f"\n⚠️ 发布可能成功，请手动确认")

    print("=" * 60)

if __name__ == "__main__":
    main()
