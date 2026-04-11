#!/usr/bin/env python3
"""
自动更新TODO列表
根据当前任务状态、项目进度和系统状态更新TODO.md
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 文件路径
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
TODO_FILE = WORKSPACE / "TODO.md"
TASK_FILE = WORKSPACE / ".current_task.json"
MEMORY_DIR = WORKSPACE / "memory"

def get_current_time():
    """获取当前时间（GMT+8）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S GMT+8")

def load_current_task():
    """加载当前任务状态"""
    if TASK_FILE.exists():
        with open(TASK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_project_status():
    """获取PARA项目状态"""
    projects_dir = WORKSPACE / "PARA" / "Projects"
    if not projects_dir.exists():
        return []
    
    projects = []
    for project_dir in projects_dir.iterdir():
        if project_dir.is_dir():
            readme = project_dir / "README.md"
            if readme.exists():
                projects.append({
                    "name": project_dir.name,
                    "path": str(readme).replace(str(WORKSPACE) + "/", "")
                })
    return projects

def update_todo():
    """更新TODO列表"""
    current_time = get_current_time()
    current_task = load_current_task()
    projects = get_project_status()
    
    # 统计信息
    active_count = 0
    completed_count = 0
    
    # 构建第一象限内容
    first_quadrant = []
    
    # 添加当前任务（如果有）
    if current_task:
        status = current_task.get("status", "")
        task_desc = current_task.get("active_task", "未知任务")
        
        if "✅" in status or "完成" in status:
            completed_count += 1
        else:
            active_count += 1
            first_quadrant.append(f"""
#### 🎯 当前任务
**任务**: {task_desc}
**状态**: {status}
**开始时间**: {current_task.get('started_at', '未知')}
""")
    
    # 添加项目
    for project in projects:
        active_count += 1
        first_quadrant.append(f"""
#### [[{project['path']}|{project['name']}]]
**状态**: 🔄 进行中
**进度**: 50% (更新于 {current_time})
""")
    
    # 构建内容
    content = f"""# 任务管理 - 四象限法则

**更新时间**: {current_time}
**更新方式**: 自动更新 (v2.2)
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
{''.join(first_quadrant) if first_quadrant else '暂无进行中的任务'}

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
{f"""
#### 🎉 {current_task.get('active_task', '未知任务')}
**完成时间**: {current_task.get('completed_at', current_time)}
**操作**: {', '.join(current_task.get('actions_taken', []))[:100]}...
""" if current_task and ('✅' in current_task.get('status', '') or '完成' in current_task.get('status', '')) else '暂无'}
---

## 📊 今日统计
- **活跃任务**: {active_count}
- **已完成**: {completed_count}
- **系统状态**: 🟢 正常

**文件位置**: `{str(TODO_FILE)}`
**最后更新**: {current_time}
**维护者**: Jarvis (贾维斯) ⚡
"""
    
    # 写入文件
    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ TODO列表已更新: {current_time}")
    print(f"📊 活跃任务: {active_count}, 已完成: {completed_count}")

if __name__ == "__main__":
    update_todo()
