#!/usr/bin/env python3
"""
Quick verification test for the E2E test framework.
Simplified version without complex imports.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add to path
framework_dir = os.path.dirname(os.path.abspath(__file__))
if framework_dir not in sys.path:
    sys.path.insert(0, framework_dir)

# Direct imports (no package)
exec(open(f"{framework_dir}/core/assertions.py").read())
exec(open(f"{framework_dir}/core/case.py").read())
exec(open(f"{framework_dir}/core/runner.py").read())


@test_case(name="Verification Test 1", tags=["verify"])
class VerifyTest1(TestCase):
    async def execute_test(self):
        expect(1 + 1).to_eq(2)
        expect("hello").to_contain("ell")
        expect([1, 2, 3]).to_have_length(3)


@test_case(name="Verification Test 2", tags=["verify"])
class VerifyTest2(TestCase):
    async def execute_test(self):
        expect(10).to_be_gt(5)
        expect(10).not_().to_eq(5)
        expect({"a": 1}).to_have_key("a")


@test_case(name="Verification Test 3", tags=["verify"])
class VerifyTest3(TestCase):
    async def execute_test(self):
        expect(3.14).to_be_close_to(3.1, tolerance=0.05)
        expect(None).to_be_none()
        expect(True).to_be_truthy()


async def main():
    print("🧪 Running verification tests...\n")

    runner = TestRunner(verbose=True)
    tests = [VerifyTest1, VerifyTest2, VerifyTest3]

    summary = await runner.run_tests(tests)

    print(f"\n📊 Summary:")
    print(f"  Total:   {summary.total}")
    print(f"  Passed:  {summary.passed}")
    print(f"  Failed:  {summary.failed}")
    print(f"  Success: {summary.success_rate():.1f}%")

    if summary.failed == 0:
        print("\n✅ All verification tests passed!")
        return 0
    else:
        print(f"\n❌ {summary.failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
