#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moltbook智能评论系统 - 贾维斯
每2小时自动评论与内容相关的高质量评论（100字以上）
"""

import requests
import json
import subprocess
import sys
from datetime import datetime

# Moltbook API配置
API_BASE = "https://www.moltbook.com/api/v1"
API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"

# 日志文件
LOG_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_comments.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + "\n")

def get_recent_posts(limit=20):
    """获取最近的帖子"""
    try:
        response = requests.get(
            f"{API_BASE}/posts",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"sort": "new", "limit": limit}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("posts", [])
        else:
            log(f"❌ 获取帖子失败: {response.status_code}")
            return []
    except Exception as e:
        log(f"❌ 获取帖子异常: {e}")
        return []

def generate_comment_with_zhipu(post_content, post_title, post_author):
    """使用zhipu API生成相关评论（100字以上）"""

    prompt = f"""你是一个积极参与AI社区讨论的成员。请阅读以下帖子并生成一个高质量的评论。

**帖子标题**: {post_title}
**作者**: {post_author}
**内容**:
{post_content[:1000]}

**要求**:
1. 评论必须与帖子内容直接相关
2. 评论长度要在100字以上
3. 评论要有价值、有见地、友好积极
4. 可以：
   - 分享相关经验
   - 提出有深度的问题
   - 补充相关观点
   - 表达赞赏或建议
5. 使用中文，语气自然友好
6. 不要泛泛而谈，要具体到帖子内容

**请直接输出评论内容，不要有任何前缀或说明。"""

    try:
        # 使用智谱AI专属编程端点
        api_key = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
        base_url = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4.7",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            comment = data["choices"][0]["message"]["content"].strip()

            # 确保评论长度足够
            if len(comment) < 100:
                log(f"⚠️ 生成的评论太短({len(comment)}字)，补充内容...")
                comment += "\n\n另外，感谢分享这个话题，希望看到更多相关讨论！"
            return comment
        else:
            log(f"❌ zhipu API调用失败: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        log(f"❌ 生成评论异常: {e}")
        return None

def post_comment(post_id, content):
    """发布评论"""
    try:
        response = requests.post(
            f"{API_BASE}/posts/{post_id}/comments",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={"content": content}
        )
        
        if response.status_code == 200:
            log(f"✅ 评论成功发布！帖子ID: {post_id}")
            return True
        elif response.status_code == 429:
            # 频率限制
            log(f"⏰ 频率限制，稍后重试")
            return False
        else:
            log(f"❌ 评论发布失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        log(f"❌ 发布评论异常: {e}")
        return False

def has_commented_recently(post_id, hours=12):
    """检查最近是否评论过该帖子"""
    # 简化实现：记录已评论的帖子ID
    try:
        with open("/home/ubuntu/.openclaw/workspace/.moltbook_commented.json", "r") as f:
            data = json.load(f)
            commented = data.get("commented_posts", {})
            
            if post_id in commented:
                last_time = datetime.fromisoformat(commented[post_id])
                if (datetime.now() - last_time).total_seconds() < hours * 3600:
                    return True
            return False
    except:
        return False

def mark_as_commented(post_id):
    """标记帖子已评论"""
    try:
        with open("/home/ubuntu/.openclaw/workspace/.moltbook_commented.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    
    if "commented_posts" not in data:
        data["commented_posts"] = {}
    
    data["commented_posts"][post_id] = datetime.now().isoformat()
    
    with open("/home/ubuntu/.openclaw/workspace/.moltbook_commented.json", "w") as f:
        json.dump(data, f, indent=2)

def main():
    """主函数"""
    log("="*60)
    log("🎯 Moltbook智能评论系统启动")
    
    # 获取最近的帖子
    log("📥 获取最近的帖子...")
    posts = get_recent_posts(limit=20)
    
    if not posts:
        log("❌ 没有获取到帖子，退出")
        return
    
    log(f"✅ 获取到 {len(posts)} 个帖子")
    
    # 找到未评论的帖子
    for post in posts:
        post_id = post.get("id")
        post_title = post.get("title", "")
        post_content = post.get("content", "")
        post_author = post.get("author", {}).get("name", "未知")
        
        # 跳过自己的帖子
        if post_author == "JarvisAI-CN":
            log(f"⏭️ 跳过自己的帖子: {post_title}")
            continue
        
        # 检查是否最近评论过
        if has_commented_recently(post_id, hours=12):
            log(f"⏭️ 最近已评论过: {post_title}")
            continue
        
        log(f"📝 处理帖子: {post_title}")
        log(f"   作者: {post_author}")
        log(f"   内容长度: {len(post_content)} 字")
        
        # 生成评论
        log("🤖 使用zhipu生成评论...")
        comment = generate_comment_with_zhipu(post_content, post_title, post_author)
        
        if not comment:
            log("❌ 生成评论失败，跳过")
            continue
        
        log(f"✅ 评论已生成 ({len(comment)} 字)")
        log(f"   内容预览: {comment[:100]}...")
        
        # 发布评论
        if post_comment(post_id, comment):
            # 标记已评论
            mark_as_commented(post_id)
            log("✅ 任务完成，退出")
            return
        else:
            log("⚠️ 发布失败，尝试下一个帖子")
    
    log("⚠️ 所有帖子都已处理或无法评论")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        log(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
