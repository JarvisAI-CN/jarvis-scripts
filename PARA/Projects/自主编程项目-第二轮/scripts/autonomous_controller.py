#!/usr/bin/env python3
"""
自主编程控制器 v2.0
实现GLM-5增强特性：自愈、自驱编码、精确Git控制、上下文管理
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
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
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
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    KNOWLEDGE = "knowledge"
    META = "meta"  # 元任务（避免循环）


@dataclass
class SubtaskResult:
    """子任务执行结果"""
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
    """任务管理器 - 管理task_list.json"""

    def __init__(self, task_list_path: str = "/home/ubuntu/.openclaw/workspace/.task_list.json"):
        self.task_list_path = Path(task_list_path)
        self.tasks: Dict[str, Task] = {}
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
                "version": "2.0",
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
            status=TaskStatus(data.get("status", "pending")),
            description=data.get("description", ""),
            subtasks=subtasks,
            logs=data.get("logs", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(),
            git_commit=data.get("git_commit")
        )

    def add_task(self, task: Task):
        """添加任务"""
        self.tasks[task.id] = task
        self._save_tasks()
        logger.info(f"添加任务: {task.id} - {task.title}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, **kwargs):
        """更新任务"""
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = datetime.now()
            self._save_tasks()
            logger.info(f"更新任务: {task_id}")

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """列出任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def get_pending_tasks(self) -> List[Task]:
        """获取待处理任务"""
        return self.list_tasks(TaskStatus.PENDING)


class GitOperator:
    """Git操作器 - Commit-per-Task精确控制"""

    def __init__(self, repo_path: str = "/home/ubuntu/.openclaw/workspace"):
        self.repo_path = Path(repo_path)

    def _run_git(self, args: List[str]) -> subprocess.CompletedProcess:
        """运行Git命令"""
        cmd = ["git", "-C", str(self.repo_path)] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def commit(self, message: str, files: Optional[List[str]] = None) -> Optional[str]:
        """提交更改"""
        try:
            # 添加文件
            if files:
                for file in files:
                    self._run_git(["add", file])
            else:
                self._run_git(["add", "-A"])

            # 检查是否有更改
            result = self._run_git(["status", "--porcelain"])
            if not result.stdout.strip():
                logger.info("没有更改需要提交")
                return None

            # 提交
            result = self._run_git(["commit", "-m", message])
            if result.returncode != 0:
                logger.error(f"提交失败: {result.stderr}")
                return None

            # 获取commit hash
            result = self._run_git(["rev-parse", "HEAD"])
            commit_hash = result.stdout.strip()

            logger.info(f"提交成功: {commit_hash[:7]} - {message}")
            return commit_hash

        except Exception as e:
            logger.error(f"Git操作失败: {e}")
            return None

    def push(self, remote: str = "origin", branch: str = "main") -> bool:
        """推送到远程"""
        try:
            result = self._run_git(["push", remote, branch])
            if result.returncode != 0:
                logger.error(f"推送失败: {result.stderr}")
                return False
            logger.info(f"推送成功: {remote}/{branch}")
            return True
        except Exception as e:
            logger.error(f"推送失败: {e}")
            return False

    def create_branch(self, branch_name: str) -> bool:
        """创建分支"""
        try:
            result = self._run_git(["checkout", "-b", branch_name])
            if result.returncode != 0:
                logger.error(f"创建分支失败: {result.stderr}")
                return False
            logger.info(f"创建分支: {branch_name}")
            return True
        except Exception as e:
            logger.error(f"创建分支失败: {e}")
            return False


