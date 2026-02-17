#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageHub技术分享质量保证系统
发布前验证、发布后检查、重复检测
"""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import json


class ImageHubQualityChecker:
    """ImageHub技术分享质量检查器"""

    def __init__(self, content_manager=None):
        self.content_manager = content_manager
        self.quality_rules = self._init_quality_rules()
        self.quality_log = []

    def _init_quality_rules(self) -> Dict:
        """初始化质量规则"""
        return {
            "min_length": 500,  # 最小字符数
            "max_length": 50000,  # 最大字符数
            "required_sections": [
                "##",  # 至少有一个二级标题
                "#",   # 必须有一级标题
            ],
            "forbidden_patterns": [
                r"待补充",
                r"TODO",
                r"\[待添加\]",
                r"内容准备中",
                r"WIP",
            ],
            "required_elements": [
                r"#+ ",      # 标题
                r"```",      # 代码块
                r"#{1,3} ",  # 标题层级
            ],
            "engagement_elements": [
                "互动",
                "评论区",
                "👇",
                "💬",
            ]
        }

    def log_check(self, level: str, message: str):
        """记录质量检查日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.quality_log.append(log_entry)

    def calculate_hash(self, content: str) -> str:
        """计算内容哈希值（用于重复检测）"""
        # 标准化：移除空白字符、统一大小写
        normalized = re.sub(r'\s+', '', content.lower())
        return hashlib.md5(normalized.encode()).hexdigest()

    def check_length(self, content: str, post_num: int) -> Tuple[bool, str]:
        """检查内容长度"""
        length = len(content)

        if length < self.quality_rules["min_length"]:
            msg = f"❌ 内容过短：{length} < {self.quality_rules['min_length']}"
            self.log_check("ERROR", f"Post {post_num}: {msg}")
            return False, msg

        if length > self.quality_rules["max_length"]:
            msg = f"⚠️ 内容过长：{length} > {self.quality_rules['max_length']}"
            self.log_check("WARNING", f"Post {post_num}: {msg}")
            return True, msg

        msg = f"✅ 长度合格：{length} 字符"
        self.log_check("INFO", f"Post {post_num}: {msg}")
        return True, msg

    def check_placeholders(self, content: str, post_num: int) -> Tuple[bool, List[str]]:
        """检查占位符和TODO"""
        issues = []

        for pattern in self.quality_rules["forbidden_patterns"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(f"发现占位符: {pattern}")

        if issues:
            msg = f"❌ 发现{len(issues)}个占位符"
            self.log_check("ERROR", f"Post {post_num}: {msg}")
            return False, issues

        msg = "✅ 无占位符"
        self.log_check("INFO", f"Post {post_num}: {msg}")
        return True, []

    def check_structure(self, content: str, post_num: int) -> Tuple[bool, List[str]]:
        """检查文章结构"""
        issues = []

        # 检查必需元素
        for element in self.quality_rules["required_elements"]:
            if not re.search(element, content):
                issues.append(f"缺少必需元素: {element}")

        # 检查标题层级
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        if len(headings) < 3:
            issues.append("标题层级过少（<3个）")

        # 检查代码块
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        if len(code_blocks) < 2:
            issues.append("代码块过少（<2个）")

        if issues:
            msg = f"⚠️ 结构问题: {len(issues)}个"
            self.log_check("WARNING", f"Post {post_num}: {msg}")
            return False, issues

        msg = "✅ 结构合格"
        self.log_check("INFO", f"Post {post_num}: {msg}")
        return True, []

    def check_engagement(self, content: str, post_num: int) -> Tuple[bool, str]:
        """检查互动元素"""
        has_engagement = any(
            elem in content
            for elem in self.quality_rules["engagement_elements"]
        )

        if not has_engagement:
            msg = "⚠️ 缺少互动环节"
            self.log_check("WARNING", f"Post {post_num}: {msg}")
            return False, msg

        msg = "✅ 包含互动环节"
        self.log_check("INFO", f"Post {post_num}: {msg}")
        return True, msg

    def check_duplicates(
        self,
        all_posts: Dict[int, Dict],
        post_num: int
    ) -> Tuple[bool, List[str]]:
        """检查内容重复"""
        duplicates = []
        current_post = all_posts.get(post_num, {})
        current_hash = self.calculate_hash(current_post.get("content", ""))

        for num, post in all_posts.items():
            if num == post_num:
                continue

            post_hash = self.calculate_hash(post.get("content", ""))

            if current_hash == post_hash:
                duplicates.append(f"Post {num}")

        if duplicates:
            msg = f"❌ 发现重复: {', '.join(duplicates)}"
            self.log_check("ERROR", f"Post {post_num}: {msg}")
            return False, duplicates

        msg = "✅ 无重复"
        self.log_check("INFO", f"Post {post_num}: {msg}")
        return True, []

    def validate_post(
        self,
        post_num: int,
        content: str = None,
        title: str = None,
        all_posts: Dict = None
    ) -> Dict:
        """全面验证单篇文章"""
        result = {
            "post_num": post_num,
            "valid": True,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }

        # 获取内容
        if self.content_manager and not content:
            post_data = self.content_manager.get_post(post_num)
            if not post_data:
                result["valid"] = False
                result["errors"].append("文章内容未找到")
                return result
            content = post_data["content"]
            title = post_data["title"]

        if not content:
            result["valid"] = False
            result["errors"].append("内容为空")
            return result

        # 获取所有文章（用于重复检测）
        if not all_posts and self.content_manager:
            all_posts = self.content_manager.get_all_posts()

        # 执行检查
        checks = {
            "length": self.check_length(content, post_num),
            "placeholders": self.check_placeholders(content, post_num),
            "structure": self.check_structure(content, post_num),
            "engagement": self.check_engagement(content, post_num),
        }

        # 添加重复检查
        if all_posts:
            checks["duplicates"] = self.check_duplicates(all_posts, post_num)

        # 汇总结果
        for check_name, (passed, info) in checks.items():
            if not passed:
                result["valid"] = False

                if check_name in ["length", "duplicates", "placeholders"]:
                    result["errors"].append(str(info))
                else:
                    result["warnings"].append(str(info))

        return result

    def validate_all_posts(self, post_nums: List[int] = None) -> Dict:
        """验证多篇文章"""
        if not post_nums:
            post_nums = [17, 18, 19, 20]

        if not self.content_manager:
            return {
                "error": "需要配置content_manager"
            }

        all_posts = self.content_manager.get_all_posts()

        results = {
            "total": len(post_nums),
            "valid": 0,
            "invalid": 0,
            "posts": {}
        }

        for post_num in post_nums:
            result = self.validate_post(post_num, all_posts=all_posts)
            results["posts"][str(post_num)] = result

            if result["valid"]:
                results["valid"] += 1
            else:
                results["invalid"] += 1

        results["success_rate"] = (
            results["valid"] / results["total"] * 100
            if results["total"] > 0 else 0
        )

        return results

    def generate_report(self, results: Dict) -> str:
        """生成质量报告"""
        lines = [
            "",
            "=" * 60,
            "📋 ImageHub技术分享质量报告",
            "=" * 60,
            f"总文章数: {results.get('total', 0)}",
            f"✅ 通过: {results.get('valid', 0)}",
            f"❌ 失败: {results.get('invalid', 0)}",
            f"成功率: {results.get('success_rate', 0):.1f}%",
            "=" * 60,
        ]

        for post_num, result in results.get("posts", {}).items():
            status = "✅" if result["valid"] else "❌"
            title = result.get("title", f"Post {post_num}")

            lines.append(f"\n{status} {title}")

            if result["errors"]:
                for error in result["errors"]:
                    lines.append(f"   ❌ {error}")

            if result["warnings"]:
                for warning in result["warnings"]:
                    lines.append(f"   ⚠️ {warning}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)

    def save_report(
        self,
        results: Dict,
        output_file: str = None
    ) -> str:
        """保存质量报告"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/quality_report_{timestamp}.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return str(output_path)


# 示例使用
if __name__ == "__main__":
    # 导入内容管理器
    import sys
    sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/脚本')
    from imagehub_content_manager import ImageHubContentManager

    # 创建检查器
    content_manager = ImageHubContentManager()
    checker = ImageHubQualityChecker(content_manager)

    # 验证所有文章
    print("🔍 开始质量检查...\n")

    results = checker.validate_all_posts([17, 18, 19, 20])

    # 生成报告
    report = checker.generate_report(results)
    print(report)

    # 保存报告
    report_file = checker.save_report(results)
    print(f"\n📄 报告已保存: {report_file}")
