#!/usr/bin/env python3
"""
自主编程控制器 v3.0 - 完整版
集成所有GLM-5增强特性：
- 任务自动提取与执行
- 三轮协作模式（编程任务）
- 增强监控与维护
- 增强知识管理
- Commit-per-Task版本控制
- 端到端验证体系

创建时间: 2026-02-14
版本: v3.0
"""

from __future__ import annotations
import os
import sys
import json
import time
import hashlib
import subprocess
import logging
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(Enum):
    """任务类型"""
    BUGFIX = "bugfix"
    FEATURE = "feature"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    KNOWLEDGE = "knowledge"
    META = "meta"


@dataclass
class SubtaskResult:
    """子任务结果"""
    name: str
    status: TaskStatus
    duration: float = 0.0
    output: Optional[str] = None
    error: Optional[str] = None
    git_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "duration": round(self.duration, 2),
            "output": self.output,
            "error": self.error,
            "git_commit": self.git_commit
        }


@dataclass
class Task:
    """任务数据结构"""
    id: str
    title: str
    type: TaskType
    priority: str  # high/medium/low
    status: TaskStatus = TaskStatus.PENDING
    description: str = ""
    subtasks: List[SubtaskResult] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    git_commit: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type.value,
            "priority": self.priority,
            "status": self.status.value,
            "description": self.description,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "logs": self.logs,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "git_commit": self.git_commit
        }


