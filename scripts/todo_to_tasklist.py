#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO.md 解析器 → task_list.json 转换器
将人类可读的 TODO.md 转换为机器可执行的 task_list.json
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# 配置
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
TODO_FILE = WORKSPACE / "TODO.md"
TASK_LIST_FILE = WORKSPACE / ".task_list.json"


class Todoparser:
    """TODO.md 解析器"""

    def __init__(self, todo_file: Path):
        self.todo_file = todo_file

    def parse(self) -> List[Dict]:
        """解析 TODO.md，提取任务列表"""
        if not self.todo_file.exists():
            print(f"警告: TODO.md 文件不存在: {self.todo_file}")
            return []

        tasks = []
        current_quadrant = None
        current_section = None

        with open(self.todo_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            # 检测象限
            if "第一象限" in line and "重要且紧急" in line:
                current_quadrant = "urgent_important"
                current_section = "active"
            elif "第二象限" in line and "紧急但不重要" in line:
                current_quadrant = "urgent_not_important"
                current_section = "active"
            elif "第三象限" in line and "重要但不紧急" in line:
                current_quadrant = "not_urgent_important"
                current_section = "active"
            elif "第四象限" in line and "不重要且不紧急" in line:
                current_quadrant = "not_urgent_not_important"
                current_section = "active"
            elif "已完成任务" in line or "✅ 已完成任务" in line:
                current_section = "completed"
                continue

            # 解析任务 - 支持多种格式
            # 格式1: [[链接|标题]]
            link_match = re.match(r'^\[\[.+?\|(.+?)\]\]', line.strip())
            if link_match:
                title = link_match.group(1)

                # 提取任务元数据
                metadata = self._extract_metadata_from_section(title, lines)

                # 判断任务类型
                task_type = self._classify_task(title)

                # 判断优先级
                priority = self._get_priority(current_quadrant)

                # 跳过已完成的任务（在已完成任务部分中）
                if current_section == "completed":
                    continue

                # 构建任务对象
                task = {
                    "title": title,
                    "description": metadata.get("description", ""),
                    "source": str(self.todo_file),
                    "type": task_type,
                    "priority": priority,
                    "quadrant": current_quadrant,
                    "status": "pending",
                    "metadata": metadata
                }

                tasks.append(task)

            # 格式2: 纯文本标题（以 #### 开头）
            header_match = re.match(r'^####\s+(.+?)\s*$', line.strip())
            if header_match:
                title = header_match.group(1)

                # 提取任务元数据
                metadata = self._extract_metadata_from_section(title, lines)

                # 判断任务类型
                task_type = self._classify_task(title)

                # 判断优先级
                priority = self._get_priority(current_quadrant)

                # 跳过已完成的任务
                if current_section == "completed":
                    continue

                # 构建任务对象
                task = {
                    "title": title,
                    "description": metadata.get("description", ""),
                    "source": str(self.todo_file),
                    "type": task_type,
                    "priority": priority,
                    "quadrant": current_quadrant,
                    "status": "pending",
                    "metadata": metadata
                }

                tasks.append(task)

        return tasks

    def _extract_metadata_from_section(self, title: str, all_lines: List[str]) -> Dict:
        """从任务所在的部分提取元数据"""
        metadata = {}
        in_target_section = False

        for i, line in enumerate(all_lines):
            # 找到标题所在行
            if title in line and ("[[" in line or "####" in line):
                # 检查接下来的几行，提取元数据
                for j in range(i+1, min(i+10, len(all_lines))):
                    next_line = all_lines[j]

                    # 检查状态
                    if "🚀 启动" in next_line or "启动" in next_line:
                        metadata["status"] = "starting"
                    elif "🔄 进行中" in next_line:
                        metadata["status"] = "in_progress"
                    elif "⏸️ 暂停" in next_line:
                        metadata["status"] = "paused"
                    elif "**状态**" in next_line:
                        status_match = re.search(r'\*\*状态\*\*[:\s]+(.+)', next_line)
                        if status_match:
                            metadata["status"] = status_match.group(1).strip()

                    # 检查进度
                    if "**进度**" in next_line:
                        progress_match = re.search(r'\*\*进度\*\*[:\s]+(\d+)%', next_line)
                        if progress_match:
                            metadata["progress"] = int(progress_match.group(1))

                    # 检查任务数量
                    if "**任务**" in next_line:
                        tasks_match = re.search(r'\*\*任务\*\*[:\s]+(\d+)', next_line)
                        if tasks_match:
                            metadata["task_count"] = int(tasks_match.group(1))

                    # 检查目标时间
                    if "**目标时间**" in next_line:
                        time_match = re.search(r'\*\*目标时间\*\*[:\s]+([\d-]+\s+[\d:]+)', next_line)
                        if time_match:
                            metadata["target_date"] = time_match.group(1)

                    # 检查描述
                    if "**任务**" in next_line or "**描述**" in next_line:
                        desc_match = re.search(r'\*\*(?:任务|描述)\*\*[:\s]+(.+)', next_line)
                        if desc_match:
                            metadata["description"] = desc_match.group(1).strip()

                    # 遇到下一个标题或分隔符，停止提取
                    if next_line.strip().startswith("---") or next_line.strip().startswith("## "):
                        break

                break

        return metadata
        """从任务行提取元数据"""
        metadata = {}

        # 检查是否有进度条
        progress_match = re.search(r'进度[:\s]+(\d+)%', line)
        if progress_match:
            metadata["progress"] = int(progress_match.group(1))

        # 检查是否有状态标签
        if "🚀 启动" in line:
            metadata["status"] = "starting"
        elif "🔄 进行中" in line:
            metadata["status"] = "in_progress"
        elif "⏸️ 暂停" in line:
            metadata["status"] = "paused"

        # 检查是否有目标时间
        time_match = re.search(r'目标时间[:\s]+([\d-]+)', line)
        if time_match:
            metadata["target_date"] = time_match.group(1)

        return metadata

    def _classify_task(self, title: str) -> str:
        """根据标题判断任务类型"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ["修复", "bug", "问题", "异常"]):
            return "bugfix"
        elif any(keyword in title_lower for keyword in ["优化", "重构", "改进"]):
            return "refactor"
        elif any(keyword in title_lower for keyword in ["测试", "验证"]):
            return "testing"
        elif any(keyword in title_lower for keyword in ["维护", "监控", "检查"]):
            return "maintenance"
        else:
            return "feature"

    def _get_priority(self, quadrant: str) -> str:
        """根据象限确定优先级"""
        priority_map = {
            "urgent_important": "high",
            "urgent_not_important": "medium",
            "not_urgent_important": "medium",
            "not_urgent_not_important": "low"
        }
        return priority_map.get(quadrant, "medium")


class TaskListGenerator:
    """task_list.json 生成器"""

    def __init__(self, task_list_file: Path):
        self.task_list_file = task_list_file
        self.data = self._load_or_create()

    def _load_or_create(self) -> Dict:
        """加载或创建任务列表"""
        if self.task_list_file.exists():
            with open(self.task_list_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "version": "2.0",
                "last_updated": datetime.now().isoformat(),
                "statistics": {
                    "total": 0,
                    "pending": 0,
                    "in_progress": 0,
                    "done": 0,
                    "failed": 0
                },
                "tasks": []
            }

    def _save(self):
        """保存任务列表"""
        self.data["last_updated"] = datetime.now().isoformat()

        # 更新统计
        stats = {
            "total": len(self.data["tasks"]),
            "pending": 0,
            "in_progress": 0,
            "done": 0,
            "failed": 0
        }

        for task in self.data["tasks"]:
            status = task["status"]
            if status in stats:
                stats[status] += 1

        self.data["statistics"] = stats

        # 保存到文件
        with open(self.task_list_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_tasks(self, new_tasks: List[Dict]):
        """添加新任务（去重）"""
        added_count = 0

        for new_task in new_tasks:
            # 检查是否已存在（根据标题）
            exists = any(
                t["title"] == new_task["title"]
                for t in self.data["tasks"]
            )

            if not exists:
                # 生成任务 ID
                date_str = datetime.now().strftime("%Y-%m-%d")
                counter = len(self.data["tasks"]) + 1
                task_id = f"TASK-{date_str}-{counter:03d}"

                # 添加完整任务对象
                task = {
                    "id": task_id,
                    "created_at": datetime.now().isoformat(),
                    "assigned_to": "GLM-4.7",
                    "subtasks": [],
                    "logs": [],
                    **new_task
                }

                self.data["tasks"].append(task)
                added_count += 1
                print(f"✅ 添加任务: {task_id} - {new_task['title']}")
            else:
                print(f"⏭️  跳过重复任务: {new_task['title']}")

        if added_count > 0:
            self._save()
            print(f"\n✅ 总共添加 {added_count} 个任务")
        else:
            print("\n⏭️  没有新任务需要添加")

    def sync_from_todo(self):
        """从 TODO.md 同步任务"""
        print("📋 从 TODO.md 解析任务...")

        # 解析 TODO.md
        parser = Todoparser(TODO_FILE)
        tasks = parser.parse()

        print(f"✅ 解析到 {len(tasks)} 个待处理任务")

        # 添加到 task_list.json
        self.add_tasks(tasks)

        # 打印统计
        print(f"\n📊 当前任务统计:")
        stats = self.data["statistics"]
        print(f"   总计: {stats['total']}")
        print(f"   待处理: {stats['pending']}")
        print(f"   进行中: {stats['in_progress']}")
        print(f"   已完成: {stats['done']}")
        print(f"   失败: {stats['failed']}")


def main():
    """主函数"""
    import sys

    print("=" * 60)
    print("TODO.md → task_list.json 转换器")
    print("=" * 60)
    print()

    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "sync":
            # 从 TODO.md 同步
            generator = TaskListGenerator(TASK_LIST_FILE)
            generator.sync_from_todo()
        elif command == "stats":
            # 显示统计信息
            generator = TaskListGenerator(TASK_LIST_FILE)
            stats = generator.data["statistics"]
            print(f"📊 任务统计:")
            print(f"   总计: {stats['total']}")
            print(f"   待处理: {stats['pending']}")
            print(f"   进行中: {stats['in_progress']}")
            print(f"   已完成: {stats['done']}")
            print(f"   失败: {stats['failed']}")
        elif command == "list":
            # 列出所有任务
            generator = TaskListGenerator(TASK_LIST_FILE)
            tasks = generator.data["tasks"]

            if not tasks:
                print("📝 任务列表为空")
            else:
                print(f"📝 所有任务 ({len(tasks)}):")
                print()

                for task in tasks:
                    status_emoji = {
                        "pending": "⏳",
                        "in_progress": "🔄",
                        "done": "✅",
                        "failed": "❌",
                        "cancelled": "⏸️"
                    }.get(task["status"], "❓")

                    print(f"{status_emoji} [{task['id']}] {task['title']}")
                    print(f"   类型: {task['type']} | 优先级: {task['priority']} | 状态: {task['status']}")

                    if task.get("description"):
                        print(f"   描述: {task['description']}")

                    print()
        else:
            print(f"未知命令: {command}")
            print("用法: python todo_to_tasklist.py [sync|stats|list]")
            sys.exit(1)
    else:
        # 默认执行同步
        generator = TaskListGenerator(TASK_LIST_FILE)
        generator.sync_from_todo()


if __name__ == "__main__":
    main()
