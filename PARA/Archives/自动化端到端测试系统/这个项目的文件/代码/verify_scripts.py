#!/usr/bin/env python3
"""
快速验证脚本 - 测试 run_all_tests.py 和 auto_reporter.py 的基本功能
"""

import sys
import json
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 70)
    print("自动化端到端测试系统 - 功能验证")
    print("=" * 70)
    print()

    # 1. 导入测试
    print("1. 测试模块导入...")
    try:
        from test_framework import TestCase, TestRunner, TestStatus
        from regression_test import RegressionSuite, FunctionalTest
        from performance_test import ResponseTimeTest, ThroughputTest
        from security_test import VulnerabilityScanner
        print("   ✅ 所有模块导入成功")
    except Exception as e:
        print(f"   ❌ 模块导入失败: {e}")
        return False
    print()

    # 2. 创建简单测试用例
    print("2. 创建测试用例...")
    try:
        # 功能测试
        def add(a, b):
            return a + b

        test1 = FunctionalTest.verify_function(
            "test_add",
            add,
            args=(1, 2),
            expected=3
        )

        # 性能测试
        def quick_task():
            return sum(range(100))

        test2 = ResponseTimeTest(
            "test_response_time",
            quick_task,
            threshold=1.0,
            iterations=3
        )

        print(f"   ✅ 创建了 {2} 个测试用例")
    except Exception as e:
        print(f"   ❌ 创建测试用例失败: {e}")
        return False
    print()

    # 3. 运行测试套件
    print("3. 运行测试套件...")
    try:
        suite = RegressionSuite("VerificationSuite", parallel=False)
        suite.add_test(test1, "functional")
        suite.add_test(test2, "performance")

        result = suite.run()
        print(f"   ✅ 测试套件执行完成")
        print(f"   - 总用例: {result.total}")
        print(f"   - 通过: {result.passed}")
        print(f"   - 失败: {result.failed}")
        print(f"   - 耗时: {result.duration:.2f}s")
    except Exception as e:
        print(f"   ❌ 运行测试套件失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # 4. 保存测试结果
    print("4. 保存测试结果...")
    try:
        results_dir = Path(__file__).parent / "test_results"
        results_dir.mkdir(exist_ok=True)

        timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"verification_{timestamp}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"   ✅ 结果已保存: {result_file.name}")
    except Exception as e:
        print(f"   ❌ 保存结果失败: {e}")
        return False
    print()

    # 5. 测试报告生成器
    print("5. 测试报告生成器...")
    try:
        from auto_reporter import (
            TrendAnalyzer,
            AlertManager,
            MarkdownReporter,
            FeishuIntegration,
            generate_report
        )

        # 生成报告
        report, metadata = generate_report(
            result_data=result.to_dict(),
            enable_trend_analysis=False,  # 没有历史数据
            regression_threshold=20.0
        )

        print(f"   ✅ 报告生成成功")
        print(f"   - 输出路径: {metadata['output_path']}")
        print(f"   - 告警数量: {metadata['alerts_count']}")
        print(f"   - 成功率: {metadata['success_rate']}%")
    except Exception as e:
        print(f"   ❌ 生成报告失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    print()

    # 6. 测试飞书集成
    print("6. 测试飞书集成...")
    try:
        feishu = FeishuIntegration(result.to_dict())
        summary = feishu.send_summary()
        print(f"   ✅ 飞书摘要生成成功")
        print(f"   - 摘要长度: {len(summary)} 字符")
    except Exception as e:
        print(f"   ❌ 飞书集成测试失败: {e}")
        return False
    print()

    # 总结
    print("=" * 70)
    print("✅ 所有功能验证通过！")
    print("=" * 70)
    print()
    print("可以使用以下命令运行完整测试:")
    print(f"  python3 {Path(__file__).parent / 'run_all_tests.py'}")
    print()
    print("测试完成后生成报告:")
    print(f"  python3 {Path(__file__).parent / 'auto_reporter.py'} --result test_results/report_YYYYMMDD_HHMMSS.json")
    print()

    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
