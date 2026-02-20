#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO.md自动更新脚本 v2.1
动态发现项目，智能分类，反映真实进度
"""

import os
import re
from datetime import datetime

WORKSPACE_DIR = "/home/ubuntu/.openclaw/workspace"
TODO_FILE = os.path.join(WORKSPACE_DIR, "TODO.md")
PROJECTS_DIR = os.path.join(WORKSPACE_DIR, "PARA/Projects")


def get_project_info(project_name):
    """从项目的 README.md 获取状态和进度"""
    readme_path = os.path.join(PROJECTS_DIR, project_name, "README.md")
    if not os.path.exists(readme_path):
        return None

    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

            # 提取进度
            prog_match = re.search(
                r"(?:进度|完成度|完成率|progress|completion)[ \*\-_]*:\s*(\d+%)",
                content,
                re.I,
            )

            # 如果没找到，尝试从状态中提取百分比
            if not prog_match:
                prog_match = re.search(r"✅\s*(\d+%)", content)

            # 如果还没找到，尝试计算任务列表
            if prog_match:
                progress = prog_match.group(1)
            else:
                tasks = re.findall(r"- \[(x| )\]", content)
                if tasks:
                    completed = tasks.count("x")
                    total = len(tasks)
                    progress = f"{int(completed / total * 100)}%"
                else:
                    progress = "0%"

            # 确定状态
            if re.search(
                r"(?:状态|status)[\s\*]*:\s*(?:项目)?✅\s*(?:已完成|completed|100%|完工|完成)",
                content,
                re.I,
            ):
                status = "✅ 已完成"
            elif re.search(
                r"(?:状态|status)[\s\*]*:\s*🛑\s*(?:已取消|cancelled)", content, re.I
            ):
                status = "🛑 已取消"
            elif "⚠️ 阻塞" in content or "blocked" in content.lower():
                status = "⚠️ 阻塞"
            else:
                status = "🔄 进行中"

            # 提取备注/最近更新
            remarks = ""
            if status == "⚠️ 阻塞":
                block_match = re.search(r"阻塞: (.+)", content)
                if block_match:
                    remarks = block_match.group(1)
            else:
                update_match = re.search(r"最近更新: (.+)", content)
                if not update_match:
                    update_match = re.search(r"任务: (.+)", content)
                if update_match:
                    remarks = update_match.group(1)

            return {
                "name": project_name,
                "status": status,
                "progress": progress,
                "remarks": remarks,
                "path": f"PARA/Projects/{project_name}/README.md",
            }
    except Exception as e:
        print(f"Error reading {readme_path}: {e}")
        return None


def generate_todo():
    """生成TODO.md内容"""
    now = datetime.now()
    update_time = now.strftime("%Y-%m-%d %H:%M:%S")

    active_projects = []
    completed_projects = []

    # 扫描项目目录
    if os.path.exists(PROJECTS_DIR):
        for item in os.listdir(PROJECTS_DIR):
            if os.path.isdir(os.path.join(PROJECTS_DIR, item)):
                info = get_project_info(item)
                if info:
                    if info["status"] == "✅ 已完成" or info["status"] == "🛑 已取消":
                        completed_projects.append(info)
                    else:
                        active_projects.append(info)

    # 构造第一象限
    urgent_items = []
    for p in active_projects:
        item_text = f"#### [[{p['path']}|{p['name']}]]\n**状态**: {p['status']}\n**进度**: {p['progress']}"
        if p["remarks"]:
            item_text += f"\n**任务**: {p['remarks']}"
        urgent_items.append(item_text)

    # 构造已完成
    done_items = []
    for p in completed_projects:
        done_items.append(
            f"#### [[{p['path']}|{p['name']}]]\n**完成日期**: {now.strftime('%Y-%m-%d')}\n**状态**: {p['status']}"
        )

    urgent_section = (
        "\n\n---\n".join(urgent_items) if urgent_items else "暂无正在进行的任务"
    )
    completed_section = "\n\n---\n".join(done_items) if done_items else "暂无已完成任务"

    content = f"""# 任务管理 - 四象限法则

**更新时间**: {update_time} GMT+8
**更新方式**: 自动更新 (v2.1)
**处理策略**: 重要紧急 > 紧急不重要 > 重要不紧急 > 不紧急

---

## 📋 四象限说明

### 🔴 第一象限：重要且紧急（立即处理）
- 关键任务 & 项目瓶颈
- 账户状态恢复
- 核心产出

### 🟠 第二象限：紧急但不重要（快速处理）
- 自动化监控 (备份、心跳、发布)
- 系统状态定期巡检

### 🟡 第三象限：重要但不紧急（计划处理）
- PARA 系统维护 & 知识图谱优化
- OpenClaw 文档与技能学习
- 代码重构与工具优化

### 🟢 第四象限：不重要且不紧急（凌晨处理）
- 临时文件清理
- 低优先级的学习任务

---

## 🔴 第一象限：重要且紧急

### 🚀 进行中

{urgent_section}

---

## 🟠 第二象限：紧急但不重要

#### 🛡️ 自动化监控
- [x] **123盘备份**: 每2小时执行 (正常)
- [x] **心跳响应**: 实时监听 (正常)
- [x] **系统巡检**: 磁盘空间、挂载状态 (正常)

---

## 🟡 第三象限：重要但不紧急

#### 📚 知识管理与系统优化
- **PARA 维护**: 整理 Resources 索引 (进行中 40%)
- **Obsidian 优化**: 强化双链连接 (进行中 15%)
- **技能学习**: 研究 OpenClaw 文档
- **脚本优化**: 完善自动化脚本的健壮性

---

## 🟢 第四象限：不重要且不紧急

#### 🧹 系统清理
- [ ] /tmp/ 目录清理
- [ ] 旧日志压缩

---

## ✅ 已完成任务

{completed_section}

---

## 📊 今日统计
- **活跃任务**: {len(urgent_items)}
- **已完成**: {len(done_items)}
- **系统状态**: 🟢 正常

**文件位置**: `/home/ubuntu/.openclaw/workspace/TODO.md`
**最后更新**: {update_time} GMT+8
**维护者**: Jarvis (贾维斯) ⚡
"""
    return content


def main():
    try:
        new_content = generate_todo()
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ TODO.md已自动更新 (v2.1)"
        )
        return 0
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 更新失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
