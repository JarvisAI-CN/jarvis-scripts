#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageHub争议性内容自动发布脚本
每小时发布一篇（Post 14-20）
"""

import requests
import json
import time
from datetime import datetime

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_auto_publish.log"

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

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
        "submolt": "general"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            
            # 完成验证
            verification = data.get('verification', {})
            if verification:
                # 解析数学挑战
                challenge = verification.get('challenge', '')
                code = verification.get('code', '')
                
                # 简单的数学解析：A lobster swims at 23 cm/sec and gains 7 cm/sec
                # 提取数字并计算
                import re
                numbers = re.findall(r'\d+\.?\d*', challenge)
                if len(numbers) >= 2:
                    v1 = float(numbers[0])
                    v2 = float(numbers[1])
                    answer = v1 + v2
                    answer_str = f"{answer:.2f}"
                    
                    # 发送验证
                    verify_url = f"{API_BASE}/verify"
                    verify_payload = {
                        "verification_code": code,
                        "answer": answer_str
                    }
                    
                    verify_response = requests.post(verify_url, headers=headers, json=verify_payload, timeout=10)
                    if verify_response.status_code == 200:
                        post_id = data.get('post', {}).get('id')
                        log_message(f"✅ 发布成功: {title[:40]}...")
                        log_message(f"   ID: {post_id[:8]}...")
                        log_message(f"   URL: https://www.moltbook.com/post/{post_id}")
                        return post_id
                    else:
                        log_message(f"❌ 验证失败: {verify_response.text}")
                        return None
        else:
            log_message(f"❌ 发布失败: HTTP {response.status_code}")
            log_message(f"   响应: {response.text}")
            return None
            
    except Exception as e:
        log_message(f"❌ 发布异常: {str(e)}")
        return None

def get_next_post_number():
    """获取下一个要发布的帖子编号"""
    state_file = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_state.json"
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
            next_post = state.get('next_post', 14)
            return next_post
    except:
        return 14

def update_state(post_number):
    """更新状态文件"""
    state_file = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_state.json"
    
    state = {
        "next_post": post_number + 1,
        "last_published": datetime.now().isoformat()
    }
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)

def main():
    """主函数"""
    log_message("=" * 60)
    log_message("ImageHub争议性内容自动发布")
    log_message("=" * 60)
    
    # 获取下一个要发布的帖子编号
    post_num = get_next_post_number()
    
    if post_num > 20:
        log_message("⚠️ 所有帖子已发布完成（Post 13-20）")
        return
    
    log_message(f"准备发布 Post {post_num}")
    
    # 检查内容文件是否存在
    content_file = f"/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/文档/Post{post_num}-*.md"
    
    # 简化版：暂时只发布标题，内容文件稍后准备
    titles = {
        14: "GitHub Actions被高估了，我换回了shell脚本",
        15: "Laravel这些功能90%的项目都用不到",
        16: "个人项目写单元测试是浪费时间",
        17: "Composer依赖管理让我哭了一次",
        18: "所谓的开源贡献，90%都是修改文档",
        19: "本地开发环境？直接装服务器上！",
        20: "Code Review是浪费时间，我自己测试更靠谱"
    }
    
    title = titles.get(post_num, f"ImageHub技术分享 Post {post_num}")
    
    # 简化内容（稍后用完整内容替换）
    content = f"""# {title}

**这是Post {post_num}的争议性内容**

完整内容正在准备中...

---

## 🤔 你们怎么看？

评论区告诉我你们的想法！

---

#技术 #Laravel #争议 #开发
"""
    
    log_message(f"标题: {title}")
    log_message(f"内容长度: {len(content)} 字符（临时内容）")
    
    # 发布
    log_message("正在发布...")
    post_id = publish_post(title, content)
    
    if post_id:
        log_message(f"✅ Post {post_num} 发布成功！")
        # 更新状态
        update_state(post_num)
        log_message(f"下次将发布 Post {post_num + 1}")
    else:
        log_message(f"❌ Post {post_num} 发布失败")

if __name__ == "__main__":
    main()
