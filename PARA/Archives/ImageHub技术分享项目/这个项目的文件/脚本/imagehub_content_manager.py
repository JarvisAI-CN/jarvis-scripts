#!/usr/bin/env python3
"""
ImageHub自动化内容管理系统 v2.0
功能：完整的内容生命周期管理（创建→发布→验证→质量检查→清理）
版本：v2.0
创建：2026-02-14
"""

import requests
import json
import time
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from difflib import SequenceMatcher
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MoltbookAPI:
    """Moltbook API封装类"""

    def __init__(self, api_key: str, base_url: str = "https://www.moltbook.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取用户信息失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None

    def get_user_posts(self, username: str = "JarvisAI-CN", limit: int = 50) -> List[Dict]:
        """获取用户的帖子列表"""
        try:
            user_info = self.get_user_info(username)
            if not user_info:
                return []

            user_id = user_info.get("id")
            if not user_id:
                logger.error("无法获取用户ID")
                return []

            url = f"{self.base_url}/users/{user_id}/posts"
            params = {"limit": limit}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get("posts", [])
            else:
                logger.error(f"获取帖子列表失败: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取帖子列表异常: {e}")
            return []

    def get_post(self, post_id: str) -> Optional[Dict]:
        """获取单个帖子详情"""
        try:
            url = f"{self.base_url}/posts/{post_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取帖子失败: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"获取帖子异常: {e}")
            return None

    def create_post(self, title: str, content: str, submolt: str = "general") -> Optional[str]:
        """创建帖子"""
        try:
            url = f"{self.base_url}/posts"
            payload = {
                "title": title,
                "content": content,
                "submolt": submolt
            }

            response = requests.post(url, headers=self.headers, json=payload, timeout=30)

            if response.status_code == 201:
                data = response.json()
                post_id = data.get("post", {}).get("id")
                logger.info(f"创建帖子成功: {title[:50]}... (ID: {post_id})")
                return post_id
            else:
                logger.error(f"创建帖子失败: HTTP {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"创建帖子异常: {e}")
            return None

    def verify_challenge(self, verification_code: str, answer: str) -> bool:
        """验证数学挑战"""
        try:
            url = f"{self.base_url}/verify"
            payload = {
                "verification_code": verification_code,
                "answer": answer
            }
            response = requests.post(url, headers=self.headers, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"验证挑战异常: {e}")
            return False

    def delete_post(self, post_id: str) -> bool:
        """删除帖子"""
        try:
            url = f"{self.base_url}/posts/{post_id}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"删除帖子成功: {post_id}")
                return True
            else:
                logger.error(f"删除帖子失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"删除帖子异常: {e}")
            return False


class ContentQualityChecker:
    """内容质量检查器"""

    def __init__(self, min_length: int = 200, max_similarity: float = 0.9):
        self.min_length = min_length
        self.max_similarity = max_similarity

    def check_length(self, content: str) -> Tuple[bool, str]:
        """检查内容长度"""
        if len(content) < self.min_length:
            return False, f"内容过短：{len(content)}字符（要求至少{self.min_length}字符）"
        return True, "长度检查通过"

    def check_placeholder(self, content: str) -> Tuple[bool, str]:
        """检查占位符"""
        placeholders = ["待准备", "待补充", "TBD", "TODO", "..."]
        for ph in placeholders:
            if ph in content:
                return False, f"包含占位符: {ph}"
        return True, "占位符检查通过"

    def check_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        return SequenceMatcher(None, text1, text2).ratio()

    def get_content_hash(self, content: str) -> str:
        """获取内容的哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def check_quality(self, title: str, content: str) -> Dict[str, Any]:
        """综合质量检查"""
        results = {
            "title": title,
            "passed": True,
            "issues": [],
            "score": 0
        }

        # 检查标题
        if len(title) < 10:
            results["issues"].append("标题过短")
            results["passed"] = False
        if len(title) > 100:
            results["issues"].append("标题过长")
            results["passed"] = False

        # 检查内容长度
        length_ok, length_msg = self.check_length(content)
        if not length_ok:
            results["issues"].append(length_msg)
            results["passed"] = False
        else:
            results["score"] += 20

        # 检查占位符
        placeholder_ok, placeholder_msg = self.check_placeholder(content)
        if not placeholder_ok:
            results["issues"].append(placeholder_msg)
            results["passed"] = False
        else:
            results["score"] += 20

        # 检查内容结构（是否有标题、段落）
        if "##" in content or "###" in content:
            results["score"] += 20

        # 检查代码块
        if "```" in content:
            results["score"] += 20

        # 检查链接
        if "http" in content:
            results["score"] += 20

        return results


class DuplicateDetector:
    """重复内容检测器"""

    def __init__(self, api: MoltbookAPI):
        self.api = api
        self.posts_cache: List[Dict] = []
        self.content_map: Dict[str, str] = {}  # hash -> post_id

    def load_posts(self, username: str = "JarvisAI-CN", limit: int = 50):
        """加载用户的帖子"""
        logger.info(f"加载帖子列表: {username}（最多{limit}篇）")
        self.posts_cache = self.api.get_user_posts(username, limit)
        logger.info(f"加载了 {len(self.posts_cache)} 篇帖子")

        # 构建内容哈希映射
        self.content_map = {}
        for post in self.posts_cache:
            content = post.get("content", "")
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            self.content_map[content_hash] = post.get("id")

        logger.info(f"构建了 {len(self.content_map)} 个内容哈希")

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """查找重复内容"""
        duplicates = []
        seen_hashes = {}

        for post in self.posts_cache:
            post_id = post.get("id")
            content = post.get("content", "")
            title = post.get("title", "")
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

            if content_hash in seen_hashes:
                duplicates.append({
                    "post_id": post_id,
                    "original_id": seen_hashes[content_hash],
                    "title": title,
                    "content_length": len(content),
                    "duplicate_type": "exact_match"
                })
                logger.warning(f"发现重复: {post_id} == {seen_hashes[content_hash]}")
            else:
                seen_hashes[content_hash] = post_id

        return duplicates

    def find_similar_content(self, threshold: float = 0.95) -> List[Dict[str, Any]]:
        """查找相似内容（使用相似度算法）"""
        similar_pairs = []

        for i, post1 in enumerate(self.posts_cache):
            for post2 in self.posts_cache[i+1:]:
                content1 = post1.get("content", "")
                content2 = post2.get("content", "")
                title1 = post1.get("title", "")
                title2 = post2.get("title", "")

                similarity = SequenceMatcher(None, content1, content2).ratio()

                if similarity >= threshold:
                    similar_pairs.append({
                        "post1_id": post1.get("id"),
                        "post2_id": post2.get("id"),
                        "post1_title": title1,
                        "post2_title": title2,
                        "similarity": round(similarity * 100, 2),
                        "similarity_type": "high_similarity"
                    })
                    logger.warning(f"发现相似内容: {post1.get('id')} vs {post2.get('id')} ({similarity*100:.1f}%)")

        return similar_pairs

    def generate_report(self) -> Dict[str, Any]:
        """生成重复检测报告"""
        duplicates = self.find_duplicates()
        similar = self.find_similar_content()

        return {
            "total_posts": len(self.posts_cache),
            "exact_duplicates": len(duplicates),
            "similar_content": len(similar),
            "duplicate_details": duplicates,
            "similar_details": similar,
            "timestamp": datetime.now().isoformat()
        }


class ContentManager:
    """内容管理器 - 统一管理内容生命周期"""

    def __init__(self, api_key: str):
        self.api = MoltbookAPI(api_key)
        self.quality_checker = ContentQualityChecker()
        self.duplicate_detector = DuplicateDetector(self.api)
        self.state_file = Path("/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/content_manager_state.json")

    def load_state(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
                return {}
        return {}

    def save_state(self, state: Dict):
        """保存状态"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def scan_and_clean(self, dry_run: bool = False) -> Dict[str, Any]:
        """扫描并清理重复内容"""
        logger.info("开始扫描重复内容...")

        # 加载帖子
        self.duplicate_detector.load_posts()

        # 生成报告
        report = self.duplicate_detector.generate_report()

        # 清理重复内容
        deleted_posts = []
        for duplicate in report["duplicate_details"]:
            post_id = duplicate["post_id"]
            original_id = duplicate["original_id"]

            logger.warning(f"发现重复: {post_id} (原始: {original_id})")

            if not dry_run:
                if self.api.delete_post(post_id):
                    deleted_posts.append(post_id)
                else:
                    logger.error(f"删除失败: {post_id}")
            else:
                logger.info(f"[DRY RUN] 将删除: {post_id}")

        report["deleted_posts"] = deleted_posts
        report["dry_run"] = dry_run

        return report

    def create_and_verify_post(
        self,
        title: str,
        content: str,
        submolt: str = "general",
        verify: bool = True
    ) -> Optional[Dict]:
        """创建并验证帖子"""
        logger.info(f"创建帖子: {title[:50]}...")

        # 质量检查
        quality_result = self.quality_checker.check_quality(title, content)

        if not quality_result["passed"]:
            logger.error(f"质量检查失败: {quality_result['issues']}")
            return None

        logger.info(f"质量检查通过: {quality_result['score']}/100")

        # 创建帖子
        post_id = self.api.create_post(title, content, submolt)

        if not post_id:
            logger.error("创建帖子失败")
            return None

        # 验证帖子
        if verify:
            time.sleep(5)  # 等待API更新

            post = self.api.get_post(post_id)
            if not post:
                logger.error(f"验证失败: 无法获取帖子 {post_id}")
                return None

            logger.info(f"验证成功: {post_id}")

            return {
                "post_id": post_id,
                "title": title,
                "content_length": len(content),
                "quality_score": quality_result["score"],
                "verified": True
            }

        return {"post_id": post_id}


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="ImageHub自动化内容管理系统v2.0")
    parser.add_argument("command", choices=["scan", "clean", "check", "report"], help="命令")
    parser.add_argument("--dry-run", action="store_true", help="干运行（不实际删除）")
    parser.add_argument("--threshold", type=float, default=0.95, help="相似度阈值（0-1）")
    parser.add_argument("--post-id", help="帖子ID（用于check命令）")

    args = parser.parse_args()

    # API密钥（从PASSWORDS.md获取）
    api_key = "moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"

    # 创建管理器
    manager = ContentManager(api_key)

    if args.command == "scan":
        # 扫描重复内容
        report = manager.scan_and_clean(dry_run=True)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == "clean":
        # 清理重复内容
        report = manager.scan_and_clean(dry_run=args.dry_run)
        print(json.dumps(report, indent=2, ensure_ascii=False))

    elif args.command == "check":
        # 检查单个帖子质量
        if not args.post_id:
            print("错误: --post-id 参数必需")
            return

        post = manager.api.get_post(args.post_id)
        if not post:
            print(f"错误: 无法获取帖子 {args.post_id}")
            return

        quality = manager.quality_checker.check_quality(
            post.get("title", ""),
            post.get("content", "")
        )

        print(f"帖子质量检查结果: {args.post_id}")
        print(json.dumps(quality, indent=2, ensure_ascii=False))

    elif args.command == "report":
        # 生成完整报告
        manager.duplicate_detector.load_posts()
        report = manager.duplicate_detector.generate_report()

        print(f"\n📊 ImageHub内容管理报告")
        print(f"=" * 50)
        print(f"总帖子数: {report['total_posts']}")
        print(f"完全重复: {report['exact_duplicates']}")
        print(f"高度相似: {report['similar_content']}")
        print(f"生成时间: {report['timestamp']}")


if __name__ == "__main__":
    main()
