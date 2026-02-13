#!/usr/bin/env python3
"""检查Moltbook最近的帖子 - 详细版本"""

import requests
import json
from datetime import datetime

API_BASE = "https://www.moltbook.com/api/v1"
API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"

def check_posts_detailed():
    """详细检查帖子"""
    try:
        response = requests.get(
            f"{API_BASE}/posts",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"sort": "new", "limit": 50}
        )

        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])

            print(f"\n📊 最近50篇帖子：")
            print("=" * 100)

            # 显示所有帖子作者
            authors = {}
            title_count = {}

            for i, post in enumerate(posts[:20], 1):  # 只看前20篇
                author = post.get("author", {}).get("name", "Unknown")
                title = post.get("title", "No title")
                created_at = post.get("createdAt", "")

                # 统计作者
                if author in authors:
                    authors[author] += 1
                else:
                    authors[author] = 1

                # 统计标题
                full_title = title[:60]
                if full_title in title_count:
                    title_count[full_title] += 1
                    print(f"⚠️ 重复标题 #{i}: {full_title}... (作者: {author})")
                else:
                    title_count[full_title] = 1
                    print(f"{i}. {full_title}... (作者: {author})")

            print(f"\n📊 作者统计：")
            for author, count in sorted(authors.items(), key=lambda x: -x[1]):
                print(f"   {author}: {count} 篇")

            # 检查重复
            duplicates = {k: v for k, v in title_count.items() if v > 1}

            if duplicates:
                print(f"\n⚠️ 发现重复标题：")
                for title, count in duplicates.items():
                    print(f"   '{title}...' 出现 {count} 次")
            else:
                print(f"\n✅ 没有发现重复标题")

        else:
            print(f"❌ API错误: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_posts_detailed()
