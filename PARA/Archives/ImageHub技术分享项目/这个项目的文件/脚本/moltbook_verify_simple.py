#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook发布验证脚本（简化版）
基于已知帖子ID进行验证
"""

import requests
import json
from datetime import datetime

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_verify.log"

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def verify_post_by_id(post_id, expected_title=None):
    """通过ID验证帖子"""
    url = f"{API_BASE}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            log_message(f"❌ 获取帖子失败: HTTP {response.status_code}")
            return False

        post = response.json()

        title = post.get('title', 'Unknown')
        content = post.get('content', '')
        upvotes = post.get('upvotes', 0)
        comments = post.get('comment_count', 0)

        log_message(f"\n📄 帖子验证:")
        log_message(f"   ID: {post_id[:8]}...")
        log_message(f"   标题: {title[:60]}...")
        log_message(f"   内容长度: {len(content)} 字符")
        log_message(f"   👍 {upvotes} | 💬 {comments}")

        # 验证标题
        if expected_title and expected_title not in title:
            log_message(f"   ⚠️ 标题可能不匹配（期望包含: {expected_title}）")
            return False

        # 验证内容长度
        if len(content) < 200:
            log_message(f"   ❌ 内容过短（< 200字符）")
            return False

        # 检查占位符
        if '...（待准备）' in content or '待准备' in content:
            log_message(f"   ❌ 内容包含占位符")
            return False

        # 检查特定重复内容标记
        if '压缩的魔法' in title and content.count('压缩') > 20:
            log_message(f"   ⚠️ 可能是重复内容（压缩主题）")

        log_message(f"   ✅ 验证通过")
        return True

    except Exception as e:
        log_message(f"❌ 验证异常: {str(e)}")
        return False

def check_duplicates(post_ids):
    """检查重复内容"""
    contents = {}

    for post_id in post_ids[:10]:  # 只检查前10个
        url = f"{API_BASE}/posts/{post_id}"
        headers = {"Authorization": f"Bearer {API_KEY}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                post = response.json()
                content = post.get('content', '')
                title = post.get('title', '')

                # 简单哈希检查
                content_hash = hash(content)

                if content_hash in contents:
                    log_message(f"\n⚠️ 发现重复内容:")
                    log_message(f"   原文: {contents[content_hash]['title'][:40]}...")
                    log_message(f"   重复: {title[:40]}...")
                else:
                    contents[content_hash] = {'title': title, 'id': post_id}

        except Exception as e:
            log_message(f"❌ 检查异常: {str(e)}")

    log_message(f"\n✅ 重复检查完成（检查了{min(len(post_ids), 10)}篇帖子）")

def main():
    """主函数"""
    import sys

    log_message("=" * 60)
    log_message("Moltbook发布验证")

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "verify" and len(sys.argv) > 2:
            # 验证单个帖子
            post_id = sys.argv[2]
            expected_title = sys.argv[3] if len(sys.argv) > 3 else None
            verify_post_by_id(post_id, expected_title)

        elif command == "check" and len(sys.argv) > 2:
            # 检查重复（传入多个ID）
            post_ids = sys.argv[2].split(',')
            check_duplicates(post_ids)

    else:
        log_message("\n使用方法:")
        log_message("  python3 moltbook_verify_simple.py verify <post_id> [expected_title]")
        log_message("  python3 moltbook_verify_simple.py check <post_id1,post_id2,...>")
        log_message("\n示例:")
        log_message("  python3 moltbook_verify_simple.py verify abc123...")
        log_message("  python3 moltbook_verify_simple.py verify abc123... '压缩'")

    log_message("=" * 60)

if __name__ == "__main__":
    main()
