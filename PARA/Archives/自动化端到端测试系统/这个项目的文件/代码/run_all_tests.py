#!/usr/bin/env python3
"""
自动化端到端测试系统 - 全测试执行器

功能:
1. 导入所有测试模块（性能、安全、回归）
2. 使用 RegressionSuite 组织所有测试用例
3. 并发执行完整测试套件
4. 将 JSON 结果自动保存到 test_results/ 目录

版本: v1.0
创建: 2026-02-16
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 添加当前目录到 Python 路径，确保可以导入本地模块
sys.path.insert(0, str(Path(__file__).parent))

# 导入测试框架和模块
from test_framework import (
    TestCase,
    TestRunner,
    TestStatus,
    logger,
    TestSuiteResult
)
from regression_test import (
    RegressionSuite,
    FunctionalTest,
    CompatibilityTest
)
from performance_test import (
    ResponseTimeTest,
    ThroughputTest,
    ResourceUsageTest
)
from security_test import (
    VulnerabilityScanner,
    ConfigAuditor,
    PermissionChecker,
    DependencyChecker
)


# ==================== 测试用例收集 ====================

def collect_all_tests() -> List[TestCase]:
    """
    收集所有测试用例

    Returns:
        包含所有测试用例的列表
    """
    all_tests: List[TestCase] = []

    # ========== 1. 性能测试用例 ==========
    logger.info("Collecting performance tests...")

    # 1.1 响应时间测试
    # 示例：测试一个快速操作的响应时间
    def fast_operation():
        """模拟快速操作"""
        return sum(range(1000))

    all_tests.append(
        ResponseTimeTest(
            name="Performance_FastOperation_ResponseTime",
            func=fast_operation,
            threshold=0.1,  # 100ms
            iterations=10
        )
    )

    # 1.2 吞吐量测试
    # 示例：测试操作的吞吐量
    def simple_task():
        """模拟简单任务"""
        return [x * 2 for x in range(100)]

    all_tests.append(
        ThroughputTest(
            name="Performance_SimpleTask_Throughput",
            func=simple_task,
            duration=2.0,  # 测试2秒
            threshold=10.0  # 至少10 TPS
        )
    )

    # 1.3 资源使用测试
    all_tests.append(
        ResourceUsageTest(
            name="Performance_Task_ResourceUsage",
            func=simple_task,
            cpu_threshold=80.0,  # CPU不超过80%
            mem_threshold_mb=512.0  # 内存不超过512MB
        )
    )

    # ========== 2. 安全测试用例 ==========
    logger.info("Collecting security tests...")

    # 获取当前代码目录路径
    current_dir = Path(__file__).parent

    # 2.1 代码漏洞扫描
    all_tests.append(
        VulnerabilityScanner(
            target_path=str(current_dir),
            name="Security_CodeVulnerabilityScan"
        )
    )

    # 2.2 配置文件审计
    config_dir = current_dir.parent / "配置"
    if config_dir.exists():
        all_tests.append(
            ConfigAuditor(
                config_path=str(config_dir),
                name="Security_ConfigAudit"
            )
        )

    # 2.3 文件权限检查
    all_tests.append(
        PermissionChecker(
            target_path=str(current_dir),
            name="Security_FilePermissionsCheck"
        )
    )

    # ========== 3. 回归测试用例 ==========
    logger.info("Collecting regression tests...")

    # 3.1 功能验证测试 - 函数验证
    def add_numbers(a, b):
        """加法函数"""
        return a + b

    def multiply_numbers(a, b):
        """乘法函数"""
        return a * b

    all_tests.append(
        FunctionalTest.verify_function(
            name="Regression_AddFunction",
            func=add_numbers,
            args=(10, 20),
            expected=30
        )
    )

    all_tests.append(
        FunctionalTest.verify_function(
            name="Regression_MultiplyFunction",
            func=multiply_numbers,
            args=(5, 6),
            expected=30
        )
    )

    # 3.2 功能验证测试 - 自定义验证器
    def is_even(value):
        """检查是否为偶数"""
        return value % 2 == 0

    all_tests.append(
        FunctionalTest.verify_function(
            name="Regression_EvenNumberCheck",
            func=lambda x: x * 2,
            args=(5,),
            validator=is_even
        )
    )

    # 3.3 兼容性测试 - 多配置验证
    def process_data(config):
        """数据处理函数"""
        multiplier = config.get("multiplier", 1)
        return [x * multiplier for x in range(10)]

    all_tests.append(
        CompatibilityTest.multi_config(
            name="Regression_DataProcessing_Compatibility",
            func=process_data,
            configs=[
                {"multiplier": 1, "expected": list(range(10))},
                {"multiplier": 2, "expected": [x * 2 for x in range(10)]},
                {"multiplier": 3, "expected": [x * 3 for x in range(10)]},
            ],
            result_validator=lambda actual, config: actual == config["expected"]
        )
    )

    # ========== 4. API测试用例（如果有的话）==========
    # 这里可以添加实际的API测试
    # 示例：测试一个公开的API
    try:
        all_tests.append(
            FunctionalTest.verify_api(
                name="Regression_PublicAPI_Test",
                url="https://httpbin.org/status/200",
                expected_status=200
            )
        )
    except Exception as e:
        logger.warning(f"API test skipped: {e}")

    logger.info(f"Total tests collected: {len(all_tests)}")
    return all_tests


# ==================== 测试结果保存 ====================

def save_test_result(result: TestSuiteResult, output_dir: Optional[Path] = None) -> Path:
    """
    保存测试结果到 JSON 文件

    Args:
        result: 测试套件结果
        output_dir: 输出目录（默认为代码目录下的 test_results/）

    Returns:
        保存的文件路径
    """
    # 确定输出目录
    if output_dir is None:
        output_dir = Path(__file__).parent / "test_results"

    # 创建目录（如果不存在）
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.json"
    output_path = output_dir / filename

    # 保存结果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    logger.info(f"Test results saved to: {output_path}")
    return output_path


# ==================== 主执行函数 ====================

def run_all_tests(
    parallel: bool = True,
    max_workers: int = 4,
    save_results: bool = True,
    output_dir: Optional[Path] = None
) -> TestSuiteResult:
    """
    运行所有测试

    Args:
        parallel: 是否并发执行
        max_workers: 最大并发数
        save_results: 是否保存结果
        output_dir: 结果输出目录

    Returns:
        TestSuiteResult 对象
    """
    # 打印开始信息
    logger.info("=" * 70)
    logger.info("自动化端到端测试系统 - 全测试执行器")
    logger.info("=" * 70)
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"并发模式: {'启用' if parallel else '禁用'}")
    logger.info(f"最大并发数: {max_workers if parallel else 1}")
    logger.info("")

    # 收集所有测试
    all_tests = collect_all_tests()

    # 创建测试套件
    suite = RegressionSuite(
        name="FullTestSuite",
        parallel=parallel,
        max_workers=max_workers
    )

    # 添加所有测试到套件
    for test in all_tests:
        # 根据测试类型自动分类
        if "Performance" in test.name:
            suite.add_test(test, "performance")
        elif "Security" in test.name:
            suite.add_test(test, "security")
        elif "Regression" in test.name:
            suite.add_test(test, "regression")
        else:
            suite.add_test(test, "general")

    # 运行测试
    logger.info("")
    logger.info("=" * 70)
    logger.info("开始执行测试...")
    logger.info("=" * 70)
    result = suite.run()

    # 保存结果
    if save_results:
        save_test_result(result, output_dir)

    # 打印报告
    logger.info("")
    suite.print_report()

    logger.info("")
    logger.info("=" * 70)
    logger.info(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"总耗时: {result.duration:.2f}秒")
    logger.info("=" * 70)

    return result


# ==================== 命令行入口 ====================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="自动化端到端测试系统 - 全测试执行器"
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="顺序执行测试（默认为并发）"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="最大并发数（默认：4）"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="不保存测试结果"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="测试结果输出目录（默认：代码目录/test_results/）"
    )

    args = parser.parse_args()

    # 运行测试
    result = run_all_tests(
        parallel=not args.sequential,
        max_workers=args.workers,
        save_results=not args.no_save,
        output_dir=Path(args.output_dir) if args.output_dir else None
    )

    # 根据测试结果设置退出码
    # 0: 全部通过
    # 1: 有失败或错误
    exit_code = 0 if result.failed == 0 and result.errors == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
