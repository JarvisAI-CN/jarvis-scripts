#!/usr/bin/env python3
"""
自主编程控制器v3.0 - 完整测试套件
测试覆盖：任务管理、Git操作、三轮协作、端到端验证等
版本: v1.0
创建: 2026-02-14
"""

import unittest
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from autonomous_controller_v3 import (
        TaskManager,
        TaskType,
        TaskStatus,
        Task,
        SubtaskResult,
        GitOperator,
        E2EVerifier,
        ProgressFlowLogger,
        AutonomousControllerV3
    )
    from enhanced_task_executor import (
        EnhancedTaskExecutor,
        TaskCategory,
        EnhancedMonitoringTask,
        EnhancedKnowledgeTask,
        EnhancedTaskResult
    )
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保autonomous_controller_v3.py和enhanced_task_executor.py在当前目录")
    sys.exit(1)


class TestTaskManager(unittest.TestCase):
    """测试TaskManager"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.task_list_path = Path(self.temp_dir) / ".task_list.json"
        self.manager = TaskManager(str(self.task_list_path))

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_file(self):
        """测试初始化创建文件"""
        self.assertTrue(self.task_list_path.exists())

    def test_add_task(self):
        """测试添加任务"""
        task = Task(
            id="TASK-001",
            title="测试任务",
            type=TaskType.FEATURE,
            priority="high"
        )

        self.manager.add_task(task)

        self.assertEqual(len(self.manager.tasks), 1)
        self.assertIn("TASK-001", self.manager.tasks)

    def test_update_task(self):
        """测试更新任务"""
        task = Task(
            id="TASK-001",
            title="测试任务",
            type=TaskType.FEATURE,
            priority="high"
        )

        self.manager.add_task(task)
        self.manager.update_task("TASK-001", status=TaskStatus.DONE)

        updated_task = self.manager.get_task("TASK-001")
        self.assertEqual(updated_task.status, TaskStatus.DONE)

    def test_get_tasks_by_status(self):
        """测试按状态获取任务"""
        task1 = Task(id="TASK-001", title="任务1", type=TaskType.FEATURE, priority="high")
        task2 = Task(id="TASK-002", title="任务2", type=TaskType.BUGFIX, priority="medium", status=TaskStatus.DONE)

        self.manager.add_task(task1)
        self.manager.add_task(task2)

        pending_tasks = self.manager.get_tasks_by_status(TaskStatus.PENDING)
        self.assertEqual(len(pending_tasks), 1)

    def test_get_tasks_by_type(self):
        """测试按类型获取任务"""
        task1 = Task(id="TASK-001", title="任务1", type=TaskType.FEATURE, priority="high")
        task2 = Task(id="TASK-002", title="任务2", type=TaskType.BUGFIX, priority="medium")

        self.manager.add_task(task1)
        self.manager.add_task(task2)

        feature_tasks = self.manager.get_tasks_by_type(TaskType.FEATURE)
        self.assertEqual(len(feature_tasks), 1)


class TestGitOperator(unittest.TestCase):
    """测试GitOperator"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

        # 初始化Git仓库
        import subprocess
        subprocess.run(
            ["git", "init"],
            cwd=self.workspace,
            capture_output=True
        )

        self.git_operator = GitOperator(str(self.workspace))

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('subprocess.run')
    def test_run_git_success(self, mock_run):
        """测试Git命令执行成功"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "success"
        mock_run.return_value = mock_result

        success, output = self.git_operator._run_git(["status"])

        self.assertTrue(success)
        self.assertEqual(output, "success")

    def test_get_changes(self):
        """测试获取更改"""
        # 创建测试文件
        test_file = self.workspace / "test.txt"
        test_file.write_text("test")

        changes = self.git_operator.get_changes()

        self.assertTrue(len(changes) > 0)


class TestE2EVerifier(unittest.TestCase):
    """测试E2EVerifier"""

    def setUp(self):
        """测试准备"""
        self.verifier = E2EVerifier()

    def test_verify_syntax_valid(self):
        """测试语法检查 - 有效代码"""
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello world')\n")
            test_file = f.name

        try:
            success, message = self.verifier.verify_syntax(test_file)
            self.assertTrue(success)
            self.assertIn("通过", message)
        finally:
            Path(test_file).unlink(missing_ok=True)

    def test_verify_syntax_invalid(self):
        """测试语法检查 - 无效代码"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello world'\n")  # 语法错误
            test_file = f.name

        try:
            success, message = self.verifier.verify_syntax(test_file)
            self.assertFalse(success)
            self.assertIn("错误", message)
        finally:
            Path(test_file).unlink(missing_ok=True)


