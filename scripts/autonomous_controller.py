#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自主编程控制器 v2.0 (Autonomous Programming Controller)
GLM-5 增强版

核心特性:
- task_list.json 结构化任务管理
- progress_flow.log 执行日志
- Commit-per-Task 精确回滚
- 上下文管理 (定期压缩)
- 端到端验证 (E2E Testing)
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
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import traceback

# 配置
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
TASK_LIST_FILE = WORKSPACE / ".task_list.json"
PROGRESS_LOG_FILE = WORKSPACE / "logs" / "progress_flow.log"
STATE_DIR = WORKSPACE / ".maintenance_state"
CONTEXT_FILE = STATE_DIR / "context.json"


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
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"


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
    """端到端验证器"""

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
                [str(script_path), "check"],  # 假设支持 check 模式
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
        """验证任务完成情况"""
        task_type = task.get("type")

        if task_type == TaskType.BUGFIX.value:
            # 对于 Bug 修复，验证问题是否解决
            return self._verify_bug_fixed(task)
        elif task_type == TaskType.FEATURE.value:
            # 对于新功能，验证功能是否工作
            return self._verify_feature_works(task)
        else:
            # 对于其他类型，进行基本验证
            return self._verify_basic(task)

    def _verify_bug_fixed(self, task: Dict) -> Tuple[bool, str]:
        """验证 Bug 已修复"""
        # 这里需要根据具体 Bug 实现
        # 示例：运行健康检查
        result = subprocess.run(
            [WORKSPACE / "scripts" / "auto_maintain_v2.sh", "check"],
            capture_output=True,
            timeout=60
        )

        if result.returncode == 0:
            return True, "健康检查通过"
        else:
            return False, "健康检查失败"

    def _verify_feature_works(self, task: Dict) -> Tuple[bool, str]:
        """验证新功能工作"""
        # 这里需要根据具体功能实现
        return True, "功能验证通过（占位）"

    def _verify_basic(self, task: Dict) -> Tuple[bool, str]:
        """基本验证"""
        # 检查是否有关联的 Git 提交
        if "git_commit" in task:
            return True, f"任务已完成，提交: {task['git_commit'][:7]}"
        else:
            return False, "任务未关联 Git 提交"


class ContextManager:
    """上下文管理器"""

    def __init__(
        self,
        context_file: Path,
        logger: ProgressFlowLogger,
        compress_every: int = 5,
        compress_minutes: int = 30
    ):
        self.context_file = context_file
        self.logger = logger
        self.compress_every = compress_every
        self.compress_minutes = compress_minutes
        self.task_count = 0
        self.last_compress_time = datetime.now()
        self.context = self._load_context()

    def _load_context(self) -> Dict:
        """加载上下文"""
        if self.context_file.exists():
            with open(self.context_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {
                "session_start": datetime.now().isoformat(),
                "tasks_completed": 0,
                "key_decisions": [],
                "lessons_learned": [],
                "compressed_contexts": []
            }

    def _save_context(self):
        """保存上下文"""
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.context_file, "w", encoding="utf-8") as f:
            json.dump(self.context, f, indent=2, ensure_ascii=False)

    def should_compress(self) -> bool:
        """判断是否应该压缩上下文"""
        # 条件1: 任务数量达到阈值
        if self.task_count >= self.compress_every:
            return True

        # 条件2: 时间达到阈值
        elapsed = datetime.now() - self.last_compress_time
        if elapsed.total_seconds() >= self.compress_minutes * 60:
            return True

        return False

    def add_key_decision(self, decision: str):
        """添加关键决策"""
        self.context["key_decisions"].append({
            "timestamp": datetime.now().isoformat(),
            "decision": decision
        })
        self._save_context()

    def add_lesson_learned(self, lesson: str):
        """添加经验教训"""
        self.context["lessons_learned"].append({
            "timestamp": datetime.now().isoformat(),
            "lesson": lesson
        })
        self._save_context()

    def compress(self) -> Dict:
        """压缩上下文"""
        compressed = {
            "compression_time": datetime.now().isoformat(),
            "session_summary": {
                "tasks_completed": self.context.get("tasks_completed", 0),
                "session_duration": str(
                    datetime.now() - datetime.fromisoformat(
                        self.context["session_start"]
                    )
                )
            },
            "key_decisions": self.context["key_decisions"][-10:],  # 保留最近10个
            "lessons_learned": self.context["lessons_learned"][-10:]  # 保留最近10个
        }

        # 保存压缩历史
        self.context["compressed_contexts"].append(compressed)

        # 重置计数器
        self.task_count = 0
        self.last_compress_time = datetime.now()

        # 清空旧数据（保留压缩历史）
        self.context["key_decisions"] = []
        self.context["lessons_learned"] = []

        self._save_context()

        self.logger.info(
            "CONTEXT-MANAGER",
            f"Context compressed. Session summary: {compressed['session_summary']}"
        )

        return compressed


