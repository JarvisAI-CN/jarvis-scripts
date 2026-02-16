#!/usr/bin/env python3
"""
回归测试模块

提供功能验证、兼容性测试和测试套件组装能力。

核心组件:
- FunctionalTest: 通用功能验证（函数输出、接口响应、文件内容）
- CompatibilityTest: 多配置兼容性验证
- RegressionSuite: 测试套件组装和批量执行

版本: v1.0
创建: 2026-02-15
"""

from __future__ import annotations
import json
import hashlib
import http.client
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass

from test_framework import TestCase, TestStatus, logger


@dataclass
class ValidationResult:
    """验证结果数据类"""
    is_valid: bool
    expected: Any
    actual: Any
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.is_valid,
            "expected": str(self.expected)[:200],  # 限制长度
            "actual": str(self.actual)[:200],
            "message": self.message
        }


class FunctionalTest(TestCase):
    """
    功能验证测试用例

    支持多种验证类型:
    1. 函数输出验证 - 执行函数并验证返回值
    2. 接口响应验证 - HTTP请求并验证响应
    3. 文件内容验证 - 检查文件存在性和内容

    使用示例:
        # 函数验证
        def add(a, b):
            return a + b
        test = FunctionalTest.verify_function("add_test", add, args=(1, 2), expected=3)

        # 接口验证
        test = FunctionalTest.verify_api("api_test", "https://api.example.com/users", expected_status=200)

        # 文件验证
        test = FunctionalTest.verify_file("file_test", "/path/to/file.txt", expected_content="Hello")
    """

    def __init__(self, name: str, timeout: float = 300.0):
        super().__init__(name, timeout)
        self.validation_result: Optional[ValidationResult] = None

    # ========== 工厂方法：创建不同类型的测试 ==========

    @classmethod
    def verify_function(cls,
                        name: str,
                        func: Callable,
                        args: Tuple = (),
                        kwargs: Dict = None,
                        expected: Any = None,
                        validator: Optional[Callable[[Any], bool]] = None) -> 'FunctionalTest':
        """
        创建函数验证测试

        Args:
            name: 测试名称
            func: 要验证的函数
            args: 位置参数
            kwargs: 关键字参数
            expected: 期望返回值（与validator二选一）
            validator: 自定义验证函数 (actual) -> bool

        Returns:
            FunctionalTest 实例

        示例:
            test = FunctionalTest.verify_function(
                "calculate_sum",
                lambda x, y: x + y,
                args=(10, 20),
                expected=30
            )
        """
        kwargs = kwargs or {}

        class _FunctionTest(cls):
            def setup(self):
                self.func = func
                self.args = args
                self.kwargs = kwargs
                self.expected = expected
                self.validator = validator

            def run_test(self):
                try:
                    # 执行函数
                    result = self.func(*self.args, **self.kwargs)
                    logger.info(f"Function {func.__name__} returned: {result}")

                    # 验证结果
                    if self.validator is not None:
                        is_valid = self.validator(result)
                        self.validation_result = ValidationResult(
                            is_valid=is_valid,
                            expected="validator condition",
                            actual=result,
                            message="Custom validation" if is_valid else "Custom validation failed"
                        )
                        self.assert_true(is_valid, f"Custom validation failed for result: {result}")
                    else:
                        is_valid = (result == self.expected)
                        self.validation_result = ValidationResult(
                            is_valid=is_valid,
                            expected=self.expected,
                            actual=result,
                            message="Values match" if is_valid else f"Expected {self.expected}, got {result}"
                        )
                        self.assert_equal(result, self.expected, f"Function returned unexpected value")

                except Exception as e:
                    logger.error(f"Function execution failed: {e}")
                    raise

        return _FunctionTest(name)

    @classmethod
    def verify_api(cls,
                   name: str,
                   url: str,
                   method: str = "GET",
                   expected_status: int = 200,
                   expected_content: Optional[str] = None,
                   expected_json_path: Optional[Tuple[str, Any]] = None,
                   headers: Dict = None,
                   timeout: int = 30) -> 'FunctionalTest':
        """
        创建接口验证测试

        Args:
            name: 测试名称
            url: 接口URL
            method: HTTP方法 (GET/POST/PUT/DELETE)
            expected_status: 期望HTTP状态码
            expected_content: 期望响应内容（子串匹配）
            expected_json_path: 期望JSON字段 (path, value) 如 ("data.id", 123)
            headers: 请求头
            timeout: 请求超时时间

        Returns:
            FunctionalTest 实例

        示例:
            test = FunctionalTest.verify_api(
                "user_api",
                "https://api.example.com/users/1",
                expected_status=200,
                expected_json_path=("data.name", "Alice")
            )
        """
        headers = headers or {}

        class _APITest(cls):
            def setup(self):
                self.url = url
                self.method = method.upper()
                self.expected_status = expected_status
                self.expected_content = expected_content
                self.expected_json_path = expected_json_path
                self.headers = headers
                self.timeout = timeout

            def run_test(self):
                try:
                    logger.info(f"Testing API: {self.method} {self.url}")

                    # 发送HTTP请求
                    req = urllib.request.Request(
                        self.url,
                        method=self.method,
                        headers=self.headers
                    )

                    with urllib.request.urlopen(req, timeout=self.timeout) as response:
                        status_code = response.getcode()
                        response_body = response.read().decode('utf-8')
                        logger.info(f"API response status: {status_code}")

                        # 验证状态码
                        self.assert_equal(status_code, self.expected_status,
                                        f"Unexpected status code")

                        # 验证响应内容
                        if self.expected_content:
                            self.assert_in(self.expected_content, response_body,
                                         f"Expected content not found in response")
                            logger.info(f"Content validation passed: '{self.expected_content}'")

                        # 验证JSON字段
                        if self.expected_json_path:
                            json_data = json.loads(response_body)
                            path, expected_value = self.expected_json_path
                            actual_value = self._get_json_path(json_data, path)
                            self.assert_equal(actual_value, expected_value,
                                            f"JSON path '{path}' mismatch")
                            logger.info(f"JSON validation passed: {path} = {actual_value}")

                        self.validation_result = ValidationResult(
                            is_valid=True,
                            expected=f"Status {self.expected_status}",
                            actual=f"Status {status_code}",
                            message="API validation passed"
                        )

                except urllib.error.HTTPError as e:
                    logger.error(f"HTTP error: {e.code} - {e.reason}")
                    raise AssertionError(f"HTTP error {e.code}: {e.reason}")
                except urllib.error.URLError as e:
                    logger.error(f"URL error: {e.reason}")
                    raise AssertionError(f"Connection failed: {e.reason}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    raise AssertionError(f"Invalid JSON response: {e}")

            def _get_json_path(self, data: Dict, path: str) -> Any:
                """获取JSON嵌套路径的值 (如 'data.user.id')"""
                keys = path.split('.')
                value = data
                for key in keys:
                    if isinstance(value, dict):
                        value = value.get(key)
                    else:
                        raise ValueError(f"Invalid path '{path}', key '{key}' not found")
                return value

        return _APITest(name)

    @classmethod
    def verify_file(cls,
                    name: str,
                    file_path: Union[str, Path],
                    must_exist: bool = True,
                    expected_content: Optional[str] = None,
                    expected_pattern: Optional[str] = None,
                    min_size: int = 0) -> 'FunctionalTest':
        """
        创建文件验证测试

        Args:
            name: 测试名称
            file_path: 文件路径
            must_exist: 文件必须存在
            expected_content: 期望文件内容（精确匹配）
            expected_pattern: 期望内容模式（子串/正则）
            min_size: 最小文件大小（字节）

        Returns:
            FunctionalTest 实例

        示例:
            test = FunctionalTest.verify_file(
                "config_file",
                "/etc/app/config.json",
                must_exist=True,
                expected_pattern='"version": "1.0"'
            )
        """
        file_path = Path(file_path)

        class _FileTest(cls):
            def setup(self):
                self.file_path = file_path
                self.must_exist = must_exist
                self.expected_content = expected_content
                self.expected_pattern = expected_pattern
                self.min_size = min_size

            def run_test(self):
                logger.info(f"Verifying file: {self.file_path}")

                # 检查文件存在性
                if self.must_exist:
                    self.assert_true(self.file_path.exists(),
                                   f"File does not exist: {self.file_path}")
                    logger.info(f"File exists: {self.file_path}")
                elif not self.file_path.exists():
                    logger.info("File does not exist (as expected)")
                    self.validation_result = ValidationResult(
                        is_valid=True,
                        expected="file not exist",
                        actual="file not exist",
                        message="File absence validated"
                    )
                    return

                # 获取文件信息
                file_size = self.file_path.stat().st_size
                logger.info(f"File size: {file_size} bytes")

                # 验证文件大小
                self.assert_true(file_size >= self.min_size,
                               f"File too small: {file_size} < {self.min_size}")

                # 读取文件内容
                content = self.file_path.read_text(encoding='utf-8')

                # 验证精确内容
                if self.expected_content is not None:
                    is_valid = content == self.expected_content
                    self.assert_true(is_valid,
                                   f"File content mismatch")
                    logger.info("Content exact match validated")

                # 验证内容模式
                if self.expected_pattern:
                    self.assert_in(self.expected_pattern, content,
                                 f"Pattern not found in file")
                    logger.info(f"Pattern validated: '{self.expected_pattern}'")

                self.validation_result = ValidationResult(
                    is_valid=True,
                    expected=f"File exists, size>={self.min_size}",
                    actual=f"File exists, size={file_size}",
                    message="File validation passed"
                )

        return _FileTest(name)


class CompatibilityTest(TestCase):
    """
    兼容性测试用例

    在多个配置环境下运行相同测试，验证结果一致性。

    应用场景:
    - 多版本兼容性（Python 3.8, 3.9, 3.10）
    - 多环境兼容性（dev, staging, prod）
    - 多配置兼容性（不同参数组合）

    使用示例:
        def test_logic(env):
            return env["value"] * 2

        test = CompatibilityTest.multi_config(
            "multi_env_test",
            test_logic,
            configs=[
                {"name": "env1", "value": 5},
                {"name": "env2", "value": 10},
            ],
            compare_results=True  # 比较各环境结果是否一致
        )
    """

    def __init__(self, name: str, timeout: float = 300.0):
        super().__init__(name, timeout)
        self.config_results: Dict[str, Any] = {}
        self.comparison_result: Optional[Dict[str, Any]] = None

    @classmethod
    def multi_config(cls,
                     name: str,
                     test_func: Callable,
                     configs: List[Dict[str, Any]],
                     config_key: str = "name",
                     compare_results: bool = False,
                     result_comparator: Optional[Callable[[Any, Any], bool]] = None) -> 'CompatibilityTest':
        """
        创建多配置兼容性测试

        Args:
            name: 测试名称
            test_func: 测试函数，接收配置字典作为参数
            configs: 配置列表，每个配置是一个字典
            config_key: 配置标识键名（用于结果索引）
            compare_results: 是否比较各配置结果
            result_comparator: 自定义结果比较函数 (result1, result2) -> bool

        Returns:
            CompatibilityTest 实例

        示例:
            def calculate(data):
                return data["a"] + data["b"]

            test = CompatibilityTest.multi_config(
                "addition_compatibility",
                calculate,
                configs=[
                    {"name": "test1", "a": 1, "b": 2},
                    {"name": "test2", "a": 10, "b": 20},
                    {"name": "test3", "a": 100, "b": 200},
                ],
                compare_results=False  # 不比较结果，只验证都能执行
            )
        """
        class _MultiConfigTest(cls):
            def setup(self):
                self.test_func = test_func
                self.configs = configs
                self.config_key = config_key
                self.compare_results = compare_results
                self.result_comparator = result_comparator

            def run_test(self):
                logger.info(f"Running compatibility test with {len(self.configs)} configs")

                results = {}
                all_passed = True

                # 在每个配置下运行测试
                for idx, config in enumerate(self.configs):
                    config_name = config.get(self.config_key, f"config_{idx}")
                    logger.info(f"Testing config: {config_name}")

                    try:
                        result = self.test_func(config)
                        results[config_name] = {
                            "status": "passed",
                            "result": result,
                            "config": config
                        }
                        logger.info(f"Config '{config_name}' passed: {result}")
                    except Exception as e:
                        all_passed = False
                        results[config_name] = {
                            "status": "failed",
                            "error": str(e),
                            "config": config
                        }
                        logger.error(f"Config '{config_name}' failed: {e}")

                self.config_results = results

                # 验证所有配置都通过
                self.assert_true(all_passed,
                               f"Some configs failed: {[k for k, v in results.items() if v['status'] == 'failed']}")

                # 比较结果
                if self.compare_results:
                    self._compare_results(results)

                logger.info("All compatibility tests passed")

            def _compare_results(self, results: Dict[str, Any]) -> None:
                """比较各配置结果"""
                logger.info("Comparing results across configs...")

                passed_results = {k: v for k, v in results.items() if v["status"] == "passed"}

                if len(passed_results) < 2:
                    logger.warning("Not enough passed results to compare")
                    return

                # 获取第一个结果作为基准
                first_key = next(iter(passed_results))
                reference_result = passed_results[first_key]["result"]

                comparison_details = []
                all_match = True

                for key, data in passed_results.items():
                    if key == first_key:
                        continue

                    current_result = data["result"]

                    # 使用自定义比较器或默认比较
                    if self.result_comparator:
                        match = self.result_comparator(reference_result, current_result)
                    else:
                        match = (reference_result == current_result)

                    comparison_details.append({
                        "config": key,
                        "match": match,
                        "reference": str(reference_result)[:100],
                        "current": str(current_result)[:100]
                    })

                    if not match:
                        all_match = False
                        logger.warning(f"Result mismatch: {first_key} vs {key}")

                self.comparison_result = {
                    "all_match": all_match,
                    "reference_config": first_key,
                    "comparisons": comparison_details
                }

                # 如果要求比较，则断言所有结果一致
                if all_match:
                    logger.info("All results match across configs")
                else:
                    self.assert_true(False, "Results differ across configs")

        return _MultiConfigTest(name)

    @classmethod
    def multi_version(cls,
                      name: str,
                      test_func: Callable,
                      versions: List[str],
                      version_executor: Callable[[str, Callable], Any]) -> 'CompatibilityTest':
        """
        创建多版本兼容性测试

        Args:
            name: 测试名称
            test_func: 测试函数
            versions: 版本列表 (如 ["3.8", "3.9", "3.10"])
            version_executor: 版本执行器 (version, func) -> result

        Returns:
            CompatibilityTest 实例

        示例:
            def execute_python(version, func):
                # 在指定Python版本下执行函数
                return subprocess.run(["python"+version, "-c", func])

            test = CompatibilityTest.multi_version(
                "python_version_test",
                lambda: print("Hello"),
                versions=["3.8", "3.9", "3.10"],
                version_executor=execute_python
            )
        """
        configs = [{"version": v} for v in versions]

        class _VersionTest(cls.multi_config(name, test_func, configs, config_key="version")):
            def setup(self):
                super().setup()
                self.version_executor = version_executor

            def run_test(self):
                logger.info(f"Testing across {len(self.configs)} Python versions")

                results = {}

                for config in self.configs:
                    version = config["version"]
                    logger.info(f"Testing Python {version}")

                    try:
                        result = self.version_executor(version, self.test_func)
                        results[f"python_{version}"] = {
                            "status": "passed",
                            "result": result
                        }
                    except Exception as e:
                        results[f"python_{version}"] = {
                            "status": "failed",
                            "error": str(e)
                        }

                self.config_results = results

                # 验证至少有一个版本通过
                passed_count = sum(1 for r in results.values() if r["status"] == "passed")
                self.assert_true(passed_count > 0,
                               f"No versions passed: {list(results.keys())}")

                logger.info(f"Multi-version test: {passed_count}/{len(versions)} passed")

        return _VersionTest(name)


class RegressionSuite:
    """
    回归测试套件

    提供便捷的测试组装和批量执行能力。

    使用示例:
        suite = RegressionSuite("Daily Regression")

        # 添加功能测试
        suite.add_test(FunctionalTest.verify_function("test1", func, expected=42))

        # 添加兼容性测试
        suite.add_test(CompatibilityTest.multi_config("test2", func, configs=[...]))

        # 执行所有测试
        result = suite.run()
        suite.print_report()
    """

    def __init__(self, name: str, parallel: bool = True, max_workers: int = 4):
        """
        初始化测试套件

        Args:
            name: 套件名称
            parallel: 是否并行执行
            max_workers: 最大并发数
        """
        self.name = name
        self.parallel = parallel
        self.max_workers = max_workers
        self.tests: List[TestCase] = []
        self.categories: Dict[str, List[TestCase]] = {}

    def add_test(self, test: TestCase, category: str = "default") -> 'RegressionSuite':
        """
        添加单个测试用例

        Args:
            test: 测试用例
            category: 分类标签

        Returns:
            self (支持链式调用)

        示例:
            suite.add_test(test1, "smoke").add_test(test2, "functional")
        """
        self.tests.append(test)
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(test)
        logger.info(f"Added test '{test.name}' to category '{category}'")
        return self

    def add_tests(self, tests: List[TestCase], category: str = "default") -> 'RegressionSuite':
        """批量添加测试用例"""
        for test in tests:
            self.add_test(test, category)
        return self

    def add_functional_tests(self, tests: List[FunctionalTest], category: str = "functional") -> 'RegressionSuite':
        """批量添加功能测试"""
        return self.add_tests(tests, category)

    def add_compatibility_tests(self, tests: List[CompatibilityTest], category: str = "compatibility") -> 'RegressionSuite':
        """批量添加兼容性测试"""
        return self.add_tests(tests, category)

    def get_tests_by_category(self, category: str) -> List[TestCase]:
        """获取指定分类的所有测试"""
        return self.categories.get(category, [])

    def run(self) -> Any:
        """
        执行测试套件

        Returns:
            TestSuiteResult 对象
        """
        from test_framework import TestRunner

        logger.info(f"Running regression suite: {self.name}")
        logger.info(f"Total tests: {len(self.tests)}")
        logger.info(f"Categories: {list(self.categories.keys())}")

        runner = TestRunner(suite_name=self.name, max_workers=self.max_workers)
        runner.add_tests(self.tests)

        if self.parallel:
            result = runner.run_parallel()
        else:
            result = runner.run_sequential()

        return result

    def run_category(self, category: str) -> Any:
        """只运行指定分类的测试"""
        tests = self.get_tests_by_category(category)
        if not tests:
            logger.warning(f"No tests found in category: {category}")
            return None

        logger.info(f"Running category: {category} ({len(tests)} tests)")

        from test_framework import TestRunner
        runner = TestRunner(suite_name=f"{self.name}_{category}", max_workers=self.max_workers)
        runner.add_tests(tests)

        if self.parallel:
            return runner.run_parallel()
        else:
            return runner.run_sequential()

    def print_report(self, result: Any) -> None:
        """打印测试报告"""
        from test_framework import TestReporter

        reporter = TestReporter(result)
        reporter.to_console()

    def save_json_report(self, result: Any, output_path: Union[str, Path]) -> None:
        """保存JSON报告"""
        from test_framework import TestReporter

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        reporter = TestReporter(result)
        reporter.to_json(output_path)

    @staticmethod
    def create_smoke_suite(name: str = "SmokeTest") -> 'RegressionSuite':
        """创建冒烟测试套件（快速验证核心功能）"""
        return RegressionSuite(name, parallel=True, max_workers=4)

    @staticmethod
    def create_full_suite(name: str = "FullRegression") -> 'RegressionSuite':
        """创建完整回归测试套件"""
        return RegressionSuite(name, parallel=True, max_workers=8)


# ========== 演示和测试 ==========

def example_function(x: int, y: int) -> int:
    """示例函数：计算两个数的和"""
    return x + y


def example_api_handler(config: Dict) -> Dict:
    """示例API处理器：模拟API响应"""
    return {
        "status": "success",
        "data": {
            "id": config.get("id", 1),
            "name": config.get("name", "unknown"),
            "value": config.get("value", 0)
        }
    }


def demo_functional_tests():
    """演示功能测试"""
    print("\n" + "="*70)
    print("📋 功能测试演示 (FunctionalTest)")
    print("="*70)

    suite = RegressionSuite("FunctionalDemo")

    # 1. 函数验证
    suite.add_test(
        FunctionalTest.verify_function(
            "addition_test",
            example_function,
            args=(10, 20),
            expected=30
        ),
        category="math"
    )

    # 2. 带验证器的函数测试
    suite.add_test(
        FunctionalTest.verify_function(
            "validator_test",
            lambda x: x * 2,
            args=(5,),
            validator=lambda result: result > 0
        ),
        category="math"
    )

    # 3. 文件验证（使用当前文件）
    suite.add_test(
        FunctionalTest.verify_file(
            "this_file_exists",
            __file__,
            must_exist=True,
            expected_pattern="class FunctionalTest"
        ),
        category="file"
    )

    # 运行并报告
    result = suite.run()
    suite.print_report(result)

    return result


def demo_compatibility_tests():
    """演示兼容性测试"""
    print("\n" + "="*70)
    print("🔄 兼容性测试演示 (CompatibilityTest)")
    print("="*70)

    # 定义一个测试函数
    def calculate_metric(config):
        """计算指标（模拟不同配置下的计算）"""
        base = config.get("base", 10)
        multiplier = config.get("multiplier", 2)
        return base * multiplier

    # 创建多配置测试
    test = CompatibilityTest.multi_config(
        "multi_config_test",
        calculate_metric,
        configs=[
            {"name": "config_A", "base": 10, "multiplier": 2},
            {"name": "config_B", "base": 20, "multiplier": 2},
            {"name": "config_C", "base": 30, "multiplier": 2},
        ],
        compare_results=False  # 不比较结果（因为期望不同）
    )

    # 执行测试
    result = test.execute()

    print(f"\n测试结果: {result.status.value}")
    print(f"耗时: {result.duration:.3f}s")
    if hasattr(test, 'config_results'):
        print(f"\n配置结果:")
        for config_name, config_result in test.config_results.items():
            print(f"  - {config_name}: {config_result['status']}")

    return result


def demo_full_regression_suite():
    """演示完整回归测试套件"""
    print("\n" + "="*70)
    print("🧪 完整回归测试套件演示")
    print("="*70)

    suite = RegressionSuite.create_full_suite("CompleteRegression")

    # 添加功能测试
    suite.add_functional_tests([
        FunctionalTest.verify_function("test1", example_function, args=(1, 2), expected=3),
        FunctionalTest.verify_function("test2", example_function, args=(100, 200), expected=300),
        FunctionalTest.verify_file("test3", __file__, must_exist=True),
    ])

    # 添加兼容性测试
    suite.add_compatibility_tests([
        CompatibilityTest.multi_config(
            "compat1",
            example_api_handler,
            configs=[
                {"name": "env1", "id": 1, "value": 100},
                {"name": "env2", "id": 2, "value": 200},
            ]
        )
    ])

    # 运行所有测试
    result = suite.run()
    suite.print_report(result)

    # 保存报告
    report_path = Path(__file__).parent / "test_results" / f"regression_{result.start_time.strftime('%Y%m%d_%H%M%S')}.json"
    suite.save_json_report(result, report_path)
    print(f"\n📄 报告已保存: {report_path}")

    return result


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           回归测试模块 (regression_test.py) 演示                   ║
╚════════════════════════════════════════════════════════════════════╝
    """)

    # 运行各类演示
    demo_functional_tests()
    demo_compatibility_tests()
    demo_full_regression_suite()

    print("\n" + "="*70)
    print("✅ 所有演示完成!")
    print("="*70)
