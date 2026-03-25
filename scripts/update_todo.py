#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO列表更新器
更新TODO.md的时间戳并同步到task_list.json
"""

import sys
from pathlib import Path
from datetime import datetime

# 添加scripts目录到Python路径
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

# 导入todo_to_tasklist模块
from todo_to_tasklist import TaskListGenerator, TASK_LIST_FILE, TODO_FILE


def update_todo_timestamp():
    """更新TODO.md的时间戳"""
    if not TODO_FILE.exists():
        print(f"❌ TODO.md不存在: {TODO_FILE}")
        return False

    # 读取文件内容
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 更新时间戳
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S GMT+8")
    updated_content = content.replace(
        f"**更新时间**: ",
        f"**更新时间**: {now}\n"
    )

    # 如果时间戳行存在，替换它
    import re
    timestamp_pattern = r'\*\*更新时间\*\*[:\s].+?GMT\+8'
    if re.search(timestamp_pattern, content):
        updated_content = re.sub(
            timestamp_pattern,
            f"**更新时间**: {now} GMT+8",
            content
        )
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"✅ 更新时间戳: {now}")
        return True
    else:
        print(f"⚠️ 未找到时间戳行，跳过更新")
        return False


def sync_to_tasklist():
    """同步TODO.md到task_list.json"""
    print("\n📋 开始同步任务列表...")
    generator = TaskListGenerator(TASK_LIST_FILE)
    generator.sync_from_todo()


def main():
    """主函数"""
    print("=" * 60)
    print("TODO列表更新器")
    print("=" * 60)
    print()

    # 步骤1: 更新时间戳
    update_todo_timestamp()

    # 步骤2: 同步到task_list.json
    sync_to_tasklist()

    print()
    print("=" * 60)
    print("✅ TODO列表更新完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
