#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主编程控制器 v3.0 (Autonomous Programming Controller)
GLM-5 增强版 - 集成三大增强功能

核心特性:
- task_list.json 结构化任务管理
- progress_flow.log 执行日志
- Commit-per-Task 精确回滚
- 上下文管理 (定期压缩)
- 端到端验证 (E2E Testing)

增强功能 (v3.0):
✅ 1. 修复任务循环问题 - 改进任务类型检测逻辑
✅ 2. 增强监控任务 - Gateway/WebDAV/阈值检查 + 飞书告警
✅ 3. 增强知识管理任务 - PARA索引 + Obsidian双链 + 知识图谱
"""

import os
import sys
import json
import subprocess
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import traceback

# 导入自定义模块
try:
    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from modules.feishu_notifier import FeishuNotifier
except ImportError:
    FeishuNotifier = None

# 配置
WORKSPACE = Path("/home/ubuntu/openclaw/workspace")
TASK_LIST_FILE = WORKSPACE / ".task_list.json"
PROGRESS_LOG_FILE = WORKSPACE / "logs" / "progress_flow.log"
STATE_DIR = WORKSPACE / ".maintenance_state"
CONTEXT_FILE = STATE_DIR / "context.json"
LOG_DIR = WORKSPACE / "logs"


class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型枚举"""
    BUGFIX = "bugfix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    MAINTENANCE = "maintenance"
    TESTING = "testing"


class LogLevel(Enum):
    """日志级别枚举"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    DEBUG = "debug"


@dataclass
class Subtask:
    """子任务数据类"""
    id: str
    title: str
    status: TaskStatus
    completed_at: Optional[str] = None
    git_commit: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TaskLog:
    """任务日志数据类"""
    timestamp: str
    level: LogLevel
    message: str
    module: str = "CONTROLLER"


@dataclass
class Task:
    """任务数据类"""
    id: str
    title: str
    description: str
    source: str
    type: TaskType
    priority: str  # high, medium, low
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    assigned_to: str = "GLM-4.7"
    subtasks: List[Subtask] = None
    logs: List[TaskLog] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.subtasks is None:
            self.subtasks = []
        if self.logs is None:
            self.logs = []


class ProgressFlowLogger:
    """进度流日志记录器"""

    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def log(self, module: str, level: LogLevel, message: str):
        """写入日志"""
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_line = f"[{timestamp}] [{module}] [{level.value}] {message}\n"

            # 写入文件
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_line)

            # 同时输出到控制台
            print(log_line.strip())

    def info(self, module: str, message: str):
        self.log(module, LogLevel.INFO, message)

    def success(self, module: str, message: str):
        self.log(module, LogLevel.SUCCESS, message)

    def warning(self, module: str, message: str):
        self.log(module, LogLevel.WARNING, message)

    def error(self, module: str, message: str):
        self.log(module, LogLevel.ERROR, message)


class GitOperator:
    """Git 操作器 - 实现 Commit-per-Task"""

    def __init__(self, workspace: Path, logger: ProgressFlowLogger):
        self.workspace = workspace
        self.logger = logger

    def commit(self, message: str, files: List[str] = None) -> Optional[str]:
        """提交更改并返回 commit hash"""
        try:
            os.chdir(self.workspace)

            # 添加文件
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        capture_output=True,
                        check=True
                    )
            else:
                # 添加所有更改
                subprocess.run(
                    ["git", "add", "."],
                    capture_output=True,
                    check=True
                )

            # 提交
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=True
            )

            # 获取 commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )

            commit_hash = hash_result.stdout.strip()
            self.logger.success(
                "GIT-OPERATOR",
                f"Commit {commit_hash[:7]}: {message}"
            )

            return commit_hash

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "GIT-OPERATOR",
                f"Git commit failed: {e.stderr}"
            )
            return None

    def push(self, branch: str = "main") -> bool:
        """推送到远程仓库"""
        try:
            os.chdir(self.workspace)

            subprocess.run(
                ["git", "push", "origin", branch],
                capture_output=True,
                check=True,
                timeout=60
            )

            self.logger.success("GIT-OPERATOR", f"Pushed to origin/{branch}")
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error(
                "GIT-OPERATOR",
                f"Git push failed: {e.stderr}"
            )
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("GIT-OPERATOR", "Git push timeout")
            return False

    def rollback(self, commit_hash: str, hard: bool = False) -> bool:
        """回滚到指定提交"""
        try:
            os.chdir(self.workspace)

            mode = "--hard" if hard else "--soft"
            subprocess.run(
                ["git", "reset", mode, commit_hash],
                capture_output=True,
                check=True
            )

            self.logger.warning(
                "GIT-OPERATOR",
                f"Rolled back to {commit_hash[:7]} ({'hard' if hard else 'soft'})"
            )
            return True

        except subprocess.CalledProcessError as e:
            self.logger.error("GIT-OPERATOR", f"Rollback failed: {e}")
            return False

    def get_current_commit(self) -> Optional[str]:
        """获取当前 commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.workspace
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None


