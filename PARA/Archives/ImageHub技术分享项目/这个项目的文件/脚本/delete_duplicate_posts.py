#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并删除Moltbook上的重复帖子
保留讨论度最高的，删除其他重复的
"""

import requests
import json
from datetime import datetime

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"

def get_my_posts(limit=50):
    """获取我发布的帖子"""
    # 尝试不同的API端点
    endpoints = [
        f"{API_BASE}/users/me/posts",
        f"{API_BASE}/posts?limit={limit}",
        f"{API_BASE}/users/JarvisAI-CN/posts?limit={limit}"
    ]

    headers = {"Authorization": f"Bearer {API_KEY}"}

    for endpoint in endpoints:
        try:
            print(f"尝试端点: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取数据")
                print(f"数据结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                return data
            else:
                print(f"响应: {response.text[:200]}")

        except Exception as e:
            print(f"错误: {str(e)}")

    return None

def find_duplicates(posts):
    """找出重复的帖子"""
    if not posts:
        return []

    # 假设posts是一个列表或包含posts字段
    post_list = posts if isinstance(posts, list) else posts.get('posts', [])

    duplicates = []
    title_counts = {}

    for post in post_list:
        title = post.get('title', '')
        if '压缩' in title or '3.4MB' in title:
            title_counts[title] = title_counts.get(title, 0) + 1
            duplicates.append({
                'id': post.get('id'),
                'title': title,
                'upvotes': post.get('upvotes', 0),
                'comments': post.get('comment_count', 0),
                'created_at': post.get('created_at'),
                'url': f"https://www.moltbook.com/post/{post.get('id')}"
            })

    return duplicates

def delete_post(post_id):
    """删除帖子"""
    url = f"{API_BASE}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.delete(url, headers=headers, timeout=10)
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            print(f"删除失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"删除异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Moltbook重复帖子检查和删除")
    print("=" * 60)

    # 获取帖子
    print("\n1. 获取帖子列表...")
    posts = get_my_posts(limit=50)

    if not posts:
        print("❌ 无法获取帖子列表")
        print("\n可能的原因:")
        print("- API端点不正确")
        print("- 需要使用不同的认证方式")
        print("- 需要通过网页手动检查")
        return

    # 找出重复
    print("\n2. 查找重复帖子...")
    duplicates = find_duplicates(posts)

    if not duplicates:
        print("✅ 没有发现重复帖子")
        return

    print(f"\n发现 {len(duplicates)} 篇可能重复的帖子:")
    print("-" * 60)

    # 按讨论度排序（upvotes + comments）
    for i, post in enumerate(duplicates, 1):
        score = post['upvotes'] + post['comments']
        print(f"\n{i}. {post['title'][:50]}...")
        print(f"   ID: {post['id'][:8]}...")
        print(f"   👍 {post['upvotes']} | 💬 {post['comments']} | 总分: {score}")
        print(f"   时间: {post['created_at']}")
        print(f"   链接: {post['url']}")

    # 保留最好的，删除其他
    print("\n" + "=" * 60)
    print("3. 删除重复帖子...")

    # 按分数排序，保留最高的
    sorted_posts = sorted(duplicates, key=lambda x: x['upvotes'] + x['comments'], reverse=True)
    keep = sorted_posts[0]
    delete_list = sorted_posts[1:]

    print(f"\n✅ 保留: {keep['title'][:40]}...")
    print(f"   👍 {keep['upvotes']} | 💬 {keep['comments']} | 总分: {keep['upvotes'] + keep['comments']}")

    print(f"\n🗑️  准备删除 {len(delete_list)} 个重复帖子:")

    confirmed = input("\n确认删除吗？(yes/no): ")

    if confirmed.lower() != 'yes':
        print("❌ 已取消")
        return

    deleted_count = 0
    for post in delete_list:
        print(f"\n删除: {post['title'][:40]}...")
        if delete_post(post['id']):
            print(f"   ✅ 删除成功")
            deleted_count += 1
        else:
            print(f"   ❌ 删除失败")

    print(f"\n" + "=" * 60)
    print(f"✅ 完成！保留了最好的，删除了 {deleted_count} 个重复帖子")
    print("=" * 60)

if __name__ == "__main__":
    main()
