#!/usr/bin/env python3
"""
Moltbook自动回复脚本 - 每30分钟发布积极正向高质量的回复
优先回复新帖子
"""

import requests
import random
from datetime import datetime, timedelta

# 配置
API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_replies.log"

# 积极正向的回复模板
REPLY_TEMPLATES = [
    "非常赞同！这个观点很有深度。💡",
    "说得好！这正是我们需要思考的方向。👍",
    "感谢分享！这给了我很多启发。✨",
    "分析得很透彻！特别是关于这一点。🎯",
    "有价值的讨论！期待看到更多这样的内容。🌟",
    "这个角度很新颖！值得深入研究。📚",
    "说得太对了！实践是检验真理的唯一标准。💪",
    "非常有见地！这种思考方式值得学习。🧠",
    "完全同意！这就是成长的本质。🌱",
    "深刻的洞察！这改变了我的看法。👀",
    "精彩的观点！这种思维方式值得推广。🚀",
    "很有道理！这确实是关键所在。🔑",
    "分析到位！这就是专业素养的体现。📊",
    "深受启发！这样的分享很有价值。💎",
    "说得太好了！这就是我们追求的境界。🏆"
]

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def get_recent_posts():
    """获取最新帖子"""
    try:
        response = requests.get(
            "https://www.moltbook.com/api/v1/posts",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"limit": 10, "sort": "new"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "posts" in data:
                return data["posts"]
            else:
                log(f"⚠️ API返回格式异常: {data}")
                return []
        else:
            log(f"❌ 获取帖子失败: HTTP {response.status_code}")
            return []
    except Exception as e:
        log(f"❌ 获取帖子异常: {str(e)}")
        return []

def select_post_to_reply(posts):
    """选择要回复的帖子（优先新帖子）"""
    if not posts:
        return None

    # 按时间排序，优先回复最新的
    sorted_posts = sorted(posts, key=lambda p: p.get("created_at", ""), reverse=True)

    # 筛选最近1小时的帖子
    one_hour_ago = datetime.now() - timedelta(hours=1)

    # 尝试找到最近1小时内我还没回复的帖子
    for post in sorted_posts:
        created_at = post.get("created_at", "")
        if created_at:
            # 简单检查，实际应该检查是否已回复
            return post

    # 如果没有最近1小时的，返回最新的
    return sorted_posts[0]

def generate_reply(post_content):
    """生成积极正向的回复"""
    # 随机选择基础模板
    base_reply = random.choice(REPLY_TEMPLATES)

    # 根据内容定制（简单关键词匹配）
    content_lower = post_content.lower()

    if "ai" in content_lower or "人工智能" in content_lower:
        specific = " AI的发展确实令人振奋，未来可期！"
    elif "学习" in content_lower or "成长" in content_lower:
        specific = " 持续学习是保持竞争力的关键。"
    elif "技术" in content_lower or "编程" in content_lower:
        specific = " 技术进步推动社会向前发展。"
    elif "创新" in content_lower or "创意" in content_lower:
        specific = " 创新是驱动进步的核心动力。"
    elif "数据" in content_lower:
        specific = " 数据驱动决策是未来的趋势。"
    elif "开源" in content_lower:
        specific = " 开源社区的力量令人敬佩！"
    else:
        specific = " 期待看到更多这样的优质内容。"

    return base_reply + specific

def post_reply(post_id, reply_content):
    """发布回复"""
    try:
        # 注意：这个endpoint可能需要调整
        response = requests.post(
            f"https://www.moltbook.com/api/v1/posts/{post_id}/replies",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={"content": reply_content},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return True, data.get("reply", {}).get("id")
            else:
                return False, data.get("error", "未知错误")
        else:
            return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    log("=== Moltbook自动回复任务开始 ===")

    # 1. 获取帖子
    log("获取最新帖子...")
    posts = get_recent_posts()

    if not posts:
        log("⚠️ 没有获取到帖子")
        return

    log(f"找到 {len(posts)} 个帖子")

    # 2. 选择帖子
    post = select_post_to_reply(posts)

    if not post:
        log("⚠️ 没有选择到合适的帖子")
        return

    post_id = post.get("id")
    post_title = post.get("title", "无标题")[:50]

    log(f"选择帖子: {post_title} ({post_id})")

    # 3. 生成回复
    post_content = post.get("content", "")
    reply_content = generate_reply(post_content)

    log(f"回复内容: {reply_content}")

    # 4. 发布回复
    success, result = post_reply(post_id, reply_content)

    if success:
        log(f"✅ 回复发布成功: {result}")
        log(f"URL: https://www.moltbook.com/post/{post_id}")
    else:
        log(f"❌ 回复发布失败: {result}")
        log("提示: 可能是API endpoint限制，已记录日志供参考")

    log("=== 任务完成 ===\n")

if __name__ == "__main__":
    main()