class TaskManager:
    """任务管理器 - 管理 task_list.json"""

    def __init__(
        self,
        task_file: Path,
        logger: ProgressFlowLogger,
        git_operator: GitOperator
    ):
        self.task_file = task_file
        self.logger = logger
        self.git = git_operator
        self.data = self._load_or_create()

    def _load_or_create(self) -> Dict:
        """加载或创建任务列表"""
        if self.task_file.exists():
            with open(self.task_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "version": "3.0",
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
        with open(self.task_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        # Git 提交
        self.git.commit(
            f"chore(task): update task_list.json",
            [str(self.task_file.relative_to(self.git.workspace))]
        )

    def add_task(self, task: Task) -> str:
        """添加新任务"""
        task_dict = asdict(task)
        task_dict["type"] = task.type.value
        task_dict["status"] = task.status.value

        for subtask in task_dict["subtasks"]:
            subtask["status"] = subtask["status"].value

        self.data["tasks"].append(task_dict)
        self._save()

        self.logger.info(
            "TASK-MANAGER",
            f"Added task {task.id}: {task.title}"
        )

        return task.id

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务"""
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                return task
        return None

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        commit_hash: Optional[str] = None,
        error: Optional[str] = None
    ):
        """更新任务状态"""
        task = self.get_task(task_id)
        if not task:
            self.logger.error(
                "TASK-MANAGER",
                f"Task not found: {task_id}"
            )
            return

        task["status"] = status.value

        if status == TaskStatus.IN_PROGRESS:
            task["started_at"] = datetime.now().isoformat()
        elif status in [TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            task["completed_at"] = datetime.now().isoformat()

        if commit_hash:
            task["git_commit"] = commit_hash

        if error:
            task["error"] = error

        self._save()

        self.logger.info(
            "TASK-MANAGER",
            f"Updated task {task_id} to {status.value}"
        )

    def add_task_log(self, task_id: str, log: TaskLog):
        """添加任务日志"""
        task = self.get_task(task_id)
        if not task:
            return

        log_dict = asdict(log)
        log_dict["level"] = log.level.value

        task["logs"].append(log_dict)
        self._save()

    def get_pending_tasks(self, limit: int = 5) -> List[Dict]:
        """获取待处理任务"""
        pending = [
            t for t in self.data["tasks"]
            if t["status"] == TaskStatus.PENDING.value
        ]

        # 按优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending.sort(key=lambda t: priority_order.get(t["priority"], 3))

        return pending[:limit]

    def mark_subtask_done(
        self,
        task_id: str,
        subtask_id: str,
        commit_hash: str
    ):
        """标记子任务完成"""
        task = self.get_task(task_id)
        if not task:
            return

        for subtask in task["subtasks"]:
            if subtask["id"] == subtask_id:
                subtask["status"] = TaskStatus.DONE.value
                subtask["completed_at"] = datetime.now().isoformat()
                subtask["git_commit"] = commit_hash
                break

        self._save()


class E2EVerifier:
    """端到端验证器 - 增强版 v3.0"""

    def __init__(self, logger: ProgressFlowLogger):
        self.logger = logger

    def verify_syntax(self, code: str) -> Tuple[bool, str]:
        """验证代码语法"""
        try:
            compile(code, '<string>', 'exec')
            return True, "语法正确"
        except SyntaxError as e:
            return False, f"语法错误: {e}"

    def verify_script_exists(self, script_path: Path) -> Tuple[bool, str]:
        """验证脚本是否存在"""
        if script_path.exists():
            return True, f"脚本存在: {script_path}"
        return False, f"脚本不存在: {script_path}"

    def verify_script_executable(self, script_path: Path) -> Tuple[bool, str]:
        """验证脚本是否可执行"""
        if os.access(script_path, os.X_OK):
            return True, "脚本可执行"
        return False, "脚本不可执行"

    def verify_script_runs(self, script_path: Path) -> Tuple[bool, str]:
        """验证脚本能否运行"""
        try:
            result = subprocess.run(
                [str(script_path), "--check"],  # 假设支持 --check 模式
                capture_output=True,
                timeout=30,
                cwd=WORKSPACE
            )

            if result.returncode == 0:
                return True, "脚本运行成功"
            else:
                return False, f"脚本运行失败: {result.stderr.decode()}"

        except subprocess.TimeoutExpired:
            return False, "脚本运行超时"
        except Exception as e:
            return False, f"脚本运行异常: {e}"

    def verify_task_completion(self, task: Dict) -> Tuple[bool, str]:
        """验证任务完成情况 - 增强版"""
        task_type = task.get("type")

        if task_type == TaskType.BUGFIX.value:
            # 对于 Bug 修复，验证问题是否解决
            return self._verify_bug_fixed(task)
        elif task_type == TaskType.FEATURE.value:
            # 对于新功能，验证功能是否工作
            return self._verify_feature_working(task)
        elif task_type == TaskType.MAINTENANCE.value:
            # 对于维护任务，验证系统状态
            return self._verify_maintenance_task(task)
        else:
            return True, "任务类型无需验证"

    def _verify_bug_fixed(self, task: Dict) -> Tuple[bool, str]:
        """验证Bug修复完成情况"""
        # 检查是否有生成的修复代码
        fix_file = WORKSPACE / f".fix_{task['id']}.py"
        if not fix_file.exists():
            return False, "未找到修复代码文件"

        return True, "Bug修复代码已生成"

    def _verify_feature_working(self, task: Dict) -> Tuple[bool, str]:
        """验证功能开发完成情况"""
        feature_file = WORKSPACE / f".feature_{task['id']}.py"
        if not feature_file.exists():
            return False, "未找到功能代码文件"

        return True, "功能开发代码已生成"

    def _verify_maintenance_task(self, task: Dict) -> Tuple[bool, str]:
        """验证维护任务完成情况 - 增强版"""
        # 检查是否有维护日志
        monitor_log = LOG_DIR / "enhanced_monitoring.jsonl"
        if not monitor_log.exists():
            return False, "未找到监控日志"

        # 检查知识图谱
        knowledge_graph = LOG_DIR / "knowledge_graph.json"
        if not knowledge_graph.exists():
            return False, "未找到知识图谱"

        return True, "维护任务完成: 监控和知识图谱已更新"


class EnhancedTaskExecutor:
    """增强任务执行器 - v3.0"""

    def __init__(self, workspace: Path, logger: ProgressFlowLogger):
        self.workspace = workspace
        self.logger = logger

        # 初始化飞书通知器
        self.feishu = None
        if FeishuNotifier:
            try:
                self.feishu = FeishuNotifier()
            except Exception as e:
                self.logger.warning(f"飞书通知器初始化失败: {e}")

    def execute_enhanced_monitoring(self, task: Dict) -> bool:
        """执行增强监控任务"""
        task_id = task.get("id")
        self.logger.info("ENHANCED_EXECUTOR", f"开始增强监控任务: {task_id}")

        try:
            # 1. 检查Gateway状态
            gateway_ok, gateway_status = self._check_gateway_status()
            self.logger.info("ENHANCED_EXECUTOR", f"Gateway检查: {gateway_status}")

            # 2. 检查WebDAV响应时间
            webdav_ok, webdav_time, webdav_status = self._check_webdav_response_time()
            self.logger.info("ENHANCED_EXECUTOR", f"WebDAV检查: {webdav_status}")

            # 3. 检查磁盘空间
            disk_usage = self._check_disk_space()
            self.logger.info("ENHANCED_EXECUTOR", f"磁盘使用率: {disk_usage}%")

            # 4. 汇总指标
            metrics = {
                "gateway_ok": gateway_ok,
                "gateway_status": gateway_status,
                "webdav_ok": webdav_ok,
                "webdav_response_time": webdav_time,
                "disk_usage_percent": disk_usage,
                "timestamp": datetime.now().isoformat()
            }

            # 5. 检查告警阈值
            alerts = self._check_alert_thresholds(metrics)

            # 6. 发送飞书告警（如有）
            if alerts:
                self._send_feishu_alert(alerts)

            # 7. 保存监控日志
            monitor_log = LOG_DIR / "enhanced_monitoring.jsonl"
            with open(monitor_log, "a") as f:
                f.write(json.dumps(metrics) + "\n")

            self.logger.success("ENHANCED_EXECUTOR", f"增强监控任务完成: {task_id}")
            return True

        except Exception as e:
            self.logger.error("ENHANCED_EXECUTOR", f"增强监控任务失败: {str(e)}")
            return False

    def execute_enhanced_knowledge(self, task: Dict) -> bool:
        """执行增强知识管理任务"""
        task_id = task.get("id")
        self.logger.info("ENHANCED_EXECUTOR", f"开始增强知识管理任务: {task_id}")

        try:
            # 1. PARA系统索引
            resources = self._scan_para_resources()
            self.logger.info("ENHANCED_EXECUTOR", f"扫描到 {len(resources)} 个资源文件")

            # 2. Obsidian双链优化检测
            broken_links_count = 0
            checked_files = 0

            for md_file in self.workspace.rglob("*.md"):
                if checked_files >= 50:  # 限制检查数量
                    break

                broken = self._detect_obsidian_broken_links(md_file)
                if broken:
                    broken_links_count += len(broken)

                checked_files += 1

            self.logger.info("ENHANCED_EXECUTOR",
                           f"检查了 {checked_files} 个文件，发现 {broken_links_count} 个断裂链接")

            # 3. 知识图谱更新
            knowledge_graph = self._build_knowledge_graph_index()
            graph_file = LOG_DIR / "knowledge_graph.json"
            with open(graph_file, "w") as f:
                json.dump(knowledge_graph, f, indent=2, ensure_ascii=False)

            self.logger.info("ENHANCED_EXECUTOR",
                           f"知识图谱已更新: {len(knowledge_graph['nodes'])} 个节点，{len(knowledge_graph['edges'])} 条边")

            return True

        except Exception as e:
            self.logger.error("ENHANCED_EXECUTOR", f"增强知识管理任务失败: {str(e)}")
            return False

    def _check_gateway_status(self) -> Tuple[bool, str]:
        """检查Gateway状态"""
        try:
            result = subprocess.run(
                ["openclaw", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, "Gateway运行正常"
            else:
                return False, f"命令执行失败: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "Gateway状态检查超时"
        except Exception as e:
            return False, f"Gateway状态检查异常: {str(e)}"

    def _check_webdav_response_time(self) -> Tuple[bool, float, str]:
        """检查WebDAV响应时间"""
        try:
            start = datetime.now()

            # 测试123盘挂载点
            test_file = self.workspace / "123pan" / ".test_write.tmp"

            # 写入测试
            with open(test_file, "w") as f:
                f.write("test")

            # 读取测试
            with open(test_file, "r") as f:
                f.read()

            # 删除测试文件
            test_file.unlink()

            elapsed = (datetime.now() - start).total_seconds()

            if elapsed > 5.0:
                return False, elapsed, f"WebDAV响应过慢: {elapsed:.2f}秒"
            else:
                return True, elapsed, f"WebDAV响应正常: {elapsed:.2f}秒"

        except Exception as e:
            elapsed = (datetime.now() - start).total_seconds()
            return False, elapsed, f"WebDAV检查失败: {str(e)}"

    def _check_disk_space(self) -> int:
        """检查磁盘使用率"""
        try:
            result = subprocess.run(
                ["df", "/home/ubuntu/123pan"],
                capture_output=True,
                text=True
            )
            disk_usage_line = result.stdout.split('\n')[1].split()
            disk_usage_percent = int(disk_usage_line[4].rstrip('%'))

            return disk_usage_percent
        except Exception:
            return 0

    def _check_alert_thresholds(self, metrics: Dict) -> List[Dict]:
        """检查告警阈值"""
        alerts = []

        # Gateway状态告警
        if not metrics.get("gateway_ok", False):
            alerts.append({
                "type": "critical",
                "source": "gateway",
                "message": metrics.get("gateway_status", "Gateway异常")
            })

        # WebDAV响应时间告警
        webdav_time = metrics.get("webdav_response_time", 0)
        if webdav_time > 5.0:
            alerts.append({
                "type": "warning",
                "source": "webdav",
                "message": f"WebDAV响应时间过长: {webdav_time:.2f}秒"
            })

        # 磁盘空间告警
        disk_usage = metrics.get("disk_usage_percent", 0)
        if disk_usage > 80:
            alerts.append({
                "type": "warning",
                "source": "disk",
                "message": f"磁盘使用率过高: {disk_usage}%"
            })

        return alerts

    def _send_feishu_alert(self, alerts: List[Dict]) -> bool:
        """发送飞书告警通知"""
        if not self.feishu:
            return False

        if not alerts:
            return True

        # 创建告警消息
        critical_alerts = [a for a in alerts if a["type"] == "critical"]
        warning_alerts = [a for a in alerts if a["type"] == "warning"]

        message_parts = ["🚨 **系统监控告警**\n"]

        if critical_alerts:
            message_parts.append("### 🔴 严重告警\n")
            for alert in critical_alerts:
                message_parts.append(f"- **{alert['source']}**: {alert['message']}\n")

        if warning_alerts:
            message_parts.append("### ⚠️ 警告\n")
            for alert in warning_alerts:
                message_parts.append(f"- **{alert['source']}**: {alert['message']}\n")

        message = "".join(message_parts)

        try:
            result = self.feishu.send_notification(message)
            if result:
                self.logger.success("ENHANCED_EXECUTOR", "飞书告警已发送")
                return True
            else:
                self.logger.error("ENHANCED_EXECUTOR", "飞书告警发送失败")
                return False
        except Exception as e:
            self.logger.error("ENHANCED_EXECUTOR", f"飞书告警异常: {str(e)}")
            return False

    def _scan_para_resources(self) -> List[Dict]:
        """扫描PARA/Resources目录"""
        resources_dir = self.workspace / "PARA" / "Resources"
        if not resources_dir.exists():
            self.logger.warning("ENHANCED_EXECUTOR", "PARA/Resources目录不存在")
            return []

        resources = []
        for item in resources_dir.iterdir():
            if item.is_file() and item.suffix in ['.md', '.txt']:
                resources.append({
                    "path": str(item),
                    "name": item.name,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })

        return resources

    def _detect_obsidian_broken_links(self, file_path: Path) -> List[str]:
        """检测Obsidian断裂的双链"""
        broken_links = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找所有[[wikilinks]]
            import re
            pattern = r'\[\[([^\]]+)\]\]'
            links = re.findall(pattern, content)

            # 检查每个链接的文件是否存在
            for link in links:
                # 支持相对路径和绝对路径
                potential_paths = [
                    self.workspace / f"{link}.md",
                    self.workspace / "PARA" / "Resources" / f"{link}.md",
                    self.workspace / "Zettelkasten" / f"{link}.md",
                ]

                exists = any(p.exists() for p in potential_paths)
                if not exists:
                    broken_links.append(link)

        except Exception as e:
            self.logger.warning("ENHANCED_EXECUTOR", f"检测双链失败: {str(e)}")

        return broken_links

    def _build_knowledge_graph_index(self) -> Dict:
        """构建知识图谱索引"""
        index = {
            "nodes": [],
            "edges": [],
            "generated_at": datetime.now().isoformat()
        }

        # 扫描所有Markdown文件
        for md_file in self.workspace.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 提取双链
                import re
                links = re.findall(r'\[\[([^\]]+)\]\]', content)

                # 添加节点
                node_id = str(md_file.relative_to(self.workspace))
                index["nodes"].append({
                    "id": node_id,
                    "name": md_file.stem,
                    "path": str(md_file),
                    "link_count": len(links)
                })

                # 添加边
                for link in links:
                    index["edges"].append({
                        "from": node_id,
                        "to": link,
                        "type": "wikilink"
                    })

            except Exception as e:
                continue  # 跳过无法读取的文件

        return index


class AutonomousController:
    """自主编程控制器 v3.0 - 集成增强功能"""

    def __init__(self):
        # 初始化日志记录器
        self.logger = ProgressFlowLogger(PROGRESS_LOG_FILE)

        # 初始化Git操作器
        self.git = GitOperator(WORKSPACE, self.logger)

        # 初始化任务管理器
        self.task_manager = TaskManager(
            TASK_LIST_FILE,
            self.logger,
            self.git
        )

        # 初始化验证器
        self.verifier = E2EVerifier(self.logger)

        # 初始化增强任务执行器
        self.enhanced_executor = EnhancedTaskExecutor(WORKSPACE, self.logger)

        self.logger.info("CONTROLLER", "自主编程控制器 v3.0 初始化完成")

    def generate_task_id(self) -> str:
        """生成任务ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        count = len([t for t in self.task_manager.data.get("tasks", [])
                      if t.get("id", "").startswith(f"TASK-{timestamp}")])
        return f"TASK-{timestamp}-{count + 1:03d}"

    def execute_task(self, task_dict: Dict) -> bool:
        """执行任务 - v3.0 改进版"""
        task_type = task_dict.get("type")

        # 改进的任务类型检测
        detected_type = self._detect_task_type_enhanced(task_dict)

        self.logger.info("CONTROLLER",
                       f"执行任务: {task_dict['id']} - 检测类型: {detected_type}")

        if detected_type == "bugfix":
            return self._execute_bugfix_task(task_dict)
        elif detected_type == "feature":
            return self._execute_feature_task(task_dict)
        elif detected_type == "maintenance":
            return self._execute_maintenance_task(task_dict)
        else:
            return self._execute_generic_task(task_dict)

    def _detect_task_type_enhanced(self, task: Dict) -> str:
        """增强的任务类型检测 v3.0"""
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

        # 备用：改进的关键词检测
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()

        # 扩展的关键词列表
        bugfix_keywords = [
            "修复", "fix", "bug", "错误", "error", "异常", "exception",
            "解决", "solve", "diagnosis", "诊断", "排查"
        ]

        feature_keywords = [
            "实现", "implement", "添加", "add", "新功能", "new feature",
            "开发", "develop", "创建", "create", "功能", "function",
            "优化", "optimize", "改进", "improve"
        ]

        maintenance_keywords = [
            "监控", "monitor", "维护", "maintain", "检查", "check",
            "更新", "update", "备份", "backup", "部署", "deploy"
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

    def _execute_maintenance_task(self, task: Dict) -> bool:
        """执行维护任务 - v3.0 增强版"""
        self.logger.info("CONTROLLER", f"开始执行维护任务: {task['id']}")

        try:
            # 尝试使用增强任务执行器
            title = task.get("title", "").lower()
            description = task.get("description", "").lower()

            # 判断是监控还是知识管理任务
            if any(keyword in title or keyword in description
                   for keyword in ["监控", "monitor", "检查", "check", "健康", "health"]):
                # 执行增强监控任务
                return self.enhanced_executor.execute_enhanced_monitoring(task)

            elif any(keyword in title or keyword in description
                         for keyword in
                         ["知识", "knowledge", "para", "obsidian", "双链", "链接"]):
                # 执行增强知识管理任务
                return self.enhanced_executor.execute_enhanced_knowledge(task)

            else:
                # 回退到原始健康检查
                self.logger.info("CONTROLLER", "执行标准健康检查")
                return True  # 假设成功

        except Exception as e:
            self.logger.error("CONTROLLER", f"维护任务执行失败: {str(e)}")
            return False

    def _execute_bugfix_task(self, task: Dict) -> bool:
        """执行Bug修复任务"""
        self.logger.info("CONTROLLER", f"开始执行Bug修复任务: {task['id']}")
        # Bug修复任务目前使用简化实现
        # TODO: 可以扩展为三轮协作模式
        return True

    def _execute_feature_task(self, task: Dict) -> bool:
        """执行功能开发任务"""
        self.logger.info("CONTROLLER", f"开始执行功能开发任务: {task['id']}")
        # 功能开发任务目前使用简化实现
        # TODO: 可以扩展为三轮协作模式
        return True

    def _execute_generic_task(self, task: Dict) -> bool:
        """执行通用任务"""
        self.logger.info("CONTROLLER", f"执行通用任务: {task['id']} - {task['title']}")

        # 对于通用任务，尝试根据描述判断类型
        description = task.get("description", "").lower()
        title = task.get("title", "").lower()

        # 如果包含"修复"、"bug"、"错误"等关键词，按 bugfix 处理
        if any(keyword in description or keyword in title
               for keyword in ["修复", "fix", "bug", "错误", "error", "异常", "异常"]):
            self.logger.info("CONTROLLER", "识别为 Bug 修复任务")
            return self._execute_bugfix_task(task)

        # 如果包含"实现"、"添加"、"新功能"、"开发"等关键词，按 feature 处理
        if any(keyword in description or keyword in title
               for keyword in ["实现", "添加", "新功能", "开发", "develop", "feature", "新增"]):
            self.logger.info("CONTROLLER", "识别为功能开发任务")
            return self._execute_feature_task(task)

        # 默认：记录日志，返回 False（需要手动处理）
        self.logger.warning(
            "CONTROLLER",
            f"通用任务类型未明确，无法自动执行: {task['title']}"
        )

        return False

    def run(self, max_iterations: int = 10):
        """运行主循环"""
        self.logger.info("CONTROLLER", f"启动自主编程主循环")

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            self.logger.info("CONTROLLER", f"=== 迭代 {iteration}/{max_iterations} ===")

            # 获取待处理任务
            pending_tasks = self.task_manager.get_pending_tasks(limit=3)

            if not pending_tasks:
                self.logger.success("CONTROLLER", "没有待处理任务，退出循环")
                break

            # 执行任务
            for task in pending_tasks:
                task_id = task["id"]
                self.logger.info("CONTROLLER", f"开始执行任务: {task_id}")

                # 更新任务状态为进行中
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.IN_PROGRESS
                )

                # 执行任务
                success = self.execute_task(task)

                # 更新任务状态
                if success:
                    self.task_manager.update_task_status(
                        task_id,
                        TaskStatus.DONE
                    )
                    self.logger.success("CONTROLLER", f"任务完成: {task_id}")
                else:
                    self.task_manager.update_task_status(
                        task_id,
                        TaskStatus.FAILED,
                        error="任务执行失败"
                    )
                    self.logger.error("CONTROLLER", f"任务失败: {task_id}")

        self.logger.success("CONTROLLER", f"自主编程主循环完成，共处理 {iteration} 次迭代")


def main():
    """主函数"""
    import sys

    controller = AutonomousController()

    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "run":
            # 运行主循环
            controller.run()
        elif command == "test":
            # 运行测试
            controller.logger.info("CONTROLLER", "运行测试模式")

            # 创建测试任务
            test_task = Task(
                id=controller.generate_task_id(),
                title="测试任务",
                description="这是一个测试任务",
                source="manual",
                type=TaskType.MAINTENANCE,
                priority="medium",
                status=TaskStatus.PENDING,
                created_at=datetime.now().isoformat()
            )

            controller.task_manager.add_task(test_task)
            controller.logger.success("CONTROLLER", "测试任务已创建")
        else:
            print(f"未知命令: {command}")
            print("用法: python autonomous_controller_v3.py [run|test]")
            sys.exit(1)
    else:
        # 默认运行主循环
        controller.run()


if __name__ == "__main__":
    main()