class AutonomousController:
    """自主编程控制器主类"""

    def __init__(self):
        # 初始化日志
        self.logger = ProgressFlowLogger(PROGRESS_LOG_FILE)

        # 初始化 Git 操作器
        self.git = GitOperator(WORKSPACE, self.logger)

        # 初始化任务管理器
        self.task_manager = TaskManager(TASK_LIST_FILE, self.logger, self.git)

        # 初始化 E2E 验证器
        self.verifier = E2EVerifier(self.logger)

        # 初始化上下文管理器
        self.context = ContextManager(CONTEXT_FILE, self.logger)

        self.logger.info("CONTROLLER", "自主编程控制器 v2.0 初始化完成")

    def generate_task_id(self) -> str:
        """生成任务 ID"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        counter = len(self.task_manager.data["tasks"]) + 1
        return f"TASK-{date_str}-{counter:03d}"

    def run(self):
        """主循环"""
        self.logger.info("CONTROLLER", "启动自主编程主循环")

        while True:
            try:
                # 获取待处理任务
                pending_tasks = self.task_manager.get_pending_tasks(limit=5)

                if not pending_tasks:
                    self.logger.info(
                        "CONTROLLER",
                        "没有待处理任务，等待 30 秒..."
                    )
                    time.sleep(30)
                    continue

                # 处理任务
                for task_dict in pending_tasks:
                    self.execute_task(task_dict)

                    # 检查是否需要压缩上下文
                    if self.context.should_compress():
                        self.context.compress()

                # 短暂休眠
                time.sleep(5)

            except KeyboardInterrupt:
                self.logger.info("CONTROLLER", "收到中断信号，退出")
                break
            except Exception as e:
                self.logger.error(
                    "CONTROLLER",
                    f"主循环异常: {traceback.format_exc()}"
                )
                time.sleep(10)

    def execute_task(self, task_dict: Dict):
        """执行单个任务"""
        task_id = task_dict["id"]
        task_title = task_dict["title"]

        self.logger.info("CONTROLLER", f"开始执行任务: {task_id} - {task_title}")

        # 更新任务状态为进行中
        self.task_manager.update_task_status(task_id, TaskStatus.IN_PROGRESS)

        try:
            # 根据 task_type 执行不同的处理逻辑
            task_type = task_dict.get("type")

            if task_type == TaskType.MAINTENANCE.value:
                success = self._execute_maintenance_task(task_dict)
            elif task_type == TaskType.BUGFIX.value:
                success = self._execute_bugfix_task(task_dict)
            elif task_type == TaskType.FEATURE.value:
                success = self._execute_feature_task(task_dict)
            else:
                success = self._execute_generic_task(task_dict)

            # 更新任务状态
            if success:
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.DONE,
                    commit_hash=self.git.get_current_commit()
                )
                self.logger.success("CONTROLLER", f"任务完成: {task_id}")
            else:
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error="任务执行失败"
                )
                self.logger.error("CONTROLLER", f"任务失败: {task_id}")

        except Exception as e:
            self.task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e)
            )
            self.logger.error(
                "CONTROLLER",
                f"任务异常: {task_id} - {traceback.format_exc()}"
            )

    def _execute_maintenance_task(self, task: Dict) -> bool:
        """执行维护任务"""
        self.logger.info("CONTROLLER", "执行维护任务")

        # 调用 auto_maintain_v2.sh
        result = subprocess.run(
            [WORKSPACE / "scripts" / "auto_maintain_v2.sh", "run"],
            capture_output=True,
            timeout=300,  # 5 分钟超时
            cwd=WORKSPACE
        )

        if result.returncode == 0:
            # Git 提交
            commit_hash = self.git.commit(
                f"chore(maintenance): {task['title']}"
            )

            # E2E 验证
            verified, message = self.verifier.verify_task_completion(task)

            if verified:
                self.logger.success("CONTROLLER", f"维护任务验证通过: {message}")
                return True
            else:
                self.logger.warning("CONTROLLER", f"维护任务验证失败: {message}")
                return False
        else:
            self.logger.error(
                "CONTROLLER",
                f"维护脚本执行失败: {result.stderr.decode()}"
            )
            return False

    def _execute_bugfix_task(self, task: Dict) -> bool:
        """执行 Bug 修复任务"""
        self.logger.info("CONTROLLER", "执行 Bug 修复任务")

        # TODO: 实现智能 Bug 修复逻辑
        # 这里可以调用 GLM-4.7/5 进行代码生成

        # 占位实现
        self.logger.warning(
            "CONTROLLER",
            "Bug 修复任务暂未实现完整逻辑（占位）"
        )

        return False

    def _execute_feature_task(self, task: Dict) -> bool:
        """执行功能开发任务"""
        self.logger.info("CONTROLLER", "执行功能开发任务")

        # TODO: 实现自主编码逻辑
        # 这里可以调用 GLM-5 Coding Plan

        # 占位实现
        self.logger.warning(
            "CONTROLLER",
            "功能开发任务暂未实现完整逻辑（占位）"
        )

        return False

    def _execute_generic_task(self, task: Dict) -> bool:
        """执行通用任务"""
        self.logger.info("CONTROLLER", "执行通用任务")

        # 占位实现
        return False


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
            print("用法: python autonomous_controller.py [run|test]")
            sys.exit(1)
    else:
        # 默认运行主循环
        controller.run()


if __name__ == "__main__":
    main()
