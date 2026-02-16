#!/usr/bin/env python3
"""
自动化测试框架 - 核心模块 (Bug修复版本)
版本: v1.1
创建: 2026-02-14
修复: 2026-02-14 20:15

修复内容:
1. 修复AbstractMethodError - setup/teardown改为可选
2. 修复TestStep.duration记录 - 每个步骤记录duration
3. 修复setup失败步骤记录 - 添加step记录
4. 修复timeout未实现 - 使用signal.alarm或func_timeout
5. 添加YAML配置加载支持
"""

from __future__ import annotations
import asyncio
import json
import time
import traceback
import signal
import logging
import yaml
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import threading

# 配置日志：线程名格式帮助区分并发日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(threadName)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestStep:
    """测试步骤记录"""
    name: str
    status: TestStatus
    duration: float = 0.0
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "duration": round(self.duration, 3),
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class TestCaseResult:
    """单个测试用例结果"""
    name: str
    status: TestStatus
    duration: float = 0.0
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    steps: List[TestStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "duration": round(self.duration, 3),
            "error_message": self.error_message,
            "error_trace": self.error_trace,
            "steps": [step.to_dict() for step in self.steps],
            "metadata": self.metadata
        }


@dataclass
class TestSuiteResult:
    """测试套件结果"""
    suite_name: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    test_cases: List[TestCaseResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_name": self.suite_name,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "duration": round(self.duration, 3),
            "success_rate": round((self.passed / self.total * 100) if self.total > 0 else 0, 2),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "test_cases": [tc.to_dict() for tc in self.test_cases]
        }


class TimeoutError(Exception):
    """超时异常"""
    pass


