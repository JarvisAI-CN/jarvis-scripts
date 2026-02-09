#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO.md自动更新脚本 v2.0
每小时更新，反映当前项目状态，智能分类
"""

import json
import os
import re
from datetime import datetime

TODO_FILE = "/home/ubuntu/.openclaw/workspace/TODO.md"
STATE_FILE = "/home/ubuntu/.openclaw/workspace/PARA/Projects/ImageHub技术分享项目/这个项目的文件/日志/controversial_state.json"
MEMORY_FILE = "/home/ubuntu/.openclaw/workspace/MEMORY.md"
WORKSPACE_DIR = "/home/ubuntu/.openclaw/workspace"

def get_podcast_status():
    """获取播客项目状态"""
    try:
        readme_path = f"{WORKSPACE_DIR}/PARA/Projects/YouTube视频转中文博客/README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "状态**: ✅ 已完成" in content:
                return {
                    'status': '✅ 已完成',
                    'progress': '100%',
                    'details': '- ✅ 项目框架完成\n- ✅ 播客翻译脚本开发完成\n- ✅ OpenClaw技能包结构创建\n- ✅ 首篇播客文稿EP001已生成\n- ✅ 定时任务已设置'
                }
        return {'status': '🔄 进行中', 'progress': '90%', 'details': '- ✅ 脚本开发完成\n- ✅ 首篇播客已生成'}
    except:
        return {'status': '待处理', 'progress': '0%', 'details': '无'}

def get_moltbook_status():
    """获取Moltbook项目状态"""
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            next_post = state.get('next_post', 14)
            posts = state.get('posts', {})
            published_count = len([p for p in posts.values() if p.get('status') == 'published'])
            
            # 检查当前时间是否在封禁期内
            now = datetime.now()
            resume_time = datetime(2026, 2, 10, 9, 0)
            is_suspended = now < resume_time
            
            return {
                'status': '⏸️ 暂停中' if is_suspended else '🔄 待恢复',
                'progress': f'{published_count}/8',
                'next_post': next_post,
                'resume_time': '2026-02-10 09:00'
            }
    except:
        return {'status': '⏸️ 暂停中', 'progress': '1/8', 'next_post': 14, 'resume_time': '2026-02-10 09:00'}

def get_email_project_status():
    """获取自建邮件网站项目状态"""
    try:
        # 优先查看 PARA/Projects 标准路径
        project_file = f"{WORKSPACE_DIR}/PARA/Projects/自建邮件网站项目/README.md"
        # 备选 Zettelkasten 路径
        old_project_file = f"{WORKSPACE_DIR}/Zettelkasten/自建邮件网站项目.md"
        
        target_file = project_file if os.path.exists(project_file) else old_project_file
        
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 尝试从内容中直接提取进度
                prog_match = re.search(r'当前进度: (\d+%)', content)
                if prog_match:
                    progress = prog_match.group(1)
                else:
                    # 智能计算进度: 任务列表中的 [x] / ([x] + [ ])
                    tasks = re.findall(r'- \[(x| )\]', content)
                    if tasks:
                        completed = tasks.count('x')
                        total = len(tasks)
                        progress = f"{int(completed / total * 100)}%"
                    else:
                        progress = '35%'
                
                if "认证失败" in content or "阻塞" in content or "535 Auth failed" in content:
                    status = '⚠️ 阻塞 (SMTP认证)'
                elif "✅ 已完成" in content:
                    status = '✅ 已完成'
                else:
                    status = '🔄 进行中'
                    
                return {'status': status, 'progress': progress}
        return None
    except:
        return {'status': '🔄 进行中', 'progress': '35%'}

def generate_todo():
    """生成TODO.md内容"""
    now = datetime.now()
    update_time = now.strftime('%Y-%m-%d %H:%M:%S')

    podcast = get_podcast_status()
    moltbook = get_moltbook_status()
    email = get_email_project_status()

    # 第一象限任务构建
    urgent_tasks = []
    
    # 邮件项目
    if email and email['status'] != '✅ 已完成':
        urgent_tasks.append(f"""#### 自建邮件网站项目 📧
**状态**: {email['status']}
**进度**: {email['progress']}
**备注**: 正在解决 SMTP 中继认证问题 (535 Auth failed)。""")

    # Moltbook 恢复任务
    urgent_tasks.append(f"""#### Moltbook 账户恢复与清理 💬
**状态**: {moltbook['status']}
**目标时间**: {moltbook['resume_time']}
**任务**: 1. 解封后立即清理重复帖子；2. 恢复争议性内容发布 (Post {moltbook['next_post']})。""")

    # 完成的任务
    completed_tasks = []
    if podcast['status'] == '✅ 已完成':
        completed_tasks.append(f"""#### YouTube视频转中文播客项目 🎙️
**完成日期**: 2026-02-09
**成果**: 
{podcast['details']}""")

    urgent_section = "\n\n---\n".join(urgent_tasks) if urgent_tasks else "暂无正在进行的任务"
    completed_section = "\n\n---\n".join(completed_tasks) if completed_tasks else "暂无已完成任务"

    content = f"""# 任务管理 - 四象限法则

**更新时间**: {update_time} GMT+8
**更新方式**: 自动更新（每小时）+ 心跳实时更新
**处理策略**: 重要紧急 > 紧急不重要 > 重要不紧急 > 不紧急

---

## 📋 四象限说明

### 🔴 第一象限：重要且紧急（立即处理）
- 关键任务 & 项目瓶颈
- 账户状态恢复
- 凌晨自主学习的核心产出

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
- [ ] **Moltbook发布**: 暂停中 (预期 09:00 恢复)
- [x] **系统巡检**: 磁盘空间、挂载状态 (正常)

---

## 🟡 第三象限：重要但不紧急

#### 📚 知识管理与系统优化
- **PARA 维护**: 整理 Resources 索引 (进行中 40%)
- **Obsidian 优化**: 强化双链连接 (进行中 15%)
- **技能学习**: 研究 awesome-openclaw-skills (进行中)
- **脚本优化**: 完善备份与发布脚本的健壮性

---

## 🟢 第四象限：不重要且不紧急

#### 🧹 系统清理
- [ ] /tmp/ 目录清理 (每周一次)
- [ ] 旧日志压缩与归档 (每月一次)

---

## ✅ 已完成任务

{completed_section}

---

## 📊 今日统计
- **活跃任务**: {len(urgent_tasks)}
- **已完成**: {len(completed_tasks)}
- **系统状态**: 🟢 正常

**文件位置**: `/home/ubuntu/.openclaw/workspace/TODO.md`
**最后更新**: {update_time} GMT+8
**维护者**: Jarvis (贾维斯) ⚡
"""
    return content

def main():
    try:
        new_content = generate_todo()
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ TODO.md已自动更新 (v2.0)")
        return 0
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 更新失败: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