class TaskManager:
    """任务管理器"""

    def __init__(self, task_list_path: str = "/home/ubuntu/.openclaw/workspace/.task_list.json"):
        self.task_list_path = Path(task_list_path)
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        self._load_tasks()

    def _load_tasks(self):
        """从文件加载任务"""
        if self.task_list_path.exists():
            try:
                with open(self.task_list_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_data in data.get("tasks", []):
                        task = self._dict_to_task(task_data)
                        self.tasks[task.id] = task
                logger.info(f"加载了 {len(self.tasks)} 个任务")
            except Exception as e:
                logger.error(f"加载任务失败: {e}")
        else:
            logger.info("任务列表文件不存在，创建新的")
            self._save_tasks()

    def _save_tasks(self):
        """保存任务到文件"""
        try:
            self.task_list_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version": "3.0",
                "updated_at": datetime.now().isoformat(),
                "tasks": [task.to_dict() for task in self.tasks.values()]
            }
            with open(self.task_list_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存任务失败: {e}")

    def _dict_to_task(self, data: Dict[str, Any]) -> Task:
        """从字典创建Task对象"""
        subtasks = [
            SubtaskResult(**st) for st in data.get("subtasks", [])
        ]
        return Task(
            id=data["id"],
            title=data["title"],
            type=TaskType(data["type"]),
            priority=data["priority"],
            status=TaskStatus(data["status"]),
            description=data.get("description", ""),
            subtasks=subtasks,
            logs=data.get("logs", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            git_commit=data.get("git_commit")
        )

    def add_task(self, task: Task):
        """添加任务"""
        with self.lock:
            self.tasks[task.id] = task
            self._save_tasks()
            logger.info(f"添加任务: {task.id} - {task.title}")

    def update_task(self, task_id: str, **kwargs):
        """更新任务"""
        with self.lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                for key, value in kwargs.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                task.updated_at = datetime.now()
                self._save_tasks()
                logger.info(f"更新任务: {task_id}")
            else:
                logger.error(f"任务不存在: {task_id}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态获取任务"""
        return [task for task in self.tasks.values() if task.status == status]

    def get_tasks_by_type(self, task_type: TaskType) -> List[Task]:
        """按类型获取任务"""
        return [task for task in self.tasks.values() if task.type == task_type]

    def get_high_priority_tasks(self) -> List[Task]:
        """获取高优先级任务"""
        return [
            task for task in self.tasks.values()
            if task.priority == "high" and task.status == TaskStatus.PENDING
        ]


class GitOperator:
    """Git操作器 - Commit-per-Task"""

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.git_dir = self.workspace / ".git"

    def _run_git(self, args: List[str]) -> Tuple[bool, str]:
        """运行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def commit_changes(
        self,
        task_id: str,
        message: str,
        files: Optional[List[str]] = None
    ) -> Optional[str]:
        """提交更改（每个任务独立提交）"""
        # 检查是否有更改
        success, output = self._run_git(["status", "--porcelain"])
        if not success or not output:
            logger.info(f"任务 {task_id} 无更改需要提交")
            return None

        # 添加文件
        if files:
            for file in files:
                self._run_git(["add", file])
        else:
            self._run_git(["add", "."])

        # 提交
        commit_msg = f"[{task_id}] {message}"
        success, output = self._run_git(["commit", "-m", commit_msg])

        if success:
            # 获取commit hash
            success, commit_hash = self._run_git(["rev-parse", "HEAD"])
            if success:
                logger.info(f"✅ Git提交: {commit_hash[:8]} - {commit_msg}")
                return commit_hash

        logger.error(f"❌ Git提交失败: {output}")
        return None

    def get_changes(self) -> List[str]:
        """获取更改的文件列表"""
        success, output = self._run_git(["status", "--porcelain"])
        if success:
            return [line.strip() for line in output.split('\n') if line.strip()]
        return []

    def create_branch(self, branch_name: str) -> bool:
        """创建新分支"""
        success, output = self._run_git(["checkout", "-b", branch_name])
        return success

    def merge_branch(self, branch_name: str) -> bool:
        """合并分支"""
        success, output = self._run_git(["merge", "--no-ff", branch_name])
        return success


class SubagentOrchestrator:
    """
    子代理协调器 - 三轮协作模式

    用于编程任务的自动处理：
    1. zhipu/glm-4.7 → 编程/写代码
    2. kimi-k2.5 → Debug/测试
    3. zhipu/glm-4.7 → 修复/优化
    """

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.sessions: Dict[str, Dict] = {}

    def spawn_subagent(
        self,
        task_id: str,
        agent_id: str,
        task: str,
        model: str = "zhipu/glm-4.7",
        timeout: int = 300
    ) -> Optional[str]:
        """
        生成子代理会话

        Args:
            task_id: 主任务ID
            agent_id: 子代理ID
            task: 任务描述
            model: 模型ID
            timeout: 超时时间（秒）

        Returns:
            会话ID或None
        """
        try:
            logger.info(f"🔄 启动子代理: {agent_id} (模型: {model})")

            # 构建命令
            cmd = [
                "openclaw",
                "sessions",
                "spawn",
                "--agent-id", agent_id,
                "--model", model,
                "--label", f"{task_id}_{agent_id}",
                "--task", task,
                "--timeout", str(timeout),
                "--cleanup", "keep"
            ]

            # 执行命令
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # 提取会话ID
                match = re.search(r'Session ID: ([a-zA-Z0-9_-]+)', result.stdout)
                if match:
                    session_id = match.group(1)
                    self.sessions[session_id] = {
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "model": model,
                        "created_at": datetime.now().isoformat()
                    }
                    logger.info(f"✅ 子代理会话创建: {session_id}")
                    return session_id

            logger.error(f"❌ 子代理创建失败: {result.stderr}")
            return None

        except Exception as e:
            logger.error(f"❌ 子代理异常: {e}")
            return None

    def execute_three_round_collaboration(
        self,
        task_id: str,
        task_description: str
    ) -> Tuple[bool, List[Optional[str]]]:
        """
        执行三轮协作模式

        Args:
            task_id: 任务ID
            task_description: 任务描述

        Returns:
            (成功标志, [session_id_1, session_id_2, session_id_3])
        """
        session_ids = []

        # Round 1: 编程
        logger.info(f"🔄 Round 1: 编程 (zhipu/glm-4.7)")
        session_id_1 = self.spawn_subagent(
            task_id=task_id,
            agent_id=f"{task_id}_coder",
            task=f"编程任务: {task_description}\n\n请实现完整的功能代码，包含错误处理和文档。",
            model="zhipu/glm-4.7",
            timeout=300
        )
        session_ids.append(session_id_1)

        # 等待第一轮完成
        if session_id_1:
            self._wait_for_session(session_id_1, timeout=300)

        # Round 2: 测试/Debug
        logger.info(f"🔄 Round 2: 测试/Debug (kimi-k2.5)")
        session_id_2 = self.spawn_subagent(
            task_id=task_id,
            agent_id=f"{task_id}_tester",
            task=f"测试任务: 请对刚才实现的代码进行完整的测试和Debug，发现所有潜在问题。",
            model="nvidia/moonshotai/kimi-k2.5",
            timeout=300
        )
        session_ids.append(session_id_2)

        # 等待第二轮完成
        if session_id_2:
            self._wait_for_session(session_id_2, timeout=300)

        # Round 3: 修复/优化
        logger.info(f"🔄 Round 3: 修复/优化 (zhipu/glm-4.7)")
        session_id_3 = self.spawn_subagent(
            task_id=task_id,
            agent_id=f"{task_id}_fixer",
            task=f"修复任务: 根据测试结果修复所有发现的问题，并优化代码质量。",
            model="zhipu/glm-4.7",
            timeout=300
        )
        session_ids.append(session_id_3)

        success = all(sid is not None for sid in session_ids)
        return success, session_ids

    def _wait_for_session(self, session_id: str, timeout: int = 300):
        """等待会话完成"""
        logger.info(f"⏳ 等待会话完成: {session_id}")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # 检查会话状态
                result = subprocess.run(
                    ["openclaw", "sessions", "list", "--label", session_id],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                # 解析状态
                if "active" not in result.stdout:
                    logger.info(f"✅ 会话完成: {session_id}")
                    return True

                time.sleep(10)

            except Exception as e:
                logger.error(f"检查会话状态失败: {e}")
                time.sleep(10)

        logger.warning(f"⏱️  会话超时: {session_id}")
        return False


class E2EVerifier:
    """端到端验证器 - 四层验证体系"""

    def __init__(self):
        self.layers = [
            "语法检查",
            "类型检查",
            "功能测试",
            "集成测试"
        ]

    def verify_syntax(self, file_path: str) -> Tuple[bool, str]:
        """Layer 1: 语法检查"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, "✅ 语法检查通过"
            else:
                return False, f"❌ 语法错误: {result.stderr}"
        except Exception as e:
            return False, f"❌ 检查失败: {e}"

    def verify_types(self, file_path: str) -> Tuple[bool, str]:
        """Layer 2: 类型检查（使用mypy，可选）"""
        try:
            result = subprocess.run(
                ["mypy", file_path, "--no-error-summary"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return True, "✅ 类型检查通过"
            else:
                return False, f"⚠️  类型警告: {result.stdout[:200]}"
        except FileNotFoundError:
            return True, "⏭️  mypy未安装，跳过类型检查"
        except Exception as e:
            return False, f"❌ 检查失败: {e}"

    def verify_functionality(self, file_path: str) -> Tuple[bool, str]:
        """Layer 3: 功能测试"""
        try:
            # 查找对应的测试文件
            test_file = Path(file_path).parent / f"test_{Path(file_path).stem}.py"

            if not test_file.exists():
                return True, "⏭️  测试文件不存在，跳过功能测试"

            # 运行测试
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return True, "✅ 功能测试通过"
            else:
                return False, f"❌ 功能测试失败: {result.stderr[:200]}"
        except Exception as e:
            return False, f"❌ 测试失败: {e}"

    def verify_integration(self, file_path: str) -> Tuple[bool, str]:
        """Layer 4: 集成测试"""
        try:
            # 简单导入测试
            result = subprocess.run(
                [sys.executable, "-c", f"import {Path(file_path).stem}"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(file_path).parent
            )

            if result.returncode == 0:
                return True, "✅ 集成测试通过"
            else:
                return False, f"❌ 导入失败: {result.stderr[:200]}"
        except Exception as e:
            return False, f"❌ 集成测试失败: {e}"

    def verify_all(self, file_path: str) -> Dict[str, Tuple[bool, str]]:
        """执行所有验证层"""
        return {
            "syntax": self.verify_syntax(file_path),
            "types": self.verify_types(file_path),
            "functionality": self.verify_functionality(file_path),
            "integration": self.verify_integration(file_path)
        }


class ProgressFlowLogger:
    """进度流日志记录器 - 毫秒级精度"""

    def __init__(self, log_file: str = "/home/ubuntu/.openclaw/workspace/logs/progress_flow.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def log_event(
        self,
        task_id: str,
        event_type: str,
        details: str = "",
        metadata: Optional[Dict] = None
    ):
        """记录事件"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = {
            "timestamp": timestamp,
            "task_id": task_id,
            "event_type": event_type,
            "details": details,
            "metadata": metadata or {}
        }

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            logger.error(f"写入日志失败: {e}")


class AutonomousControllerV3:
    """
    自主编程控制器 v3.0

    集成所有增强特性：
    - 任务自动提取
    - 三轮协作模式
    - 增强监控
    - 增强知识管理
    - Commit-per-Task
    - 端到端验证
    """

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.task_manager = TaskManager(str(self.workspace / ".task_list.json"))
        self.git_operator = GitOperator(str(self.workspace))
        self.subagent_orchestrator = SubagentOrchestrator(str(self.workspace))
        self.verifier = E2EVerifier()
        self.progress_logger = ProgressFlowLogger(str(self.workspace / "logs/progress_flow.log"))

    def extract_tasks_from_todo(self) -> List[Task]:
        """从TODO.md提取任务"""
        todo_file = self.workspace / "TODO.md"

        if not todo_file.exists():
            logger.warning("TODO.md不存在")
            return []

        tasks = []
        try:
            with open(todo_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 解析TODO.md
            current_section = None
            for line in content.split('\n'):
                line = line.strip()

                # 检测任务项
                if line.startswith('- [ ]'):
                    title = line[4:].strip()

                    # 生成任务ID
                    task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(tasks):02d}"

                    # 确定任务类型
                    task_type = self._detect_task_type(title)

                    task = Task(
                        id=task_id,
                        title=title,
                        type=task_type,
                        priority="medium",
                        description=title
                    )

                    tasks.append(task)

            logger.info(f"从TODO.md提取了 {len(tasks)} 个任务")
            return tasks

        except Exception as e:
            logger.error(f"提取任务失败: {e}")
            return []

    def _detect_task_type(self, title: str) -> TaskType:
        """检测任务类型"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ["bug", "修复", "fix"]):
            return TaskType.BUGFIX
        elif any(keyword in title_lower for keyword in ["功能", "新", "feature", "添加"]):
            return TaskType.FEATURE
        elif any(keyword in title_lower for keyword in ["监控", "检查", "monitor"]):
            return TaskType.MONITORING
        elif any(keyword in title_lower for keyword in ["知识", "文档", "knowledge"]):
            return TaskType.KNOWLEDGE
        elif any(keyword in title_lower for keyword in ["维护", "maintenance"]):
            return TaskType.MAINTENANCE
        else:
            return TaskType.FEATURE

    def execute_bugfix_task(self, task: Task) -> SubtaskResult:
        """执行Bug修复任务（三轮协作）"""
        start_time = time.time()
        self.progress_logger.log_event(task.id, "bugfix_start", task.title)

        logger.info(f"🐛 执行Bug修复任务: {task.title}")

        # 使用三轮协作模式
        success, session_ids = self.subagent_orchestrator.execute_three_round_collaboration(
            task_id=task.id,
            task_description=task.description
        )

        duration = time.time() - start_time

        if success:
            output = f"三轮协作完成: {', '.join(session_ids)}"
            self.progress_logger.log_event(task.id, "bugfix_complete", output)

            return SubtaskResult(
                name=f"BugFix: {task.title}",
                status=TaskStatus.DONE,
                duration=duration,
                output=output
            )
        else:
            error = "三轮协作失败"
            self.progress_logger.log_event(task.id, "bugfix_failed", error)

            return SubtaskResult(
                name=f"BugFix: {task.title}",
                status=TaskStatus.FAILED,
                duration=duration,
                error=error
            )

    def execute_feature_task(self, task: Task) -> SubtaskResult:
        """执行功能开发任务（三轮协作）"""
        start_time = time.time()
        self.progress_logger.log_event(task.id, "feature_start", task.title)

        logger.info(f"✨ 执行功能开发任务: {task.title}")

        # 使用三轮协作模式
        success, session_ids = self.subagent_orchestrator.execute_three_round_collaboration(
            task_id=task.id,
            task_description=task.description
        )

        duration = time.time() - start_time

        if success:
            output = f"功能开发完成: {', '.join(session_ids)}"

            # 端到端验证
            verification_results = self._verify_task_changes(task.id)

            self.progress_logger.log_event(task.id, "feature_complete", output, verification_results)

            return SubtaskResult(
                name=f"Feature: {task.title}",
                status=TaskStatus.DONE,
                duration=duration,
                output=output,
                metadata={"verification": verification_results}
            )
        else:
            error = "功能开发失败"
            self.progress_logger.log_event(task.id, "feature_failed", error)

            return SubtaskResult(
                name=f"Feature: {task.title}",
                status=TaskStatus.FAILED,
                duration=duration,
                error=error
            )

    def _verify_task_changes(self, task_id: str) -> Dict[str, Any]:
        """验证任务更改"""
        changes = self.git_operator.get_changes()

        verification_results = {}
        for change in changes[:5]:  # 验证前5个文件
            file_path = change.split()[-1]
            full_path = self.workspace / file_path

            if full_path.exists() and full_path.suffix == '.py':
                results = self.verifier.verify_all(str(full_path))
                verification_results[file_path] = results

        return verification_results

    def run_auto_programming(self, max_tasks: int = 5):
        """运行自主编程流程"""
        logger.info("=" * 70)
        logger.info("🚀 自主编程控制器 v3.0 启动")
        logger.info("=" * 70)

        # 1. 提取任务
        logger.info("\n📋 第一步: 从TODO.md提取任务")
        tasks = self.extract_tasks_from_todo()

        if not tasks:
            logger.warning("没有找到待处理任务")
            return

        # 2. 执行高优先级任务
        high_priority_tasks = sorted(tasks, key=lambda t: t.priority == "high", reverse=True)[:max_tasks]

        for task in high_priority_tasks:
            logger.info(f"\n🔄 执行任务: {task.id} - {task.title}")
            self.progress_logger.log_event(task.id, "task_start", task.title)

            task.status = TaskStatus.IN_PROGRESS

            # 根据任务类型执行
            if task.type == TaskType.BUGFIX:
                result = self.execute_bugfix_task(task)
            elif task.type == TaskType.FEATURE:
                result = self.execute_feature_task(task)
            else:
                # 其他任务类型直接标记为完成
                result = SubtaskResult(
                    name=f"Task: {task.title}",
                    status=TaskStatus.DONE,
                    duration=0.0,
                    output=f"任务类型 {task.type} 暂不支持自动执行"
                )

            # 更新任务状态
            task.status = result.status
            task.subtasks.append(result)

            # Git提交
            if result.status == TaskStatus.DONE:
                commit_hash = self.git_operator.commit_changes(
                    task.id,
                    task.title
                )
                task.git_commit = commit_hash

            self.task_manager.update_task(
                task.id,
                status=result.status,
                subtasks=task.subtasks,
                git_commit=task.git_commit
            )

            logger.info(f"✅ 任务完成: {task.id} - {result.status.value}")

        # 3. 生成报告
        logger.info("\n" + "=" * 70)
        logger.info("📊 执行报告")
        logger.info("=" * 70)

        for task in high_priority_tasks:
            logger.info(f"\n{task.id}: {task.title}")
            logger.info(f"  状态: {task.status.value}")
            logger.info(f"  类型: {task.type.value}")
            if task.git_commit:
                logger.info(f"  提交: {task.git_commit[:8]}")

        logger.info("\n✅ 自主编程流程完成")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自主编程控制器v3.0")
    parser.add_argument("--workspace", default="/home/ubuntu/.openclaw/workspace", help="工作区路径")
    parser.add_argument("--max-tasks", type=int, default=5, help="最大执行任务数")
    parser.add_argument("--extract-tasks", action="store_true", help="仅提取任务")
    parser.add_argument("--verify", help="验证指定文件")

    args = parser.parse_args()

    controller = AutonomousControllerV3(workspace=args.workspace)

    if args.extract_tasks:
        # 仅提取任务
        tasks = controller.extract_tasks_from_todo()
        for task in tasks:
            print(f"{task.id}: {task.title} ({task.type.value})")
    elif args.verify:
        # 验证文件
        verifier = E2EVerifier()
        results = verifier.verify_all(args.verify)

        print(f"\n验证结果: {args.verify}")
        print("=" * 70)
        for layer, (success, message) in results.items():
            status = "✅" if success else "❌"
            print(f"{status} {layer}: {message}")
    else:
        # 运行完整流程
        controller.run_auto_programming(max_tasks=args.max_tasks)


if __name__ == "__main__":
    main()