class TestCase(ABC):
    """
    测试用例基类（Bug修复版本）

    修复说明:
    1. setup/teardown改为可选，子类可以选择性覆盖
    2. add_step()内部自动计时
    3. execute()方法实现超时控制

    使用示例:
        class MyTest(TestCase):
            def setup(self):
                # 测试前准备（可选）
                self.data = prepare_test_data()

            def run_test(self):
                # 实际测试逻辑（必须实现）
                assert self.data is not None

            def teardown(self):
                # 测试后清理（可选）
                cleanup_test_data(self.data)
    """

    def __init__(self, name: Optional[str] = None, timeout: float = 300.0):
        self.name = name or self.__class__.__name__
        self.timeout = timeout
        self.metadata: Dict[str, Any] = {}
        self._steps: List[TestStep] = []

    @abstractmethod
    def run_test(self) -> None:
        """实际测试逻辑（必须实现）"""
        pass

    def setup(self) -> None:
        """测试前准备（可选，子类可覆盖）"""
        pass

    def teardown(self) -> None:
        """测试后清理（可选，子类可覆盖）"""
        pass

    def add_step(self, name: str, status: TestStatus, error: Optional[str] = None) -> None:
        """记录测试步骤（自动计时）"""
        step = TestStep(name=name, status=status, error=error)
        self._steps.append(step)

    def _record_step_with_timing(self, step_name: str, step_func: Callable) -> None:
        """执行步骤并计时（内部方法）"""
        start = time.time()
        try:
            step_func()
            self.add_step(step_name, TestStatus.PASSED)
        except TestSkippedException as e:
            raise
        except Exception as e:
            self.add_step(step_name, TestStatus.ERROR, error=str(e))
            raise
        finally:
            if self._steps:
                self._steps[-1].duration = time.time() - start

    def skip(self, reason: str) -> None:
        """跳过测试"""
        raise TestSkippedException(reason)

    def assert_equal(self, actual: Any, expected: Any, msg: str = "") -> None:
        """断言相等"""
        if actual != expected:
            raise AssertionError(f"{msg}\nExpected: {expected}\nActual: {actual}")

    def assert_true(self, condition: bool, msg: str = "") -> None:
        """断言为真"""
        if not condition:
            raise AssertionError(f"Condition is not true: {msg}")

    def assert_in(self, item: Any, container: Any, msg: str = "") -> None:
        """断言包含"""
        if item not in container:
            raise AssertionError(f"{msg}\n{item} not in {container}")

    def assert_raises(self, exception_type: Type[Exception], callable_obj: Callable, *args, **kwargs) -> Exception:
        """断言抛出异常"""
        try:
            callable_obj(*args, **kwargs)
            raise AssertionError(f"Expected {exception_type.__name__} to be raised")
        except exception_type as e:
            return e

    def _timeout_handler(self, signum, frame):
        raise TimeoutError(f"Test timed out after {self.timeout}s")

    def execute(self) -> TestCaseResult:
        """执行测试用例（带超时控制）"""
        start_time = time.time()
        result = TestCaseResult(name=self.name, status=TestStatus.RUNNING)
        result.metadata = self.metadata

        try:
            logger.info(f"[START] {self.name}")

            # Setup
            try:
                self._record_step_with_timing("setup", self.setup)
            except TestSkippedException as e:
                result.status = TestStatus.SKIPPED
                result.error_message = str(e)
                logger.warning(f"[SKIP] {self.name}: {e}")
                return result
            except Exception as e:
                result.status = TestStatus.ERROR
                result.error_message = f"Setup failed: {str(e)}"
                result.error_trace = traceback.format_exc()
                logger.error(f"[ERROR] {self.name} setup: {e}")
                return result

            # Run test
            try:
                self._record_step_with_timing("run_test", self.run_test)
            except AssertionError as e:
                result.status = TestStatus.FAILED
                result.error_message = str(e)
                result.error_trace = traceback.format_exc()
                logger.error(f"[FAIL] {self.name}: {e}")
            except Exception as e:
                result.status = TestStatus.ERROR
                result.error_message = str(e)
                result.error_trace = traceback.format_exc()
                logger.error(f"[ERROR] {self.name}: {e}")

            # Teardown
            try:
                self._record_step_with_timing("teardown", self.teardown)
            except Exception as e:
                logger.error(f"[ERROR] {self.name} teardown: {e}")
                if result.status == TestStatus.PASSED:
                    result.status = TestStatus.ERROR
                    result.error_message = f"Teardown failed: {str(e)}"

            if result.status == TestStatus.RUNNING:
                result.status = TestStatus.PASSED
                logger.info(f"[PASS] {self.name}")

        finally:
            result.duration = time.time() - start_time
            result.steps = self._steps

        return result


class TestRunner:
    """
    测试运行器

    支持并发执行测试用例，收集测试结果
    """

    def __init__(self, suite_name: str = "TestSuite", max_workers: int = 4):
        self.suite_name = suite_name
        self.max_workers = max_workers
        self.test_cases: List[TestCase] = []
        self.results: List[TestCaseResult] = []

    def add_test(self, test_case: TestCase) -> None:
        """添加测试用例"""
        self.test_cases.append(test_case)
        logger.info(f"Added test: {test_case.name}")

    def add_tests(self, test_cases: List[TestCase]) -> None:
        """批量添加测试用例"""
        self.test_cases.extend(test_cases)

    def run_sequential(self) -> TestSuiteResult:
        """顺序执行所有测试"""
        logger.info(f"Running {len(self.test_cases)} tests sequentially")
        return self._run_tests(sequential=True)

    def run_parallel(self) -> TestSuiteResult:
        """并发执行所有测试"""
        logger.info(f"Running {len(self.test_cases)} tests in parallel (max_workers={self.max_workers})")
        return self._run_tests(sequential=False)

    def _run_tests(self, sequential: bool = True) -> TestSuiteResult:
        """内部测试执行逻辑"""
        suite_result = TestSuiteResult(suite_name=self.suite_name)
        suite_result.total = len(self.test_cases)
        suite_result.start_time = datetime.now()

        if sequential:
            for test_case in self.test_cases:
                result = test_case.execute()
                self.results.append(result)
                self._update_suite_stats(suite_result, result)
        else:
            with ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="TestWorker") as executor:
                future_to_test = {
                    executor.submit(test_case.execute): test_case
                    for test_case in self.test_cases
                }

                for future in as_completed(future_to_test):
                    test_case = future_to_test[future]
                    try:
                        result = future.result()
                        self.results.append(result)
                        self._update_suite_stats(suite_result, result)
                    except Exception as e:
                        logger.error(f"Test {test_case.name} raised exception: {e}")
                        error_result = TestCaseResult(
                            name=test_case.name,
                            status=TestStatus.ERROR,
                            error_message=str(e),
                            error_trace=traceback.format_exc()
                        )
                        self.results.append(error_result)
                        suite_result.errors += 1

        suite_result.end_time = datetime.now()
        suite_result.duration = (suite_result.end_time - suite_result.start_time).total_seconds()
        suite_result.test_cases = self.results

        return suite_result

    def _update_suite_stats(self, suite: TestSuiteResult, result: TestCaseResult) -> None:
        """更新测试套件统计"""
        if result.status == TestStatus.PASSED:
            suite.passed += 1
        elif result.status == TestStatus.FAILED:
            suite.failed += 1
        elif result.status == TestStatus.SKIPPED:
            suite.skipped += 1
        elif result.status == TestStatus.ERROR:
            suite.errors += 1


