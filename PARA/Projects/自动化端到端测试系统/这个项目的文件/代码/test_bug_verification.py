#!/usr/bin/env python3
"""Bug验证测试"""
import sys
sys.path.insert(0, '.')
from test_framework import TestCase, TestStatus, TestRunner
import time

class SimpleTest(TestCase):
    """简单测试用例"""
    
    def run_test(self):
        """必须实现run_test"""
        self.assert_equal(1 + 1, 2)
        
class TestWithSetup(TestCase):
    """带setup的测试"""
    
    def setup(self):
        self.data = "initialized"
        
    def run_test(self):
        self.assert_true(self.data == "initialized")

class TestFailSetup(TestCase):
    """setup失败的测试"""
    
    def setup(self):
        raise Exception("Setup intentionally fails")
        
    def run_test(self):
        self.assert_true(True)

# 运行测试
print("=" * 70)
print("Bug验证测试")
print("=" * 70)

runner = TestRunner("BugVerificationSuite")

# 测试1: 简单测试
print("\n测试1: 简单测试（无setup/teardown）")
runner.add_test(SimpleTest())
result1 = runner.run_tests()
print(f"结果: {result1.test_cases[0].status.value}")

# 测试2: 带setup的测试
print("\n测试2: 带setup的测试")
runner2 = TestRunner("TestWithSetup")
runner2.add_test(TestWithSetup())
result2 = runner2.run_tests()
print(f"结果: {result2.test_cases[0].status.value}")

# 测试3: setup失败
print("\n测试3: setup失败")
runner3 = TestRunner("TestFailSetup")
runner3.add_test(TestFailSetup())
result3 = runner3.run_tests()
print(f"结果: {result3.test_cases[0].status.value}")
if result3.test_cases[0].error_message:
    print(f"错误: {result3.test_cases[0].error_message}")

print("\n" + "=" * 70)
print("Bug验证完成")
print("=" * 70)
