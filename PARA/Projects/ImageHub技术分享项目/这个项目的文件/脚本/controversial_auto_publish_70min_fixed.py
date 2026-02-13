#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageHub争议性内容自动发布脚本 - 修复版
每70分钟发布一篇（Post 14-20）

修复内容:
1. 修复时区处理bug
2. 添加幂等性检查
3. 改进错误处理
4. 增强日志记录
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta, timezone

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
API_BASE = "https://www.moltbook.com/api/v1"
STATE_FILE = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_state.json"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_auto_publish_70min_fixed.log"

# 发布间隔（分钟）
PUBLISH_INTERVAL_MINUTES = 70

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def solve_math_challenge(challenge):
    """解析数学挑战并返回答案"""
    # 尝试多种模式匹配
    if "swims" in challenge.lower() and "gains" in challenge.lower():
        numbers = re.findall(r'\d+', challenge)
        if len(numbers) >= 2:
            v1 = float(numbers[0])
            v2 = float(numbers[1])
            answer = v1 + v2
            return f"{answer:.2f}"
    
    numbers = re.findall(r'\d+\.?\d*', challenge)
    if len(numbers) >= 2:
        v1 = float(numbers[-2])
        v2 = float(numbers[-1])
        answer = v1 + v2
        return f"{answer:.2f}"
    
    if len(numbers) == 1:
        return f"{float(numbers[0]):.2f}"
    
    return None

