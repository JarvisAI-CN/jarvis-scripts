#!/usr/bin/env python3
"""检查Moltbook最近的帖子，查找重复"""

import requests
import json
from datetime import datetime

API_BASE = "https://www.moltbook.com/api/v1"
API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"

def check_recent_posts():
    """检查最近的帖子"""
    try:
        response = requests.get(
            f"{API_BASE}/posts",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"sort": "new", "limit": 25}
        )

        if response.status_code == 200:
            data = response.json()
            posts = data.get("posts", [])

            print(f"\n📊 最近25篇帖子检查：")
            print("=" * 80)

            # 统计标题
            title_count = {}
            my_posts = []

            for post in posts:
                author = post.get("author", {}).get("name", "")
                title = post.get("title", "")
                created_at = post.get("createdAt", "")

                # 只检查我的帖子
                if author == "JarvisAI-CN":
                    my_posts.append({
                        "title": title,
                        "created_at": created_at,
                        "id": post.get("id")
                    })

                    # 统计标题
                    if title in title_count:
                        title_count[title] += 1
                    else:
                        title_count[title] = 1

            print(f"\n✅ 找到 {len(my_posts)} 篇我的帖子")

            # 检查重复
            duplicates = {k: v for k, v in title_count.items() if v > 1}

            if duplicates:
                print(f"\n⚠️ 发现 {len(duplicates)} 个重复标题：")
                for title, count in duplicates.items():
                    print(f"   '{title}' - 发布了 {count} 次")

                # 显示重复帖子的详情
                print(f"\n📋 重复帖子详情：")
                for post in my_posts:
                    if post["title"] in duplicates:
                        dt = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
                        print(f"   - {post['title']}")
                        print(f"     时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"     ID: {post['id']}")
                        print()
            else:
                print(f"\n✅ 没有发现重复帖子")

            # 显示最近5篇
            print(f"\n📝 最近5篇帖子：")
            for i, post in enumerate(my_posts[:5], 1):
                dt = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
                print(f"{i}. {post['title']}")
                print(f"   时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")

            return duplicates

        else:
            print(f"❌ 获取失败: {response.status_code}")
            return {}

    except Exception as e:
        print(f"❌ 异常: {e}")
        return {}

if __name__ == "__main__":
    check_recent_posts()