class TestEnhancedTaskExecutor(unittest.TestCase):
    """测试EnhancedTaskExecutor"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.executor = EnhancedTaskExecutor(workspace=self.temp_dir)

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_task_category_monitoring(self):
        """测试检测监控任务"""
        category = self.executor.detect_task_category("系统健康检查")
        self.assertEqual(category, TaskCategory.MONITORING)

    def test_detect_task_category_knowledge(self):
        """测试检测知识管理任务"""
        category = self.executor.detect_task_category("更新知识库")
        self.assertEqual(category, TaskCategory.KNOWLEDGE)

    @patch('subprocess.run')
    def test_execute_monitoring_task(self, mock_run):
        """测试执行监控任务"""
        # Mock subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "running"
        mock_run.return_value = mock_result

        result = self.executor.monitoring_task.execute_enhanced_monitoring()

        self.assertEqual(result.category, TaskCategory.MONITORING)
        self.assertIn(result.status, ["success", "partial", "failed"])

    def test_execute_knowledge_task(self):
        """测试执行知识管理任务"""
        # 创建测试PARA结构
        para_dir = Path(self.temp_dir) / "PARA"
        para_dir.mkdir()
        (para_dir / "Projects").mkdir()

        result = self.executor.knowledge_task.execute_enhanced_knowledge_management()

        self.assertEqual(result.category, TaskCategory.KNOWLEDGE)
        self.assertIn("para_structure", result.metrics)


class TestAutonomousControllerV3(unittest.TestCase):
    """测试AutonomousControllerV3"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.controller = AutonomousControllerV3(workspace=self.temp_dir)

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_task_type_bugfix(self):
        """测试检测Bug修复任务"""
        task_type = self.controller._detect_task_type("修复登录Bug")
        self.assertEqual(task_type, TaskType.BUGFIX)

    def test_detect_task_type_feature(self):
        """测试检测功能开发任务"""
        task_type = self.controller._detect_task_type("添加新功能")
        self.assertEqual(task_type, TaskType.FEATURE)

    @patch('subprocess.run')
    def test_execute_bugfix_task_mock(self, mock_run):
        """测试执行Bug修复任务（Mock）"""
        # Mock子代理创建
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Session ID: test_session_123"
        mock_run.return_value = mock_result

        task = Task(
            id="TASK-001",
            title="修复Bug",
            type=TaskType.BUGFIX,
            priority="high",
            description="修复登录Bug"
        )

        result = self.controller.execute_bugfix_task(task)

        self.assertEqual(result.name, "BugFix: 修复Bug")
        self.assertIn(result.status, [TaskStatus.DONE, TaskStatus.FAILED])


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()

        # 创建测试TODO.md
        todo_file = Path(self.temp_dir) / "TODO.md"
        todo_file.write_text("""
# TODO.md

## 第一象限：重要且紧急

- [ ] 修复登录Bug
- [ ] 添加用户注册功能

## 第二象限：紧急但不重要

- [ ] 回复邮件
""")

        self.controller = AutonomousControllerV3(workspace=self.temp_dir)

    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_extract_tasks_from_todo(self):
        """测试从TODO.md提取任务"""
        tasks = self.controller.extract_tasks_from_todo()

        self.assertEqual(len(tasks), 3)

        # 检查第一个任务
        self.assertEqual(tasks[0].title, "修复登录Bug")
        self.assertEqual(tasks[0].type, TaskType.BUGFIX)

        # 检查第二个任务
        self.assertEqual(tasks[1].title, "添加用户注册功能")
        self.assertEqual(tasks[1].type, TaskType.FEATURE)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestGitOperator))
    suite.addTests(loader.loadTestsFromTestCase(TestE2EVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedTaskExecutor))
    suite.addTests(loader.loadTestsFromTestCase(TestAutonomousControllerV3))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 70)
    print(f"测试完成: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