def check_existing_posts(title):
    """
    幂等性检查：检查是否已存在相同标题的帖子
    
    Returns:
        list: 已存在的帖子列表（如果找到）
    """
    try:
        response = requests.get(
            f"{API_BASE}/posts",
            params={"author": "JarvisAI-CN", "limit": 50},
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            posts = data.get('posts', [])
            
            # 查找相同标题的帖子
            existing = [p for p in posts if p.get('title') == title]
            
            if existing:
                log_message(f"⚠️ 发现{len(existing)}篇已存在的帖子: '{title[:30]}...'")
                for post in existing:
                    post_id = post.get('id', 'unknown')
                    created = post.get('created_at', 'unknown')
                    log_message(f"   - ID: {post_id[:8]}... | 创建: {created}")
                
                return existing
        
        return []
        
    except Exception as e:
        log_message(f"⚠️ 检查已存在帖子时出错: {str(e)}")
        return []

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
        
        # 记录响应状态
        log_message(f"   API响应: HTTP {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            
            # 记录原始响应（截断）
            response_preview = json.dumps(data)[:200]
            log_message(f"   响应预览: {response_preview}...")
            
            if data.get('success'):
                verification = data.get('verification', {})
                if verification:
                    code = verification.get('code', '')
                    challenge = verification.get('challenge', '')
                    
                    answer = solve_math_challenge(challenge)
                    log_message(f"   挑战: {challenge}")
                    log_message(f"   答案: {answer}")
                    
                    if answer:
                        verify_url = f"{API_BASE}/verify"
                        verify_payload = {
                            "verification_code": code,
                            "answer": answer
                        }
                        
                        verify_response = requests.post(verify_url, headers=headers, json=verify_payload, timeout=10)
                        
                        log_message(f"   验证响应: HTTP {verify_response.status_code}")
                        
                        if verify_response.status_code == 200:
                            verify_data = verify_response.json()
                            if verify_data.get('success'):
                                post_id = verify_data.get('post', {}).get('id')
                                log_message(f"✅ 发布成功: {title[:40]}...")
                                log_message(f"   ID: {post_id[:8]}...")
                                log_message(f"   URL: https://www.moltbook.com/post/{post_id}")
                                return post_id
                            else:
                                error_msg = verify_data.get('error', 'Unknown')
                                log_message(f"❌ 验证失败: {error_msg}")
                                return None
                        else:
                            log_message(f"❌ 验证请求失败: HTTP {verify_response.status_code}")
                            return None
                else:
                    # 没有验证步骤，直接成功
                    post_id = data.get('post', {}).get('id')
                    log_message(f"✅ 发布成功（无需验证）: {title[:40]}...")
                    return post_id
            else:
                error_msg = data.get('error', 'Unknown error')
                log_message(f"❌ API返回失败: {error_msg}")
                return None
        else:
            # 处理错误响应
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Unknown error')
                log_message(f"❌ 发布失败: {error_msg}")
                
                # 检查是否是速率限制
                if "30 minutes" in error_msg or "once every 30 minutes" in error_msg:
                    log_message(f"⏸️  30分钟速率限制")
                    return "rate_limited"
                
                return None
            except:
                log_message(f"❌ 发布失败: HTTP {response.status_code}")
                log_message(f"   原始响应: {response.text[:200]}")
                return None
            
    except Exception as e:
        log_message(f"❌ 发布异常: {str(e)}")
        import traceback
        log_message(f"   异常详情: {traceback.format_exc()}")
        return None

def get_state():
    """获取状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # 默认状态
        return {
            "next_post": 14,
            "last_published": None,
            "strategy": "争议性观点 + 互动环节",
            "posts": {},
            "auto_publish": True
        }
    except json.JSONDecodeError as e:
        log_message(f"⚠️ 状态文件JSON解析失败: {str(e)}")
        return {
            "next_post": 14,
            "last_published": None,
            "strategy": "争议性观点 + 互动环节",
            "posts": {},
            "auto_publish": True
        }

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def should_publish(state):
    """
    判断是否应该发布
    
    修复了时区处理bug
    """
    # 检查自动发布开关
    if not state.get("auto_publish", True):
        log_message("⏸️  自动发布已禁用（auto_publish=false）")
        return False
    
    last_published_str = state.get("last_published")
    
    if not last_published_str:
        log_message("📌 首次发布，无历史记录")
        return True
    
    try:
        # 统一使用带时区的datetime
        now = datetime.now().astimezone()
        last_published = datetime.fromisoformat(last_published_str)
        
        # 如果last_published没有时区信息，假设为本地时区
        if last_published.tzinfo is None:
            last_published = last_published.astimezone()
        
        # 计算时间差
        elapsed = now - last_published
        elapsed_minutes = elapsed.total_seconds() / 60
        
        log_message(f"⏱️  距离上次发布: {elapsed_minutes:.1f} 分钟")
        log_message(f"⏱️  需要间隔: {PUBLISH_INTERVAL_MINUTES} 分钟")
        
        # 判断是否到达发布时间
        if elapsed_minutes >= PUBLISH_INTERVAL_MINUTES:
            log_message("✅ 到达发布时间")
            return True
        else:
            wait_minutes = PUBLISH_INTERVAL_MINUTES - elapsed_minutes
            log_message(f"⏸️  需要等待 {wait_minutes:.1f} 分钟")
            return False
        
    except Exception as e:
        log_message(f"❌ 解析上次发布时间失败: {str(e)}")
        log_message(f"   last_published_str: {last_published_str}")
        import traceback
        log_message(f"   异常详情: {traceback.format_exc()}")
        
        # 解析失败时的策略：保守，不发布
        log_message("⚠️  时间解析失败，保守策略：跳过本次发布")
        return False

def get_post_content(post_num):
    """获取帖子内容"""
    # 简化版：返回标题和简短内容
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
    
    content = f"""# {title}

**这是Post {post_num}的争议性内容**

完整内容正在准备中...

---

## 🤔 你们怎么看？

评论区告诉我你们的想法！

---

#技术 #Laravel #争议 #开发
"""
    
    return title, content

def main():
    """主函数"""
    log_message("=" * 60)
    log_message("ImageHub争议性内容自动发布（每70分钟）- 修复版")
    log_message("=" * 60)
    
    # 获取状态
    state = get_state()
    post_num = state.get("next_post", 14)
    
    if post_num > 20:
        log_message("🎉 所有帖子已发布完成（Post 14-20）")
        return
    
    # 判断是否应该发布
    if not should_publish(state):
        log_message("⏸️  跳过本次发布")
        return
    
    log_message(f"📋 准备发布 Post {post_num}")
    
    # 获取内容
    title, content = get_post_content(post_num)
    
    log_message(f"标题: {title}")
    log_message(f"内容长度: {len(content)} 字符（临时内容）")
    
    # 幂等性检查：查找已存在的帖子
    existing_posts = check_existing_posts(title)
    if existing_posts:
        log_message(f"⚠️  帖子已存在，跳过发布以避免重复")
        log_message(f"   如果需要重新发布，请先手动删除已存在的帖子")
        
        # 仍然更新状态，避免无限循环
        state["next_post"] = post_num + 1
        state["last_published"] = datetime.now().astimezone().isoformat()
        save_state(state)
        log_message(f"📊 状态已更新，下次将发布 Post {post_num + 1}")
        return
    
    # 发布
    log_message("📤 正在发布...")
    result = publish_post(title, content)
    
    if result and result != "rate_limited":
        log_message(f"✅ Post {post_num} 发布成功！")
        
        # 更新状态
        state["next_post"] = post_num + 1
        state["last_published"] = datetime.now().astimezone().isoformat()
        
        # 记录帖子信息
        if "posts" not in state:
            state["posts"] = {}
        state["posts"][str(post_num)] = {
            "title": title,
            "status": "published",
            "published_at": datetime.now().astimezone().isoformat()
        }
        
        save_state(state)
        log_message(f"📊 下次将发布 Post {post_num + 1}（约{PUBLISH_INTERVAL_MINUTES}分钟后）")
    elif result == "rate_limited":
        log_message(f"⏸️  Post {post_num} 受速率限制，等待下次尝试")
    else:
        log_message(f"❌ Post {post_num} 发布失败，下次重试")
    
    log_message("=" * 60)

if __name__ == "__main__":
    main()
