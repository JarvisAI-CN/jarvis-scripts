#!/usr/bin/env python3
"""
任务列表转换器 - TODO.md → task_list.json
支持Markdown链接格式，智能任务分类
"""

from __future__ import annotations
import os
import sys
import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class TaskType(Enum):
    """任务类型"""
    BUGFIX = "bugfix"
    FEATURE = "feature"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    KNOWLEDGE = "knowledge"
    META = "meta"


class TaskPriority(Enum):
    """任务优先级"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ParsedTask:
    """解析的任务"""
    id: str
    title: str
    type: TaskType
    priority: TaskPriority
    description: str = ""
    projects: List[str] = field(default_factory=list)
    status: str = "pending"
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type.value,
            "priority": self.priority.value,
            "description": self.description,
            "projects": self.projects,
            "status": self.status,
            "metadata": self.metadata
        }


class TodoParser:
    """TODO.md解析器"""

    # 任务类型关键词映射
    TYPE_KEYWORDS = {
        TaskType.BUGFIX: ["修复", "bug", "fix", "问题"],
        TaskType.FEATURE: ["开发", "实现", "功能", "feature", "新增"],
        TaskType.MAINTENANCE: ["维护", "优化", "升级", "maintenance"],
        TaskType.MONITORING: ["监控", "检测", "巡检", "monitor"],
        TaskType.KNOWLEDGE: ["学习", "文档", "知识", "knowledge"],
        TaskType.META: ["元任务", "meta", "管理"]
    }

    # 优先级关键词映射
    PRIORITY_KEYWORDS = {
        TaskPriority.HIGH: ["紧急", "重要", "high", "urgent", "重要"],
        TaskPriority.MEDIUM: ["中等", "medium", "normal"],
        TaskPriority.LOW: ["低", "暂时", "low", "optional"]
    }

    def __init__(self, todo_path: str = "/home/ubuntu/.openclaw/workspace/TODO.md"):
        self.todo_path = Path(todo_path)
        self.tasks: List[ParsedTask] = []

    def parse(self) -> List[ParsedTask]:
        """解析TODO.md"""
        if not self.todo_path.exists():
            logger.error(f"TODO.md not found: {self.todo_path}")
            return []

        logger.info(f"解析 TODO.md: {self.todo_path}")

        content = self.todo_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        current_section = None
        task_counter = 1

        for i, line in enumerate(lines):
            # 检测章节标题
            if line.startswith('#'):
                current_section = self._parse_section(line)
                continue

            # 检测任务项
            if line.startswith('- [') or line.startswith('* ['):
                task = self._parse_task_item(line, current_section, task_counter)
                if task:
                    self.tasks.append(task)
                    task_counter += 1

        logger.info(f"解析到 {len(self.tasks)} 个任务")
        return self.tasks

    def _parse_section(self, line: str) -> str:
        """解析章节标题"""
        # 提取 # 后的文本
        match = re.match(r'^#+\s+(.+)$', line)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_task_item(
        self,
        line: str,
        section: str,
        counter: int
    ) -> Optional[ParsedTask]:
        """解析任务项"""
        try:
            # 提取状态和标题
            # 格式: - [ ] 任务标题 或 - [x] 已完成任务
            match = re.match(r'^[\-\*]\s+\[([ x])\]\s+(.+)$', line)
            if not match:
                return None

            status_char = match.group(1)
            title_line = match.group(2)

            # 检查是否已完成
            is_done = status_char == 'x'

            # 提取Markdown链接 [[link|title]] 或 [[link]]
            title, projects = self._extract_title_and_projects(title_line)

            # 生成任务ID
            task_id = self._generate_task_id(title, counter)

            # 检测任务类型
            task_type = self._detect_task_type(title)

            # 检测优先级
            priority = self._detect_priority(title)

            # 如果在第一象限，提升为高优先级
            if "第一象限" in section or "重要且紧急" in section:
                priority = TaskPriority.HIGH

            # 创建任务对象
            task = ParsedTask(
                id=task_id,
                title=title,
                type=task_type,
                priority=priority,
                description=f"来自章节: {section}" if section else "",
                projects=projects,
                status="done" if is_done else "pending"
            )

            logger.debug(f"解析任务: {task.id} - {task.title}")
            return task

        except Exception as e:
            logger.warning(f"解析任务行失败 ({i+1}): {e}")
            return None

    def _extract_title_and_projects(self, text: str) -> Tuple[str, List[str]]:
        """提取标题和项目链接"""
        title = text
        projects = []

        # 查找所有 [[link|title]] 或 [[link]] 格式
        pattern = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
        matches = re.findall(pattern, text)

        for link, display_text in matches:
            # 如果链接看起来像项目路径，添加到项目列表
            if 'Projects' in link or 'PARA' in link:
                project_name = display_text if display_text else link
                projects.append(project_name)

            # 从标题中移除Markdown链接
            title = re.sub(pattern, display_text if display_text else link, title, count=1)

        return title.strip(), projects

    def _detect_task_type(self, title: str) -> TaskType:
        """检测任务类型"""
        title_lower = title.lower()

        # 优先级: BUGFIX > FEATURE > MONITORING > MAINTENANCE > KNOWLEDGE > META
        if any(keyword in title_lower for keyword in self.TYPE_KEYWORDS[TaskType.BUGFIX]):
            return TaskType.BUGFIX
        elif any(keyword in title_lower for keyword in self.TYPE_KEYWORDS[TaskType.FEATURE]):
            return TaskType.FEATURE
        elif any(keyword in title_lower for keyword in self.TYPE_KEYWORDS[TaskType.MONITORING]):
            return TaskType.MONITORING
        elif any(keyword in title_lower for keyword in self.TYPE_KEYWORDS[TaskType.MAINTENANCE]):
            return TaskType.MAINTENANCE
        elif any(keyword in title_lower for keyword in self.TYPE_KEYWORDS[TaskType.KNOWLEDGE]):
            return TaskType.KNOWLEDGE
        else:
            return TaskType.META

    def _detect_priority(self, title: str) -> TaskPriority:
        """检测任务优先级"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in self.PRIORITY_KEYWORDS[TaskPriority.HIGH]):
            return TaskPriority.HIGH
        elif any(keyword in title_lower for keyword in self.PRIORITY_KEYWORDS[TaskPriority.LOW]):
            return TaskPriority.LOW
        else:
            return TaskPriority.MEDIUM

    def _generate_task_id(self, title: str, counter: int) -> str:
        """生成任务ID"""
        # 格式: TASK-YYYY-MM-DD-NNN
        today = datetime.now().strftime("%Y-%m-%d")
        # 使用标题的简短hash
        title_hash = hashlib.md5(title.encode()).hexdigest()[:3]
        return f"TASK-{today}-{counter:03d}-{title_hash}"


