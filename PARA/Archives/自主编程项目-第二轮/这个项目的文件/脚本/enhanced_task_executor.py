#!/usr/bin/env python3
"""
增强任务执行器 v3.0
集成增强监控、增强知识管理等功能
创建时间: 2026-02-14
版本: v3.0
"""

from __future__ import annotations
import os
import sys
import json
import time
import subprocess
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TaskCategory(Enum):
    """任务类别"""
    MONITORING = "monitoring"
    KNOWLEDGE = "knowledge"
    MAINTENANCE = "maintenance"
    DEVELOPMENT = "development"


@dataclass
class EnhancedTaskResult:
    """增强任务结果"""
    task_id: str
    category: TaskCategory
    status: str  # success/failed/partial
    duration: float
    output: str
    metrics: Dict[str, Any]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "category": self.category.value,
            "status": self.status,
            "duration": round(self.duration, 2),
            "output": self.output,
            "metrics": self.metrics,
            "timestamp": self.timestamp.isoformat()
        }


class EnhancedMonitoringTask:
    """增强监控任务"""

    def __init__(self):
        self.feishu_alert_url = os.getenv("FEISHU_WEBHOOK_URL", "")

    def check_gateway_health(self) -> Tuple[bool, str]:
        """检查Gateway健康状态"""
        try:
            result = subprocess.run(
                ["openclaw", "gateway", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)

    def check_webdav_mount(self) -> Tuple[bool, str]:
        """检查WebDAV挂载状态"""
        mount_point = "/home/ubuntu/123pan"

        try:
            # 检查挂载点
            result = subprocess.run(
                ["mount", "|", "grep", "123pan"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # 检查读写权限
                test_file = Path(mount_point) / f".test_{int(time.time())}"
                try:
                    test_file.touch()
                    test_file.unlink()
                    return True, "WebDAV挂载正常，读写权限正常"
                except Exception:
                    return False, "WebDAV挂载但无写权限"
            else:
                return False, "WebDAV未挂载"

        except Exception as e:
            return False, f"检查失败: {e}"

    def check_disk_space(self) -> Tuple[bool, str]:
        """检查磁盘空间"""
        try:
            result = subprocess.run(
                ["df", "-h", "/home/ubuntu"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage_percent = int(parts[4].replace('%', ''))
                        if usage_percent > 90:
                            return False, f"磁盘空间不足: {usage_percent}%"
                        elif usage_percent > 80:
                            return True, f"磁盘警告: {usage_percent}%"
                        else:
                            return True, f"磁盘正常: {usage_percent}%"
            return False, "无法解析磁盘信息"
        except Exception as e:
            return False, f"检查失败: {e}"

    def send_feishu_alert(self, title: str, content: str):
        """发送飞书告警"""
        if not self.feishu_alert_url:
            logger.warning("飞书Webhook URL未配置")
            return

        try:
            import requests

            payload = {
                "msg_type": "text",
                "content": {
                    "text": f"【{title}】\n\n{content}"
                }
            }

            response = requests.post(
                self.feishu_alert_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("飞书告警发送成功")
            else:
                logger.error(f"飞书告警发送失败: {response.text}")

        except Exception as e:
            logger.error(f"发送飞书告警失败: {e}")

    def execute_enhanced_monitoring(self) -> EnhancedTaskResult:
        """执行增强监控任务"""
        start_time = time.time()
        task_id = f"MON-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"🔍 执行增强监控: {task_id}")

        metrics = {}
        alerts = []

        # 检查Gateway
        gateway_ok, gateway_info = self.check_gateway_health()
        metrics["gateway"] = gateway_ok
        if not gateway_ok:
            alerts.append(f"Gateway异常: {gateway_info}")
            self.send_feishu_alert("Gateway异常", gateway_info)

        # 检查WebDAV
        webdav_ok, webdav_info = self.check_webdav_mount()
        metrics["webdav"] = webdav_ok
        if not webdav_ok:
            alerts.append(f"WebDAV异常: {webdav_info}")
            self.send_feishu_alert("WebDAV异常", webdav_info)

        # 检查磁盘空间
        disk_ok, disk_info = self.check_disk_space()
        metrics["disk"] = disk_ok
        if not disk_ok:
            alerts.append(f"磁盘空间异常: {disk_info}")
            self.send_feishu_alert("磁盘空间异常", disk_info)

        duration = time.time() - start_time

        # 判断状态
        all_ok = all(metrics.values())
        status = "success" if all_ok else "partial" if any(metrics.values()) else "failed"

        output = f"监控完成: {len([k for k, v in metrics.items() if v])}/{len(metrics)} 项正常"

        if alerts:
            output += f" | 告警: {len(alerts)} 个"

        return EnhancedTaskResult(
            task_id=task_id,
            category=TaskCategory.MONITORING,
            status=status,
            duration=duration,
            output=output,
            metrics=metrics,
            timestamp=datetime.now()
        )


class EnhancedKnowledgeTask:
    """增强知识管理任务"""

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.para_dir = self.workspace / "PARA"
        self.zettelkasten_dir = self.workspace / "Zettelkasten"

    def scan_para_structure(self) -> Dict[str, Any]:
        """扫描PARA结构"""
        structure = {
            "Projects": [],
            "Areas": [],
            "Resources": [],
            "Archives": []
        }

        for category in structure.keys():
            category_path = self.para_dir / category
            if category_path.exists():
                for item in category_path.iterdir():
                    if item.is_dir():
                        structure[category].append({
                            "name": item.name,
                            "path": str(item),
                            "readme": (item / "README.md").exists()
                        })

        return structure

    def detect_broken_links(self) -> List[str]:
        """检测断裂的双链"""
        broken_links = []

        for md_file in self.workspace.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 查找所有双链
                links = re.findall(r'\[\[([^\]]+)\]\]', content)

                for link in links:
                    # 解析链接
                    link_parts = link.split('|')
                    link_target = link_parts[0].strip()

                    # 查找目标文件
                    target_files = list(self.workspace.rglob(f"{link_target}.md"))

                    if not target_files:
                        broken_links.append(f"{md_file}: [[{link}]]")

            except Exception as e:
                logger.warning(f"检测文件失败 {md_file}: {e}")

        return broken_links

    def generate_knowledge_graph(self) -> Dict[str, List[str]]:
        """生成知识图谱"""
        graph = {}

        for md_file in self.workspace.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 查找所有双链
                links = re.findall(r'\[\[([^\]]+)\]\]', content)

                # 清理链接
                cleaned_links = []
                for link in links:
                    link_parts = link.split('|')
                    cleaned_links.append(link_parts[0].strip())

                # 添加到图谱
                relative_path = str(md_file.relative_to(self.workspace))
                graph[relative_path] = cleaned_links

            except Exception as e:
                logger.warning(f"解析文件失败 {md_file}: {e}")

        return graph

    def execute_enhanced_knowledge_management(self) -> EnhancedTaskResult:
        """执行增强知识管理"""
        start_time = time.time()
        task_id = f"KNOW-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"📚 执行增强知识管理: {task_id}")

        # 扫描PARA结构
        logger.info("扫描PARA结构...")
        para_structure = self.scan_para_structure()

        # 检测断裂链接
        logger.info("检测断裂双链...")
        broken_links = self.detect_broken_links()

        # 生成知识图谱
        logger.info("生成知识图谱...")
        knowledge_graph = self.generate_knowledge_graph()

        duration = time.time() - start_time

        metrics = {
            "para_items": sum(len(items) for items in para_structure.values()),
            "broken_links": len(broken_links),
            "knowledge_nodes": len(knowledge_graph),
            "total_links": sum(len(links) for links in knowledge_graph.values())
        }

        output = (
            f"知识管理完成: "
            f"PARA项目 {metrics['para_items']} 个, "
            f"断裂链接 {metrics['broken_links']} 个, "
            f"知识节点 {metrics['knowledge_nodes']} 个"
        )

        status = "success" if metrics['broken_links'] == 0 else "partial"

        return EnhancedTaskResult(
            task_id=task_id,
            category=TaskCategory.KNOWLEDGE,
            status=status,
            duration=duration,
            output=output,
            metrics={
                "para_structure": para_structure,
                "broken_links": broken_links[:10],  # 只保留前10个
                "knowledge_graph_stats": {
                    "nodes": metrics['knowledge_nodes'],
                    "links": metrics['total_links']
                }
            },
            timestamp=datetime.now()
        )


class EnhancedTaskExecutor:
    """增强任务执行器"""

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.monitoring_task = EnhancedMonitoringTask()
        self.knowledge_task = EnhancedKnowledgeTask(str(self.workspace))

    def detect_task_category(self, task_description: str) -> TaskCategory:
        """检测任务类别"""
        desc_lower = task_description.lower()

        if any(keyword in desc_lower for keyword in ["监控", "检查", "monitor", "health"]):
            return TaskCategory.MONITORING
        elif any(keyword in desc_lower for keyword in ["知识", "文档", "knowledge", "para", "双链"]):
            return TaskCategory.KNOWLEDGE
        elif any(keyword in desc_lower for keyword in ["维护", "maintenance"]):
            return TaskCategory.MAINTENANCE
        else:
            return TaskCategory.DEVELOPMENT

    def execute_task(
        self,
        task_id: str,
        task_description: str,
        category: Optional[TaskCategory] = None
    ) -> EnhancedTaskResult:
        """执行增强任务"""
        logger.info(f"🔄 执行增强任务: {task_id}")

        # 检测任务类别
        if category is None:
            category = self.detect_task_category(task_description)

        # 根据类别执行
        if category == TaskCategory.MONITORING:
            result = self.monitoring_task.execute_enhanced_monitoring()
        elif category == TaskCategory.KNOWLEDGE:
            result = self.knowledge_task.execute_enhanced_knowledge_management()
        else:
            # 默认执行
            result = EnhancedTaskResult(
                task_id=task_id,
                category=category,
                status="success",
                duration=0.0,
                output=f"任务类别 {category.value} 暂不支持增强执行",
                metrics={},
                timestamp=datetime.now()
            )

        logger.info(f"✅ 任务完成: {result.task_id} - {result.status}")
        return result

    def execute_all_enhanced_tasks(self) -> List[EnhancedTaskResult]:
        """执行所有增强任务"""
        logger.info("=" * 70)
        logger.info("🚀 增强任务执行器启动")
        logger.info("=" * 70)

        results = []

        # 1. 增强监控
        logger.info("\n📍 任务1: 增强监控")
        result1 = self.execute_task(
            task_id=f"MON-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_description="系统健康检查",
            category=TaskCategory.MONITORING
        )
        results.append(result1)

        # 2. 增强知识管理
        logger.info("\n📍 任务2: 增强知识管理")
        result2 = self.execute_task(
            task_id=f"KNOW-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_description="知识库管理",
            category=TaskCategory.KNOWLEDGE
        )
        results.append(result2)

        # 生成报告
        logger.info("\n" + "=" * 70)
        logger.info("📊 执行报告")
        logger.info("=" * 70)

        for result in results:
            logger.info(f"\n{result.task_id}: {result.category.value}")
            logger.info(f"  状态: {result.status}")
            logger.info(f"  耗时: {result.duration:.2f}秒")
            logger.info(f"  输出: {result.output}")

        return results


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增强任务执行器v3.0")
    parser.add_argument("--workspace", default="/home/ubuntu/.openclaw/workspace", help="工作区路径")
    parser.add_argument("--task-id", help="任务ID")
    parser.add_argument("--task-description", help="任务描述")
    parser.add_argument("--category", help="任务类别 (monitoring/knowledge)")
    parser.add_argument("--run-all", action="store_true", help="执行所有增强任务")

    args = parser.parse_args()

    executor = EnhancedTaskExecutor(workspace=args.workspace)

    if args.run_all:
        # 执行所有增强任务
        results = executor.execute_all_enhanced_tasks()
    elif args.task_id and args.task_description:
        # 执行单个任务
        category = TaskCategory(args.category) if args.category else None
        result = executor.execute_task(args.task_id, args.task_description, category)

        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print("请提供 --run-all 或 --task-id + --task-description")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
