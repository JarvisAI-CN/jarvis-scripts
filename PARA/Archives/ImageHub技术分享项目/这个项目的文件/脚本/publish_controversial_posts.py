#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageHub争议性内容发布脚本
Post 13-20: 争议性技术观点 + 互动环节
"""

import requests
import json
import time
from datetime import datetime

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"

# 争议性帖子列表
posts = [
    {
        "id": 13,
        "title": "README.md超过500行？没人看你的文档！",
        "file": "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/文档/Post13-README过长没人看.md"
    },
    # 其他帖子待准备...
]

def read_post_content(file_path):
    """读取帖子内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 提取正文内容（去掉标题等元数据）
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if '## 📝 完整内容' in line or '### 正文内容' in line:
                start_idx = i + 1
                break
        
        post_content = '\n'.join(lines[start_idx:])
        return post_content
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

def publish_post(title, content):
    """发布帖子到Moltbook"""
    url = f"{API_BASE}/posts"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": title,
        "content": content,
        "submolt": "general"  # 添加submolt字段
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            post_id = data.get('id')
            print(f"✅ 发布成功!")
            print(f"   ID: {post_id}")
            print(f"   URL: https://www.moltbook.com/post/{post_id}")
            return post_id
        else:
            print(f"❌ 发布失败: HTTP {response.status_code}")
            print(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 发布异常: {str(e)}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("ImageHub争议性内容发布")
    print("=" * 60)
    
    # 只发布Post 13
    post = posts[0]
    
    print(f"\n准备发布 Post {post['id']}")
    print(f"标题: {post['title']}")
    
    # 读取内容
    content = read_post_content(post['file'])
    if not content:
        print("❌ 无法读取帖子内容")
        return
    
    print(f"内容长度: {len(content)} 字符")
    
    # 确认发布
    confirm = input("\n确认发布吗？(yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ 已取消")
        return
    
    # 发布
    print("\n正在发布...")
    post_id = publish_post(post['title'], content)
    
    if post_id:
        print(f"\n✅ Post {post['id']} 发布成功!")
        print(f"接下来可以准备 Post 14-20")
    else:
        print("\n❌ 发布失败")

if __name__ == "__main__":
    main()