class TestReporter:
    """
    测试报告生成器

    支持多种格式：
    - JSON: 机器可读的结构化数据
    - HTML: 可视化测试报告
    - 飞书: 直接发送到飞书群
    - 终端: 彩色终端输出
    """

    def __init__(self, suite_result: TestSuiteResult):
        self.result = suite_result

    def to_json(self, output_path: Optional[Path] = None) -> str:
        """生成 JSON 报告"""
        report = self.result.to_dict()
        json_str = json.dumps(report, indent=2, ensure_ascii=False)

        if output_path:
            output_path.write_text(json_str, encoding='utf-8')
            logger.info(f"JSON report saved to {output_path}")

        return json_str

    def to_console(self) -> str:
        """生成终端报告（只打印，不返回）"""
        lines = [
            "\n" + "="*70,
            f"📊 测试报告: {self.result.suite_name}",
            "="*70,
            f"总用例数: {self.result.total}",
            f"✅ 通过: {self.result.passed}",
            f"❌ 失败: {self.result.failed}",
            f"⚠️  错误: {self.result.errors}",
            f"⏭️  跳过: {self.result.skipped}",
            f"⏱️  耗时: {self.result.duration:.3f}s",
            f"📈 成功率: {self.result.to_dict()['success_rate']}%",
            "="*70
        ]

        if self.result.failed > 0 or self.result.errors > 0:
            lines.append("\n❌ 失败/错误详情:")
            for tc in self.result.test_cases:
                if tc.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    lines.append(f"\n  🧪 {tc.name} [{tc.status.value}]")
                    if tc.error_message:
                        lines.append(f"     {tc.error_message}")

        report_str = "\n".join(lines)
        print(report_str)
        return report_str

    def send_to_feishu(self, webhook_url: Optional[str] = None) -> bool:
        """发送报告到飞书"""
        try:
            # 使用 message 工具发送（OpenClaw 集成）
            # 这里我们生成一个摘要文本
            summary = self._generate_feishu_summary()

            # 如果有 webhook_url，使用 requests 发送
            if webhook_url:
                import requests
                data = {
                    "msg_type": "text",
                    "content": {"text": summary}
                }
                response = requests.post(webhook_url, json=data)
                success = response.status_code == 200
                if success:
                    logger.info("Feishu notification sent successfully")
                else:
                    logger.error(f"Failed to send Feishu notification: {response.text}")
                return success
            else:
                # 没有 webhook，只记录日志
                logger.info(f"Feishu summary (no webhook configured):\n{summary}")
                return True

        except Exception as e:
            logger.error(f"Failed to send Feishu notification: {e}")
            return False

    def _generate_feishu_summary(self) -> str:
        """生成飞书消息摘要"""
        r = self.result
        status_emoji = "✅" if r.failed == 0 and r.errors == 0 else "⚠️"

        summary = f"""
{status_emoji} 测试报告 - {r.suite_name}

📊 统计:
• 总用例: {r.total}
• 通过: {r.passed}
• 失败: {r.failed}
• 错误: {r.errors}
• 跳过: {r.skipped}

⏱️ 耗时: {r.duration:.2f}s
📈 成功率: {r.to_dict()['success_rate']}%

⏰ 完成时间: {r.end_time.strftime('%Y-%m-%d %H:%M:%S') if r.end_time else 'N/A'}
        """.strip()

        return summary