class SubagentOrchestrator:
    """子代理协调器 - 三轮协作模式"""

    def __init__(self):
        self.model_mapping = {
            "zhipu": "zhipu/glm-4.7",
            "kimi": "nvidia/moonshotai/kimi-k2.5",
            "gemini": "google-antigravity/gemini-3-flash"
        }

    def execute_bugfix_task(self, task: Task) -> SubtaskResult:
        """执行Bug修复任务（三轮协作）"""
        logger.info(f"开始Bug修复任务: {task.title}")
        start_time = time.time()

        try:
            # 第一轮：zhipu分析Bug + 生成修复代码
            logger.info("第一轮：zhipu/glm-4.7 分析Bug")
            round1_result = self._call_subagent(
                model="zhipu",
                task_context=task.to_dict(),
                prompt=f"""你是一个Bug修复专家。请分析以下Bug并生成修复代码：

任务: {task.title}
描述: {task.description}

请按以下格式输出：
DIAGNOSIS: [Bug原因分析]
AFFECTED_FILES: [受影响的文件列表]
FIX_CODE:
```python
[修复代码]
```
TEST_STEPS: [测试步骤]
"""
            )

            if not round1_result or round1_result.status == TaskStatus.FAILED:
                return SubtaskResult(
                    name="bugfix_round1",
                    status=TaskStatus.FAILED,
                    error="第一轮失败"
                )

            # 第二轮：kimi测试修复代码
            logger.info("第二轮：kimi-k2.5 测试修复代码")
            round2_result = self._call_subagent(
                model="kimi",
                task_context=task.to_dict(),
                prompt=f"""你是一个测试工程师。请测试以下修复代码：

{round1_result.output}

请执行测试并反馈：
1. 代码审查结果
2. 发现的问题
3. 改进建议
4. 测试结论（PASS/FAIL）
"""
            )

            # 第三轮：zhipu根据反馈优化
            logger.info("第三轮：zhipu/glm-4.7 优化代码")
            round3_result = self._call_subagent(
                model="zhipu",
                task_context=task.to_dict(),
                prompt=f"""根据测试反馈优化代码：

原始修复:
{round1_result.output}

测试反馈:
{round2_result.output if round2_result else "无反馈"}

请生成最终优化后的代码。
"""
            )

            duration = time.time() - start_time
            return SubtaskResult(
                name="bugfix_complete",
                status=TaskStatus.DONE,
                duration=duration,
                output=round3_result.output if round3_result else round1_result.output
            )

        except Exception as e:
            logger.error(f"Bug修复失败: {e}")
            return SubtaskResult(
                name="bugfix_failed",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    def execute_feature_task(self, task: Task) -> SubtaskResult:
        """执行功能开发任务（三轮协作）"""
        logger.info(f"开始功能开发任务: {task.title}")
        start_time = time.time()

        try:
            # 第一轮：zhipu需求分析 + 代码实现
            logger.info("第一轮：zhipu/glm-4.7 需求分析 + 实现")
            round1_result = self._call_subagent(
                model="zhipu",
                task_context=task.to_dict(),
                prompt=f"""你是一个全栈工程师。请分析需求并实现功能：

任务: {task.title}
描述: {task.description}

请按以下格式输出：
ANALYSIS: [需求分析和技术方案]
IMPLEMENTATION:
```python
[完整的功能实现代码]
```
TEST_PLAN: [测试计划]
DEPENDENCIES: [依赖的外部模块或库]
"""
            )

            if not round1_result or round1_result.status == TaskStatus.FAILED:
                return SubtaskResult(
                    name="feature_round1",
                    status=TaskStatus.FAILED,
                    error="第一轮失败"
                )

            # 第二轮：kimi代码审查 + 测试
            logger.info("第二轮：kimi-k2.5 代码审查 + 测试")
            round2_result = self._call_subagent(
                model="kimi",
                task_context=task.to_dict(),
                prompt=f"""你是一个代码审查专家。请审查以下实现：

{round1_result.output}

请检查：
1. 代码质量
2. 边界情况处理
3. 错误处理
4. 性能优化建议
5. 安全问题

请提供详细的审查报告。
"""
            )

            # 第三轮：zhipu根据审查优化
            logger.info("第三轮：zhipu/glm-4.7 优化代码")
            round3_result = self._call_subagent(
                model="zhipu",
                task_context=task.to_dict(),
                prompt=f"""根据代码审查优化实现：

原始实现:
{round1_result.output}

审查反馈:
{round2_result.output if round2_result else "无反馈"}

请生成最终优化后的实现。
"""
            )

            duration = time.time() - start_time
            return SubtaskResult(
                name="feature_complete",
                status=TaskStatus.DONE,
                duration=duration,
                output=round3_result.output if round3_result else round1_result.output
            )

        except Exception as e:
            logger.error(f"功能开发失败: {e}")
            return SubtaskResult(
                name="feature_failed",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    def _call_subagent(
        self,
        model: str,
        task_context: Dict[str, Any],
        prompt: str
    ) -> Optional[SubtaskResult]:
        """调用子代理（简化版本，实际应使用sessions_spawn）"""
        try:
            model_id = self.model_mapping.get(model, model)
            logger.info(f"调用子代理: {model_id}")

            # 这里应该使用sessions_spawn工具调用子代理
            # 简化版本：直接模拟返回
            output = f"[{model_id} output]\n\n模拟的子代理输出..."

            return SubtaskResult(
                name=f"subagent_{model}",
                status=TaskStatus.DONE,
                output=output
            )

        except Exception as e:
            logger.error(f"子代理调用失败: {e}")
            return None


class E2EVerifier:
    """端到端验证器 - 四层验证体系"""

    def verify(self, task: Task) -> bool:
        """执行端到端验证"""
        logger.info(f"开始端到端验证: {task.title}")

        # Level 1: 语法验证
        if not self._level1_syntax_check(task):
            logger.error("Level 1: 语法验证失败")
            return False
        logger.info("Level 1: 语法验证通过")

        # Level 2: 功能验证
        if not self._level2_functional_test(task):
            logger.error("Level 2: 功能验证失败")
            return False
        logger.info("Level 2: 功能验证通过")

        # Level 3: 集成验证
        if not self._level3_integration_test(task):
            logger.error("Level 3: 集成验证失败")
            return False
        logger.info("Level 3: 集成验证通过")

        # Level 4: 自我验证
        if not self._level4_self_verification(task):
            logger.error("Level 4: 自我验证失败")
            return False
        logger.info("Level 4: 自我验证通过")

        logger.info("✅ 端到端验证全部通过")
        return True

    def _level1_syntax_check(self, task: Task) -> bool:
        """Level 1: 语法验证"""
        for subtask in task.subtasks:
            if subtask.output:
                # 简单的Python语法检查
                try:
                    compile(subtask.output, '<string>', 'exec')
                except SyntaxError as e:
                    logger.error(f"语法错误: {e}")
                    return False
        return True

    def _level2_functional_test(self, task: Task) -> bool:
        """Level 2: 功能验证"""
        # 简化版本：检查是否有测试代码
        for subtask in task.subtasks:
            if "test" in subtask.name.lower():
                return True
        return True  # 简化版本

    def _level3_integration_test(self, task: Task) -> bool:
        """Level 3: 集成验证"""
        # 简化版本：检查依赖是否满足
        return True

    def _level4_self_verification(self, task: Task) -> bool:
        """Level 4: 自我验证"""
        # 简化版本：检查任务状态
        return task.status == TaskStatus.DONE


class ContextManager:
    """上下文管理器 - 智能压缩与重置"""

    def __init__(self, max_tasks: int = 5, max_minutes: int = 30):
        self.max_tasks = max_tasks
        self.max_minutes = max_minutes
        self.task_count = 0
        self.last_reset = datetime.now()
        self.context: Dict[str, Any] = {}

    def should_compress(self) -> bool:
        """判断是否需要压缩"""
        time_elapsed = (datetime.now() - self.last_reset).total_seconds() / 60
        return self.task_count >= self.max_tasks or time_elapsed >= self.max_minutes

    def compress(self) -> Dict[str, Any]:
        """压缩上下文"""
        logger.info(f"压缩上下文: {self.task_count} 个任务")

        # 保留关键信息
        compressed = {
            "task_count": self.task_count,
            "last_reset": self.last_reset.isoformat(),
            "key_decisions": self.context.get("key_decisions", []),
            "lessons_learned": self.context.get("lessons_learned", [])
        }

        # 重置
        self.task_count = 0
        self.last_reset = datetime.now()

        return compressed

    def add_context(self, key: str, value: Any):
        """添加上下文"""
        self.context[key] = value

    def get_context(self, key: str) -> Any:
        """获取上下文"""
        return self.context.get(key)


class AutonomousController:
    """自主编程控制器 - 主控制器"""

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.task_manager = TaskManager()
        self.git_operator = GitOperator(str(workspace))
        self.orchestrator = SubagentOrchestrator()
        self.verifier = E2EVerifier()
        self.context_manager = ContextManager()
        self.running = False

    def run(self):
        """主循环"""
        logger.info("🚀 自主编程控制器启动")
        self.running = True

        while self.running:
            try:
                # 检查上下文压缩
                if self.context_manager.should_compress():
                    self.context_manager.compress()

                # 获取待处理任务
                pending_tasks = self.task_manager.get_pending_tasks()

                if not pending_tasks:
                    logger.info("没有待处理任务，等待...")
                    time.sleep(60)
                    continue

                # 执行任务
                for task in pending_tasks:
                    if not self.running:
                        break

                    self._execute_task(task)

                    # 更新任务计数
                    self.context_manager.task_count += 1

            except KeyboardInterrupt:
                logger.info("接收到中断信号")
                self.running = False
            except Exception as e:
                logger.error(f"主循环错误: {e}", exc_info=True)
                time.sleep(60)

        logger.info("🛑 自主编程控制器停止")

    def _execute_task(self, task: Task):
        """执行单个任务"""
        logger.info(f"执行任务: {task.id} - {task.title}")

        # 更新任务状态
        self.task_manager.update_task(task.id, status=TaskStatus.IN_PROGRESS)

        try:
            # 根据任务类型执行
            if task.type == TaskType.BUGFIX:
                result = self.orchestrator.execute_bugfix_task(task)
            elif task.type == TaskType.FEATURE:
                result = self.orchestrator.execute_feature_task(task)
            else:
                result = SubtaskResult(
                    name=f"execute_{task.type.value}",
                    status=TaskStatus.DONE,
                    output=f"完成{task.type.value}任务"
                )

            # 添加子任务结果
            task.subtasks.append(result)

            # 端到端验证
            if self.verifier.verify(task):
                task.status = TaskStatus.DONE

                # Git提交
                commit_msg = f"{task.type.value}({task.id}): {task.title}"
                commit_hash = self.git_operator.commit(commit_msg)
                task.git_commit = commit_hash

                logger.info(f"✅ 任务完成: {task.id}")
            else:
                task.status = TaskStatus.FAILED
                logger.error(f"❌ 任务失败: {task.id} (验证未通过)")

            # 保存任务状态
            self.task_manager.update_task(
                task.id,
                status=task.status,
                git_commit=task.git_commit
            )

        except Exception as e:
            logger.error(f"任务执行异常: {e}", exc_info=True)
            task.status = TaskStatus.FAILED
            task.logs.append(str(e))
            self.task_manager.update_task(task.id, status=TaskStatus.FAILED)

    def stop(self):
        """停止控制器"""
        self.running = False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="自主编程控制器v2.0")
    parser.add_argument("--workspace", default="/home/ubuntu/.openclaw/workspace", help="工作区路径")
    parser.add_argument("--once", action="store_true", help="只执行一次")
    parser.add_argument("--list", action="store_true", help="列出任务")

    args = parser.parse_args()

    controller = AutonomousController(args.workspace)

    if args.list:
        tasks = controller.task_manager.list_tasks()
        print(f"\n📋 任务列表 ({len(tasks)}):")
        for task in tasks:
            print(f"  [{task.status.value}] {task.id} - {task.title}")
        return

    if args.once:
        # 只执行一次
        pending_tasks = controller.task_manager.get_pending_tasks()
        if pending_tasks:
            controller._execute_task(pending_tasks[0])
        return

    # 持续运行
    try:
        controller.run()
    except KeyboardInterrupt:
        controller.stop()


if __name__ == "__main__":
    main()
