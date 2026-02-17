#!/usr/bin/env python3
"""
智谱24小时任务调度器
让 zhipu/glm-4.7 全天候处理重活
"""

import json
import subprocess
from datetime import datetime
import os

SCHEDULE_FILE = "/home/ubuntu/.openclaw/workspace/.zhipu_schedule.json"

# 24小时任务计划
HOURLY_TASKS = {
    "00:00": "凌晨自主学习 - 知识整理与内容准备",
    "01:00": "代码扫描 - 检查所有Python脚本的性能问题",
    "02:00": "备份验证 - 检查123盘备份完整性",
    "03:00": "日志分析 - 分析Nginx访问日志，发现异常",
    "04:00": "文档优化 - 优化README和文档",
    "05:00": "知识图谱 - 更新Obsidian双链",
    "06:00": "系统巡检 - 检查磁盘、内存、服务状态",
    "07:00": "项目归档 - 整理PARA/Projects，归档完成项目",
    "08:00": "代码审查 - 扫描最近修改的代码",
    "09:00": "更新检查 - 检查OpenClaw和依赖更新",
    "10:00": "数据库优化 - 分析数据库性能",
    "11:00": "文档生成 - 为新项目生成README",
    "12:00": "日志清理 - 清理旧日志文件",
    "13:00": "依赖检查 - 检查过期的npm/pip包",
    "14:00": "安全扫描 - 扫描代码安全问题",
    "15:00": "性能分析 - 分析脚本执行时间",
    "16:00": "备份检查 - 验证最新备份",
    "17:00": "知识整理 - 整理最近的学习笔记",
    "18:00": "脚本优化 - 优化慢速脚本",
    "19:00": "文档更新 - 更新技术文档",
    "20:00": "系统清理 - 清理临时文件",
    "21:00": "错误分析 - 分析最近的错误日志",
    "22:00": "备份准备 - 为夜间备份做准备",
    "23:00": "日报生成 - 生成每日工作报告",
}

# 任务类型（使用sessions_spawn创建隔离会话）
TASK_TYPES = {
    "代码扫描": "scan_code",
    "文档优化": "optimize_docs",
    "日志分析": "analyze_logs",
    "知识整理": "organize_knowledge",
    "系统巡检": "system_check",
    "安全扫描": "security_scan",
}

def get_current_hour_task():
    """获取当前小时的任务"""
    now = datetime.now()
    hour_key = f"{now.hour:02d}:00"
    return HOURLY_TASKS.get(hour_key, "待机状态")

def spawn_zhipu_task(task_name, task_description):
    """启动智谱子代理处理任务"""
    try:
        # 使用 sessions_spawn 创建隔离会话
        result = subprocess.run([
            "python3", "-c",
            f"""
import subprocess
subprocess.run([
    "sessions_spawn",
    "--agentId", "zhipu/glm-4.7",
    "--label", "zhipu-hourly-{datetime.now().hour}",
    "--task", "{task_description}",
    "--cleanup", "keep"
], capture_output=True, text=True)
print(result.stdout)
"""
        ], capture_output=True, text=True, timeout=300)
        
        print(f"✅ 任务已派发: {task_name}")
        print(f"   会话: zhipu-hourly-{datetime.now().hour}")
        return True
    except Exception as e:
        print(f"❌ 任务派发失败: {e}")
        return False

def show_schedule():
    """显示24小时任务计划"""
    print("=" * 60)
    print("🤖 智谱24小时任务调度计划")
    print("=" * 60)
    
    for hour, task in sorted(HOURLY_TASKS.items()):
        print(f"{hour} - {task}")
    
    print("=" * 60)

def main():
    import sys
    now = datetime.now()
    current_hour = now.hour
    
    print(f"\n📅 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 当前任务: {HOURLY_TASKS.get(f'{current_hour:02d}:00', '待机')}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        show_schedule()
    elif len(sys.argv) > 1 and sys.argv[1] == "--run":
        # 执行当前小时的任务
        task = HOURLY_TASKS.get(f"{current_hour:02d}:00")
        if task:
            print(f"\n🚀 启动智谱处理: {task}")
            spawn_zhipu_task(f"hourly-{current_hour}", task)
        else:
            print("⏸️ 当前时段无任务")
    else:
        print("\n用法:")
        print("  python3 zhipu_scheduler.py --schedule  # 显示任务计划")
        print("  python3 zhipu_scheduler.py --run      # 执行当前任务")
        print("\n💡 建议添加到crontab:")
        print(f"  0 * * * * /usr/bin/python3 {SCHEDULE_FILE.replace('.json', '.py')} --run")

if __name__ == "__main__":
    main()