class TaskListManager:
    """任务列表管理器"""

    def __init__(self, task_list_path: str = "/home/ubuntu/.openclaw/workspace/.task_list.json"):
        self.task_list_path = Path(task_list_path)
        self.tasks: Dict[str, Dict] = {}

    def load_tasks(self):
        """加载任务列表"""
        if self.task_list_path.exists():
            try:
                with open(self.task_list_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = {
                        task["id"]: task
                        for task in data.get("tasks", [])
                    }
                logger.info(f"加载任务列表: {len(self.tasks)} 个任务")
            except Exception as e:
                logger.error(f"加载任务列表失败: {e}")
                self.tasks = {}
        else:
            logger.info("任务列表文件不存在，创建新的")
            self._save_tasks()

    def _save_tasks(self):
        """保存任务列表"""
        try:
            self.task_list_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": "2.0",
                "updated_at": datetime.now().isoformat(),
                "tasks": list(self.tasks.values())
            }
            with open(self.task_list_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("保存任务列表成功")
        except Exception as e:
            logger.error(f"保存任务列表失败: {e}")

    def add_task(self, task: ParsedTask):
        """添加或更新任务"""
        task_dict = task.to_dict()
        self.tasks[task.id] = task_dict
        logger.info(f"添加任务: {task.id} - {task.title}")

    def sync_from_todo(self, todo_path: str = "/home/ubuntu/.openclaw/workspace/TODO.md"):
        """从TODO.md同步任务"""
        parser = TodoParser(todo_path)
        parsed_tasks = parser.parse()

        added_count = 0
        updated_count = 0
        skipped_count = 0

        for task in parsed_tasks:
            if task.id in self.tasks:
                # 任务已存在，检查是否需要更新
                existing = self.tasks[task.id]
                if existing.get("status") != task.status:
                    # 更新状态
                    existing["status"] = task.status
                    existing["updated_at"] = datetime.now().isoformat()
                    updated_count += 1
                else:
                    skipped_count += 1
            else:
                # 新任务
                if task.status != "done":
                    self.add_task(task)
                    added_count += 1

        self._save_tasks()

        logger.info(f"同步完成: 添加 {added_count}, 更新 {updated_count}, 跳过 {skipped_count}")
        logger.info(f"当前任务总数: {len(self.tasks)}")

    def list_tasks(
        self,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict]:
        """列出任务"""
        tasks = list(self.tasks.values())

        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        if task_type:
            tasks = [t for t in tasks if t.get("type") == task_type]
        if priority:
            tasks = [t for t in tasks if t.get("priority") == priority]

        return sorted(tasks, key=lambda x: x.get("id", ""))

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取单个任务"""
        return self.tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        **kwargs
    ):
        """更新任务"""
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)
            self.tasks[task_id]["updated_at"] = datetime.now().isoformat()
            self._save_tasks()
            logger.info(f"更新任务: {task_id}")
            return True
        return False

    def delete_task(self, task_id: str) -> bool:
        """删除任务"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            logger.info(f"删除任务: {task_id}")
            return True
        return False

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        tasks = list(self.tasks.values()

        stats = {
            "total": len(tasks),
            "by_status": {},
            "by_type": {},
            "by_priority": {}
        }

        for task in tasks:
            # 按状态统计
            status = task.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            # 按类型统计
            task_type = task.get("type", "unknown")
            stats["by_type"][task_type] = stats["by_type"].get(task_type, 0) + 1

            # 按优先级统计
            priority = task.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

        return stats


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="TODO.md任务列表转换器")
    parser.add_argument(
        "command",
        choices=["sync", "list", "show", "update", "delete", "stats"],
        help="命令"
    )
    parser.add_argument(
        "--todo",
        default="/home/ubuntu/.openclaw/workspace/TODO.md",
        help="TODO.md文件路径"
    )
    parser.add_argument(
        "--tasklist",
        default="/home/ubuntu/.openclaw/workspace/.task_list.json",
        help="task_list.json文件路径"
    )
    parser.add_argument(
        "--task-id",
        help="任务ID"
    )
    parser.add_argument(
        "--status",
        help="筛选状态"
    )
    parser.add_argument(
        "--type",
        help="筛选类型"
    )
    parser.add_argument(
        "--priority",
        help="筛选优先级"
    )

    args = parser.parse_args()

    # 创建管理器
    manager = TaskListManager(args.tasklist)
    manager.load_tasks()

    # 执行命令
    if args.command == "sync":
        print("🔄 同步 TODO.md → task_list.json")
        manager.sync_from_todo(args.todo)
        print("✅ 同步完成")

    elif args.command == "list":
        tasks = manager.list_tasks(
            status=args.status,
            task_type=args.type,
            priority=args.priority
        )

        print(f"\n📋 任务列表 ({len(tasks)}):")
        for task in tasks:
            status_icon = "✅" if task.get("status") == "done" else "⏳"
            print(f"  {status_icon} [{task.get('id')}] {task.get('title')}")
            print(f"      类型: {task.get('type')} | 优先级: {task.get('priority')}")

    elif args.command == "show":
        if not args.task_id:
            print("❌ 请指定 --task-id")
            return

        task = manager.get_task(args.task_id)
        if not task:
            print(f"❌ 任务不存在: {args.task_id}")
            return

        print(f"\n📝 任务详情:")
        for key, value in task.items():
            print(f"  {key}: {value}")

    elif args.command == "stats":
        stats = manager.get_statistics()

        print(f"\n📊 任务统计:")
        print(f"  总计: {stats['total']}")
        print(f"\n  按状态:")
        for status, count in stats['by_status'].items():
            print(f"    {status}: {count}")
        print(f"\n  按类型:")
        for task_type, count in stats['by_type'].items():
            print(f"    {task_type}: {count}")
        print(f"\n  按优先级:")
        for priority, count in stats['by_priority'].items():
            print(f"    {priority}: {count}")

    else:
        print(f"❌ 未实现的命令: {args.command}")


if __name__ == "__main__":
    main()
