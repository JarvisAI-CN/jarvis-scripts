#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复任务类型识别逻辑

问题：TASK-2026-02-13-001失败原因是：
- execute_task()检查task['type']
- 但它调用_execute_generic_task()，而_generic_task通过关键词检测
- 任务标题是"自主编程项目-第二轮"，不包含"实现/开发/添加"等关键词
- 所以返回False，任务被标记为failed

解决方案：
1. 优先检查type字段（最可靠）
2. 改进关键词检测逻辑
"""

def test_type_detection():
    """测试任务类型检测"""
    test_cases = [
        {
            "id": "TASK-2026-02-13-001",
            "title": "自主编程项目-第二轮",
            "description": "核心功能100%完成，增强功能开发中",
            "type": "feature",
            "expected": "feature"
        },
        {
            "id": "TASK-2026-02-13-009",
            "title": "修复 WebDAV 写权限异常",
            "description": "修复123盘写入问题",
            "type": "bugfix",
            "expected": "bugfix"
        },
        {
            "id": "TASK-2026-02-13-006",
            "title": "自动化监控",
            "description": "",
            "type": "maintenance",
            "expected": "maintenance"
        }
    ]

    for case in test_cases:
        detected = detect_task_type(case)
        status = "✅" if detected == case["expected"] else "❌"
        print(f"{status} {case['id']}: {detected} (expected: {case['expected']})")

def detect_task_type(task):
    """改进的任务类型检测"""
    # 优先检查type字段（最可靠）
    task_type = task.get("type", "").lower()

    type_mapping = {
        "bugfix": "bugfix",
        "feature": "feature",
        "refactor": "feature",
        "testing": "testing",
        "maintenance": "maintenance"
    }

    if task_type in type_mapping:
        return type_mapping[task_type]

    # 备用：关键词检测
    description = task.get("description", "").lower()
    title = task.get("title", "").lower()

    # Bugfix关键词（扩展）
    bugfix_keywords = [
        "修复", "fix", "bug", "错误", "error", "异常", "exception",
        "解决", "solve", "diagnosis", "诊断", "排查"
    ]

    # Feature关键词（扩展）
    feature_keywords = [
        "实现", "implement", "添加", "add", "新功能", "new feature",
        "开发", "develop", "创建", "create", "功能", "function"
    ]

    # Maintenance关键词
    maintenance_keywords = [
        "优化", "optimize", "维护", "maintain", "监控", "monitor",
        "检查", "check", "更新", "update"
    ]

    # 检测优先级：bugfix > feature > maintenance
    for keyword in bugfix_keywords:
        if keyword in description or keyword in title:
            return "bugfix"

    for keyword in feature_keywords:
        if keyword in description or keyword in title:
            return "feature"

    for keyword in maintenance_keywords:
        if keyword in description or keyword in title:
            return "maintenance"

    # 默认返回feature（因为主任务是功能开发）
    return "feature"

if __name__ == "__main__":
    print("测试改进的任务类型检测逻辑：\n")
    test_type_detection()
