#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook发布质量验证系统
功能：发布后自动验证帖子质量，检测重复内容，生成报告
"""

import requests
import json
import re
from datetime import datetime
from difflib import SequenceMatcher
import hashlib

# 配置
API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_quality.log"
QUALITY_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_quality_report.json"

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def get_post_content(post_id):
    """获取帖子内容"""
    url = f"{API_BASE}/posts/{post_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            log_message(f"❌ 获取帖子失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        log_message(f"❌ 获取帖子异常: {str(e)}")
        return None

def get_user_posts(username="JarvisAI-CN", limit=20):
    """获取用户的帖子列表"""
    # 先获取用户ID
    user_url = f"{API_BASE}/users/{username}"
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        # 获取用户信息
        user_response = requests.get(user_url, headers=headers, timeout=10)
        if user_response.status_code != 200:
            log_message(f"❌ 获取用户信息失败: HTTP {user_response.status_code}")
            return []

        user_data = user_response.json()
        user_id = user_data.get('id')

        if not user_id:
            log_message(f"❌ 无法获取用户ID")
            return []

        # 获取帖子列表
        posts_url = f"{API_BASE}/users/{user_id}/posts"
        params = {"limit": limit}
        posts_response = requests.get(posts_url, headers=headers, params=params, timeout=10)

        if posts_response.status_code == 200:
            data = posts_response.json()
            return data.get('posts', [])
        else:
            log_message(f"❌ 获取帖子列表失败: HTTP {posts_response.status_code}")
            return []

    except Exception as e:
        log_message(f"❌ 获取帖子列表异常: {str(e)}")
        return []

def calculate_similarity(text1, text2):
    """计算两个文本的相似度"""
    return SequenceMatcher(None, text1, text2).ratio()

def get_content_hash(content):
    """获取内容的哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def detect_duplicates(posts):
    """检测重复内容"""
    duplicates = []
    content_map = {}

    for post in posts:
        content = post.get('content', '')
        content_hash = get_content_hash(content)

        if content_hash in content_map:
            duplicates.append({
                'original_id': content_map[content_hash],
                'duplicate_id': post.get('id'),
                'title': post.get('title'),
                'similarity': 1.0
            })
        else:
            content_map[content_hash] = post.get('id')

    return duplicates

def validate_post(post):
    """验证单个帖子的质量"""
    issues = []

    # 检查标题
    title = post.get('title', '')
    if len(title) < 10:
        issues.append("标题过短")

    # 检查内容
    content = post.get('content', '')
    if len(content) < 100:
        issues.append("内容过短")

    # 检查是否有占位符
    if '...（待准备）' in content or '待准备' in content:
        issues.append("内容包含占位符")

    # 检查标题中是否有"压缩的魔法"（特定重复内容标记）
    if '压缩的魔法' in title and title.count('压缩') > 0:
        issues.append("可能是重复内容（压缩主题）")

    return issues

def generate_quality_report():
    """生成质量报告"""
    log_message("=" * 60)
    log_message("开始质量检查...")

    # 获取最近20篇帖子
    posts = get_user_posts(limit=20)

    if not posts:
        log_message("⚠️ 无法获取帖子列表")
        return

    log_message(f"📊 获取到 {len(posts)} 篇帖子")

    # 检测重复
    duplicates = detect_duplicates(posts)

    # 验证每篇帖子
    validation_results = []
    for post in posts:
        issues = validate_post(post)
        validation_results.append({
            'id': post.get('id'),
            'title': post.get('title'),
            'created_at': post.get('created_at'),
            'issues': issues,
            'upvotes': post.get('upvotes', 0),
            'comments': post.get('comment_count', 0)
        })

    # 生成报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_posts': len(posts),
        'duplicates_found': len(duplicates),
        'duplicate_details': duplicates,
        'validation_results': validation_results,
        'posts_with_issues': len([r for r in validation_results if r['issues']]),
        'summary': {
            'needs_attention': len(duplicates) > 0 or any(r['issues'] for r in validation_results),
            'duplicate_count': len(duplicates),
            'issue_count': sum(len(r['issues']) for r in validation_results)
        }
    }

    # 保存报告
    with open(QUALITY_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # 输出摘要
    log_message(f"\n📋 质量检查摘要:")
    log_message(f"   总帖子数: {report['total_posts']}")
    log_message(f"   重复帖子: {report['duplicates_found']}")
    log_message(f"   有问题帖子: {report['posts_with_issues']}")
    log_message(f"   需要关注: {'是' if report['summary']['needs_attention'] else '否'}")

    # 如果发现重复，列出详情
    if duplicates:
        log_message(f"\n⚠️ 发现重复内容:")
        for dup in duplicates[:5]:  # 只显示前5个
            log_message(f"   - 原文ID: {dup['original_id'][:8]}...")
            log_message(f"     重复ID: {dup['duplicate_id'][:8]}...")
            log_message(f"     标题: {dup['title']}")

    # 如果发现其他问题，列出详情
    problematic_posts = [r for r in validation_results if r['issues']]
    if problematic_posts:
        log_message(f"\n⚠️ 发现问题帖子:")
        for post in problematic_posts[:5]:
            log_message(f"   - {post['title'][:40]}...")
            for issue in post['issues']:
                log_message(f"     • {issue}")

    log_message("=" * 60)

    return report

def verify_latest_post(expected_title=None):
    """验证最新发布的帖子"""
    posts = get_user_posts(limit=5)

    if not posts:
        log_message("⚠️ 无法获取帖子进行验证")
        return False

    latest_post = posts[0]

    log_message(f"\n🔍 验证最新帖子:")
    log_message(f"   标题: {latest_post.get('title')}")

    if expected_title:
        if expected_title in latest_post.get('title', ''):
            log_message(f"   ✅ 标题匹配")
        else:
            log_message(f"   ❌ 标题不匹配（期望: {expected_title}）")
            return False

    # 检查内容
    content = latest_post.get('content', '')
    if len(content) < 100:
        log_message(f"   ❌ 内容过短: {len(content)} 字符")
        return False

    # 检查占位符
    if '待准备' in content or '...' in content:
        log_message(f"   ⚠️ 内容可能包含占位符")

    log_message(f"   ✅ 验证通过")
    return True

def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "verify":
            # 验证最新帖子
            expected_title = sys.argv[2] if len(sys.argv) > 2 else None
            verify_latest_post(expected_title)

        elif command == "report":
            # 生成质量报告
            generate_quality_report()

        elif command == "check":
            # 快速检查
            report = generate_quality_report()
            if report['summary']['needs_attention']:
                log_message("\n⚠️ 需要关注！请查看详细报告")
                exit(1)
            else:
                log_message("\n✅ 质量检查通过")
                exit(0)

    else:
        # 默认生成报告
        generate_quality_report()

if __name__ == "__main__":
    main()
