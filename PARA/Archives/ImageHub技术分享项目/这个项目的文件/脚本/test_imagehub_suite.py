#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageHub技术分享自动化测试套件
单元测试、集成测试、端到端测试
"""

import asyncio
import pytest
from pathlib import Path
import sys

# 导入被测试模块
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/脚本')

from imagehub_content_manager import ImageHubContentManager
from imagehub_quality_checker import ImageHubQualityChecker


class TestImageHubContentManager:
    """内容管理器测试"""

    @pytest.fixture
    def manager(self):
        """创建内容管理器实例"""
        return ImageHubContentManager()

    def test_initialization(self, manager):
        """测试初始化"""
        assert manager.posts is not None
        assert len(manager.posts) == 4
        assert 17 in manager.posts
        assert 20 in manager.posts

    def test_get_post(self, manager):
        """测试获取文章"""
        post = manager.get_post(17)
        assert post is not None
        assert "title" in post
        assert "content" in post
        assert "tags" in post
        assert "Composer" in post["title"]

    def test_get_nonexistent_post(self, manager):
        """测试获取不存在的文章"""
        post = manager.get_post(99)
        assert post is None

    def test_get_post_hash(self, manager):
        """测试内容哈希"""
        hash1 = manager.get_post_hash(17)
        hash2 = manager.get_post_hash(18)

        assert hash1 != hash2
        assert len(hash1) == 32  # MD5哈希长度

    def test_validate_post(self, manager):
        """测试文章验证"""
        is_valid, msg = manager.validate_post(17)

        # Post 17内容完整，应该通过
        assert is_valid
        assert "验证通过" in msg or msg == ""

    def test_get_all_posts(self, manager):
        """测试获取所有文章"""
        all_posts = manager.get_all_posts()

        assert len(all_posts) == 4
        for num in [17, 18, 19, 20]:
            assert str(num) in all_posts or num in all_posts


class TestImageHubQualityChecker:
    """质量检查器测试"""

    @pytest.fixture
    def checker(self):
        """创建质量检查器实例"""
        manager = ImageHubContentManager()
        return ImageHubQualityChecker(manager)

    def test_initialization(self, checker):
        """测试初始化"""
        assert checker.quality_rules is not None
        assert "min_length" in checker.quality_rules
        assert checker.quality_rules["min_length"] == 500

    def test_calculate_hash(self, checker):
        """测试哈希计算"""
        content1 = "Hello World"
        content2 = "hello world"  # 小写

        hash1 = checker.calculate_hash(content1)
        hash2 = checker.calculate_hash(content2)

        # 标准化后应该相同
        assert hash1 == hash2

    def test_check_length_valid(self, checker):
        """测试长度检查 - 有效内容"""
        long_content = "x" * 1000
        valid, msg = checker.check_length(long_content, 17)

        assert valid
        assert "✅" in msg

    def test_check_length_invalid(self, checker):
        """测试长度检查 - 无效内容"""
        short_content = "x" * 100
        valid, msg = checker.check_length(short_content, 17)

        assert not valid
        assert "❌" in msg

    def test_check_placeholders_valid(self, checker):
        """测试占位符检查 - 有效内容"""
        clean_content = "这是一篇正常的技术文章，没有占位符。"
        valid, issues = checker.check_placeholders(clean_content, 17)

        assert valid
        assert len(issues) == 0

    def test_check_placeholders_invalid(self, checker):
        """测试占位符检查 - 无效内容"""
        todo_content = "这里是TODO待补充内容"
        valid, issues = checker.check_placeholders(todo_content, 17)

        assert not valid
        assert len(issues) > 0

    def test_check_structure_valid(self, checker):
        """测试结构检查 - 有效内容"""
        structured_content = """
# 标题

## 副标题

内容部分

```python
code here
```

更多内容
        """
        valid, issues = checker.check_structure(structured_content, 17)

        assert valid
        assert len(issues) == 0

    def test_check_engagement_valid(self, checker):
        """测试互动检查 - 有效内容"""
        engagement_content = """
# 标题

内容...

## 互动

评论区告诉我！👇
        """
        valid, msg = checker.check_engagement(engagement_content, 17)

        assert valid
        assert "✅" in msg

    def test_check_engagement_invalid(self, checker):
        """测试互动检查 - 无效内容"""
        no_engagement_content = """
# 标题

内容...

结束。
        """
        valid, msg = checker.check_engagement(no_engagement_content, 17)

        assert not valid
        assert "⚠️" in msg

    def test_validate_post(self, checker):
        """测试完整文章验证"""
        result = checker.validate_post(17)

        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "post_num" in result

    def test_validate_all_posts(self, checker):
        """测试批量验证"""
        results = checker.validate_all_posts([17, 18, 19, 20])

        assert "total" in results
        assert "valid" in results
        assert "invalid" in results
        assert results["total"] == 4

    def test_generate_report(self, checker):
        """测试报告生成"""
        results = checker.validate_all_posts([17, 18])
        report = checker.generate_report(results)

        assert "质量报告" in report
        assert "✅" in report or "❌" in report
        assert "总文章数" in report


class TestImageHubIntegration:
    """集成测试"""

    @pytest.fixture
    def manager(self):
        return ImageHubContentManager()

    @pytest.fixture
    def checker(self, manager):
        return ImageHubQualityChecker(manager)

    def test_full_workflow(self, checker):
        """测试完整工作流"""
        # 1. 获取所有文章
        all_posts = checker.content_manager.get_all_posts()
        assert len(all_posts) == 4

        # 2. 验证所有文章
        results = checker.validate_all_posts()
        assert results["total"] == 4

        # 3. 生成报告
        report = checker.generate_report(results)
        assert "质量报告" in report

        # 4. 保存报告
        report_file = checker.save_report(results)
        assert Path(report_file).exists()

    def test_duplicate_detection(self, checker):
        """测试重复检测"""
        # 创建重复内容
        duplicate_content = "这是重复内容" * 100

        # 检测应该发现重复
        all_posts = {
            17: {"content": duplicate_content},
            18: {"content": duplicate_content},
            19: {"content": "其他内容"}
        }

        valid, duplicates = checker.check_duplicates(all_posts, 17)
        assert not valid
        assert len(duplicates) > 0

    def test_export_to_dict(self, manager):
        """测试导出功能"""
        manager_dict = manager.to_dict()

        assert isinstance(manager_dict, dict)
        assert "17" in manager_dict or 17 in manager_dict


class TestImageHubEdgeCases:
    """边界情况测试"""

    def test_empty_content(self):
        """测试空内容"""
        manager = ImageHubContentManager()
        checker = ImageHubQualityChecker(manager)

        result = checker.validate_post(17, content="")

        assert not result["valid"]
        assert any("为空" in e for e in result["errors"])

    def test_very_long_content(self):
        """测试超长内容"""
        manager = ImageHubContentManager()
        checker = ImageHubQualityChecker(manager)

        long_content = "x" * 100000  # 100KB
        valid, msg = checker.check_length(long_content, 17)

        assert not valid
        assert "过长" in msg

    def test_special_characters(self):
        """测试特殊字符"""
        manager = ImageHubContentManager()
        checker = ImageHubQualityChecker(manager)

        special_content = """
# 标题

内容包含：中文、English、日本語、한국어

特殊符号：!@#$%^&*()_+-=[]{}|;':",./<>?

```python
code = "test"
```
        """
        valid, issues = checker.check_structure(special_content, 17)
        assert valid


# pytest运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
