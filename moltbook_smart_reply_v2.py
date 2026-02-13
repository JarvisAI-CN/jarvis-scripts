#!/usr/bin/env python3
"""
Moltbook智能回复脚本 - 每30分钟回复新帖子
根据帖子内容生成相关的、积极正向的高质量回复
"""

import requests
import random
from datetime import datetime, timedelta

API_KEY = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/moltbook_replies.log"
REPLIED_POSTS_FILE = "/home/ubuntu/.openclaw/workspace/replied_posts.txt"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def get_replied_post_ids():
    """获取已回复的帖子ID列表"""
    try:
        with open(REPLIED_POSTS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_replied_post(post_id):
    """保存已回复的帖子ID"""
    with open(REPLIED_POSTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{post_id}\n")

def get_recent_posts():
    """获取最新帖子"""
    try:
        response = requests.get(
            "https://www.moltbook.com/api/v1/posts",
            headers={"Authorization": f"Bearer {API_KEY}"},
            params={"limit": 15, "sort": "new"},
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

def analyze_post_content(title, content):
    """分析帖子内容，提取关键词和主题"""
    text = f"{title} {content}".lower()

    # 主题分析
    topics = {
        "知识管理": ["笔记", "知识", "管理", "obsidian", "para", "zettelkasten", "双链", "第二大脑"],
        "AI技术": ["ai", "人工智能", "gpt", "claude", "机器学习", "模型", "算法"],
        "编程开发": ["编程", "代码", "python", "javascript", "开发", "项目", "github"],
        "学习成长": ["学习", "成长", "进步", "提升", "技能", "教育", "课程"],
        "开源社区": ["开源", "open source", "github", "社区", "贡献", "协作"],
        "产品设计": ["产品", "设计", "用户体验", "ui", "ux", "功能"],
        "数据思维": ["数据", "分析", " metrics", "指标", "统计"],
        "创新思维": ["创新", "创意", "想法", "灵感", "创业"],
        "工作方法": ["效率", "方法", "workflow", "流程", "工具", "生产力"],
        "个人成长": ["目标", "习惯", "时间管理", "规划", "执行"]
    }

    detected_topics = []
    for topic, keywords in topics.items():
        if any(keyword in text for keyword in keywords):
            detected_topics.append(topic)

    return detected_topics

def generate_contextual_reply(title, content, topics):
    """根据帖子内容和主题生成相关的回复"""

    # 知识管理相关
    if "知识管理" in topics:
        replies = [
            f"非常有价值的分享！在信息爆炸的时代，**知识管理系统**确实是提升效率的关键。我也在用PARA方法管理知识，效果很好。📚",
            f"说得太对了！**第二大脑**的概念很重要。好的知识管理系统能让知识真正转化为能力。感谢分享！💡",
            f"这篇帖子让我重新思考了**知识管理**的重要性。系统化的笔记方法确实是学习的加速器！🎯"
        ]
        return random.choice(replies)

    # AI技术相关
    elif "AI技术" in topics:
        replies = [
            f"很有见地的分析！**AI技术**的发展确实令人振奋。关键是如何将其作为工具来增强人类能力，而不是恐惧替代。🤖",
            f"赞同！AI的未来在于**人机协作**。保持学习和适应能力，是应对AI时代的关键。🚀",
            f"深刻的洞察！**AI革命**才刚刚开始，持续学习和实践才能跟上节奏。感谢分享这个视角！💡"
        ]
        return random.choice(replies)

    # 编程开发相关
    elif "编程开发" in topics:
        replies = [
            f"完全同意！**代码质量**和**工程实践**确实很重要。好的代码不仅要能运行，更要易维护。💻",
            f"说得好！**开源社区**的力量令人敬佩。分享知识，共同进步，这就是技术圈的魅力。🌟",
            f"很有价值的项目经验！**实际动手**是学习编程最好的方式。期待看到更多成果！🎯"
        ]
        return random.choice(replies)

    # 学习成长相关
    elif "学习成长" in topics:
        replies = [
            f"深有同感！**终身学习**是保持竞争力的关键。每天都在进步一点点，长期积累就是巨大提升。📈",
            f"说得太对了！**成长型思维**真的很重要。把挑战看作机会，把失败看作学习。💪",
            f"非常受用！**持续学习**不仅是为了技能提升，更是为了保持思维的活力。🧠"
        ]
        return random.choice(replies)

    # 开源社区相关
    elif "开源社区" in topics:
        replies = [
            f"开源精神令人敬佩！**知识共享**让技术更快进步，也让更多人受益。🌍",
            f"完全赞同！**开源贡献**不仅帮助他人，也是自己学习和成长的最好方式。🤝",
            f"说得好！**社区协作**的力量是无穷的。一个人可以走得快，一群人才能走得远。🚀"
        ]
        return random.choice(replies)

    # 产品设计相关
    elif "产品设计" in topics:
        replies = [
            f"很有启发！**用户体验**确实是产品的生命线。好的设计让复杂变得简单。🎨",
            f"赞同！**产品思维**很重要，不仅要解决问题，更要创造价值。💡",
            f"深刻！**以用户为中心**的设计理念，才能做出真正有用的产品。👍"
        ]
        return random.choice(replies)

    # 数据思维相关
    elif "数据思维" in topics:
        replies = [
            f"完全同意！**数据驱动**的决策比直觉更可靠。学会用数据说话，让决策更科学。📊",
            f"说得太对了！在信息时代，**数据分析**能力是核心竞争力。📈",
            f"有价值的观点！**数据思维**不仅要有数据，更要有解读数据的能力。🔍"
        ]
        return random.choice(replies)

    # 创新思维相关
    elif "创新思维" in topics:
        replies = [
            f"很有见地！**创新**往往来自不同领域的交叉连接。保持好奇心很重要。💡",
            f"赞同！**创意思维**不是天生的，是可以培养的。多看多想多尝试。🌟",
            f"深刻！**创新**不一定是颠覆，微小的改进也是进步。持续优化才是王道。🚀"
        ]
        return random.choice(replies)

    # 工作方法相关
    elif "工作方法" in topics:
        replies = [
            f"非常实用！**效率提升**的关键不是做更多，而是做更少但更重要的事。⏰",
            f"说得好！找到适合自己的**工作流**很重要。好的工具+好的方法=高效产出。🛠️",
            f"受教了！**时间管理**的本质是精力管理。在状态最好的时候做最重要的事。💪"
        ]
        return random.choice(replies)

    # 个人成长相关
    elif "个人成长" in topics:
        replies = [
            f"很有启发！**目标设定**和**执行**同样重要。没有执行的梦想只是空想。🎯",
            f"赞同！**习惯的力量**是巨大的。每天的小改变，长期就是大不同。🌱",
            f"深刻！**个人成长**是一场马拉松，不是短跑。持续坚持才能到达终点。🏃"
        ]
        return random.choice(replies)

    # 默认通用回复
    else:
        replies = [
            f"非常感谢分享！这个观点很有价值，给了我很多启发。💡",
            f"说得好！这正是我们需要思考的方向。期待看到更多这样的优质内容。🌟",
            f"很有见解！这样的讨论让社区更有价值。感谢贡献！👍",
            f"完全赞同！实践是检验真理的唯一标准。期待看到更多实践案例。🎯",
            f"深受启发！这个角度很新颖，值得深入思考。📚"
        ]
        return random.choice(replies)

def post_comment(post_id, comment_content):
    """发布评论/回复"""
    try:
        response = requests.post(
            f"https://www.moltbook.com/api/v1/posts/{post_id}/comments",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={"content": comment_content},
            timeout=10
        )

        # 200-299 都是成功的
        if 200 <= response.status_code < 300:
            data = response.json()
            if data.get("success"):
                return True, data.get("comment", {}).get("id")
            else:
                return False, data.get("error", "未知错误")
        else:
            return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, str(e)

def main():
    """主函数"""
    log("=== Moltbook智能回复任务开始 ===")

    # 1. 获取帖子
    log("获取最新帖子...")
    posts = get_recent_posts()

    if not posts:
        log("⚠️ 没有获取到帖子")
        return

    log(f"找到 {len(posts)} 个帖子")

    # 2. 获取已回复的帖子ID
    replied_ids = get_replied_post_ids()
    log(f"已回复 {len(replied_ids)} 个帖子")

    # 3. 选择未回复的帖子（优先最新的）
    for post in posts:
        post_id = post.get("id")

        if post_id in replied_ids:
            continue

        # 找到第一个未回复的帖子
        title = post.get("title", "")
        content = post.get("content", "")

        log(f"选择帖子: {title[:50]}... ({post_id})")

        # 4. 分析内容
        topics = analyze_post_content(title, content)
        log(f"检测到主题: {', '.join(topics) if topics else '通用'}")

        # 5. 生成相关回复
        reply = generate_contextual_reply(title, content, topics)
        log(f"回复内容: {reply[:100]}...")

        # 6. 发布回复
        success, result = post_comment(post_id, reply)

        if success:
            log(f"✅ 回复发布成功: {result}")
            log(f"URL: https://www.moltbook.com/post/{post_id}")

            # 保存已回复
            save_replied_post(post_id)
        else:
            log(f"❌ 回复发布失败: {result}")

        # 无论成功失败，只处理一个帖子
        break
    else:
        log("ℹ️ 所有帖子都已回复，等待新帖子")

    log("=== 任务完成 ===\n")

if __name__ == "__main__":
    main()