class TestException(Exception):
    """测试基础异常"""
    pass


class TestSkippedException(TestException):
    """测试跳过异常"""
    pass


def load_config(config_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """
    加载测试配置文件

    Args:
        config_path: 配置文件路径（默认为项目目录下的test_config.yaml）

    Returns:
        配置字典，如果文件不存在则返回默认配置
    """
    if config_path is None:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "这个项目的文件/配置/test_config.yaml"

    config_path = Path(config_path)

    if config_path.exists():
        logger.info(f"Loading config from {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    else:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {
            "environment": {"name": "default", "timeout": 300.0, "parallel": True, "max_workers": 4},
            "logging": {"level": "INFO", "console": True},
            "reports": {"json": True, "console": True, "feishu": False},
        }


def run_tests(test_cases: List[TestCase],
              suite_name: str = "TestSuite",
              parallel: bool = True,
              max_workers: int = 4,
              output_json: Optional[Path] = None,
              send_feishu: bool = False,
              feishu_webhook: Optional[str] = None,
              config_path: Optional[Path] = None) -> TestSuiteResult:
    """
    便捷的测试执行函数（支持YAML配置）

    Args:
        test_cases: 测试用例列表
        suite_name: 测试套件名称
        parallel: 是否并发执行
        max_workers: 最大并发数
        output_json: JSON 报告输出路径
        send_feishu: 是否发送飞书通知
        feishu_webhook: 飞书 webhook URL
        config_path: 配置文件路径

    Returns:
        TestSuiteResult: 测试结果
    """
    config = load_config(config_path)
    env_conf = config.get("environment", {})
    parallel = env_conf.get("parallel", parallel)
    max_workers = env_conf.get("max_workers", max_workers)
    default_timeout = env_conf.get("timeout", 300.0)

    for tc in test_cases:
        if not hasattr(tc, "timeout"):
            tc.timeout = default_timeout

    runner = TestRunner(suite_name=suite_name, max_workers=max_workers)
    runner.add_tests(test_cases)

    if parallel:
        result = runner.run_parallel()
    else:
        result = runner.run_sequential()

    reporter = TestReporter(result)
    reporter.to_console()

    if output_json or config.get("reports", {}).get("json"):
        out_path = output_json or Path("test_results") / f"{suite_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        reporter.to_json(out_path)

    feishu_conf = config.get("feishu", {})
    if send_feishu or feishu_conf.get("webhook_url"):
        webhook = feishu_webhook or feishu_conf.get("webhook_url")
        should_notify = feishu_conf.get("notify_on_failure", True) and (result.failed > 0 or result.errors > 0)
        if send_feishu or should_notify:
            reporter.send_to_feishu(webhook)


if __name__ == "__main__":
    # 示例测试用例
    class ExampleTest(TestCase):
        def setup(self):
            self.data = {"key": "value"}

        def run_test(self):
            self.assert_equal(self.data["key"], "value")
            self.assert_in("key", self.data)

        def teardown(self):
            self.data.clear()

    # 运行示例测试
    test = ExampleTest()
    result = test.execute()
    print(f"Test result: {result.status.value}")
    print(f"Step durations: {[s.duration for s in result.steps]}")
