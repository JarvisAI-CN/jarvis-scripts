"""
Test runner with parallel execution and reporting.
"""

from typing import List, Type, Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import json
import sys
import os

from .case import TestCase, TestResult, TestCaseInfo


@dataclass
class TestRunSummary:
    """Test run summary."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    timeout: int = 0
    duration: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    results: List[TestResult] = field(default_factory=list)
    
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100
    
    def to_dict(self) -> dict:
        """Serialize to dict."""
        return {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "timeout": self.timeout,
            "duration": self.duration,
            "success_rate": f"{self.success_rate():.1f}%",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results]
        }


class TestRunner:
    """Test execution engine."""
    
    def __init__(
        self,
        parallel: int = 1,
        stop_on_fail: bool = False,
        filter_tags: List[str] = None,
        filter_names: List[str] = None,
        verbose: bool = False,
        reporter: Callable = None
    ):
        self.parallel = parallel
        self.stop_on_fail = stop_on_fail
        self.filter_tags = set(filter_tags or [])
        self.filter_names = filter_names or []
        self.verbose = verbose
        self.reporter = reporter
        self.hooks = {
            'before_run': [],
            'after_run': [],
            'before_test': [],
            'after_test': [],
            'on_error': []
        }
        self.shared_context: Dict[str, Any] = {}
    
    def add_hook(self, event: str, callback: Callable):
        """Add lifecycle hook."""
        if event in self.hooks:
            self.hooks[event].append(callback)
    
    async def _run_hooks(self, event: str, *args, **kwargs):
        """Run hooks for event."""
        for hook in self.hooks.get(event, []):
            if asyncio.iscoroutinefunction(hook):
                await hook(*args, **kwargs)
            else:
                hook(*args, **kwargs)
    
    def _should_run(self, test_case: Type[TestCase]) -> bool:
        """Check if test should run based on filters."""
        info = test_case.get_info()
        
        # Tag filter
        if self.filter_tags and not self.filter_tags.intersection(set(info.tags)):
            return False
        
        # Name filter
        if self.filter_names and info.name not in self.filter_names:
            return False
        
        # Skip flag
        if info.skip:
            return False
        
        return True
    
    def _get_priority(self, test_case: Type[TestCase]) -> int:
        """Get test priority for sorting."""
        return test_case.get_info().priority
    
    async def _run_test(self, test_class: Type[TestCase]) -> TestResult:
        """Run a single test case."""
        info = test_class.get_info()
        
        # Check dependencies
        for dep in info.dependencies:
            dep_result = self.shared_context.get(f"result:{dep}")
            if dep_result and dep_result.status != "passed":
                result = TestResult(info.name)
                result.end("skipped")
                result.metadata["skip_reason"] = f"Dependency {dep} failed"
                return result
        
        await self._run_hooks('before_test', info)
        
        test_instance = test_class()
        test_instance.shared_context = self.shared_context
        result = await test_instance.run()
        
        self.shared_context[f"result:{info.name}"] = result
        
        await self._run_hooks('after_test', info, result)
        
        if result.status == "failed":
            await self._run_hooks('on_error', info, result, result.error)
        
        return result
    
    async def run_tests(
        self,
        test_cases: List[Type[TestCase]]
    ) -> TestRunSummary:
        """Run all test cases."""
        summary = TestRunSummary()
        summary.start_time = datetime.now()
        
        # Filter tests
        filtered_tests = [t for t in test_cases if self._should_run(t)]
        
        # Sort by priority
        filtered_tests.sort(key=self._get_priority, reverse=True)
        
        summary.total = len(filtered_tests)
        
        await self._run_hooks('before_run', filtered_tests)
        
        # Execute tests
        if self.parallel == 1:
            # Sequential execution
            for test_class in filtered_tests:
                if self.stop_on_fail and summary.failed > 0:
                    break
                
                result = await self._run_test(test_class)
                summary.results.append(result)
                
                if result.status == "passed":
                    summary.passed += 1
                elif result.status == "failed":
                    summary.failed += 1
                elif result.status == "timeout":
                    summary.timeout += 1
                elif result.status == "skipped":
                    summary.skipped += 1
                
                if self.verbose or result.status != "passed":
                    self._print_result(result)
        
        else:
            # Parallel execution
            semaphore = asyncio.Semaphore(self.parallel)
            
            async def run_with_semaphore(test_class):
                async with semaphore:
                    return await self._run_test(test_class)
            
            tasks = [run_with_semaphore(t) for t in filtered_tests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    result = TestResult("Unknown")
                    result.end("failed", result)
                
                summary.results.append(result)
                
                if result.status == "passed":
                    summary.passed += 1
                elif result.status == "failed":
                    summary.failed += 1
                elif result.status == "timeout":
                    summary.timeout += 1
                elif result.status == "skipped":
                    summary.skipped += 1
                
                if self.verbose or result.status != "passed":
                    self._print_result(result)
        
        summary.end_time = datetime.now()
        summary.duration = (summary.end_time - summary.start_time).total_seconds()
        
        await self._run_hooks('after_run', summary)
        
        # Print summary
        self._print_summary(summary)
        
        # Call reporter if provided
        if self.reporter:
            if asyncio.iscoroutinefunction(self.reporter):
                await self.reporter(summary)
            else:
                self.reporter(summary)
        
        return summary
    
    def _print_result(self, result: TestResult):
        """Print individual test result."""
        status_symbols = {
            "passed": "✅",
            "failed": "❌",
            "timeout": "⏱️",
            "skipped": "⏭️"
        }
        symbol = status_symbols.get(result.status, "❓")
        
        duration = f"{result.duration:.3f}s"
        retry_info = f" (retry {result.retry_count})" if result.retry_count > 0 else ""
        
        print(f"{symbol} {result.name} [{duration}]{retry_info}")
        
        if result.status == "failed" and self.verbose:
            print(f"   Error: {result.error}")
            if result.error_trace:
                print(f"   Trace: {result.error_trace[:200]}...")
    
    def _print_summary(self, summary: TestRunSummary):
        """Print test summary."""
        lines = [
            "",
            "=" * 60,
            "📊 Test Run Summary",
            "=" * 60,
            f"Total:    {summary.total}",
            f"Passed:   {summary.passed} ✅",
            f"Failed:   {summary.failed} ❌",
            f"Skipped:  {summary.skipped} ⏭️",
            f"Timeout:  {summary.timeout} ⏱️",
            f"Duration: {summary.duration:.2f}s",
            f"Success:  {summary.success_rate():.1f}%",
            "=" * 60,
        ]
        
        if summary.failed > 0:
            lines.append("\n❌ Failed tests:")
            for r in summary.results:
                if r.status == "failed":
                    lines.append(f"  - {r.name}: {r.error}")
        
        print("\n".join(lines))


class TestSuite:
    """Test suite organizer."""
    
    def __init__(self, name: str = "Test Suite"):
        self.name = name
        self.test_cases: List[Type[TestCase]] = []
        self.suites: List['TestSuite'] = []
        self.before_all: Optional[Callable] = None
        self.after_all: Optional[Callable] = None
    
    def add_test(self, test_class: Type[TestCase]):
        """Add test case to suite."""
        self.test_cases.append(test_class)
    
    def add_suite(self, suite: 'TestSuite'):
        """Add nested suite."""
        self.suites.append(suite)
    
    def add_tests(self, *test_classes: Type[TestCase]):
        """Add multiple test cases."""
        self.test_cases.extend(test_classes)
    
    def collect_all(self) -> List[Type[TestCase]]:
        """Collect all tests from this and nested suites."""
        all_tests = list(self.test_cases)
        for suite in self.suites:
            all_tests.extend(suite.collect_all())
        return all_tests
    
    async def run(
        self,
        parallel: int = 1,
        stop_on_fail: bool = False,
        filter_tags: List[str] = None,
        filter_names: List[str] = None,
        verbose: bool = False
    ) -> TestRunSummary:
        """Run all tests in suite."""
        runner = TestRunner(
            parallel=parallel,
            stop_on_fail=stop_on_fail,
            filter_tags=filter_tags,
            filter_names=filter_names,
            verbose=verbose
        )
        
        all_tests = self.collect_all()
        
        if self.before_all:
            if asyncio.iscoroutinefunction(self.before_all):
                await self.before_all()
            else:
                self.before_all()
        
        summary = await runner.run_tests(all_tests)
        
        if self.after_all:
            if asyncio.iscoroutinefunction(self.after_all):
                await self.after_all()
            else:
                self.after_all()
        
        return summary


def create_suite(name: str = "Test Suite") -> TestSuite:
    """Factory function to create test suite."""
    return TestSuite(name)


def run_tests(
    test_cases: List[Type[TestCase]],
    parallel: int = 1,
    stop_on_fail: bool = False,
    filter_tags: List[str] = None,
    filter_names: List[str] = None,
    verbose: bool = False
) -> TestRunSummary:
    """Convenience function to run tests."""
    runner = TestRunner(
        parallel=parallel,
        stop_on_fail=stop_on_fail,
        filter_tags=filter_tags,
        filter_names=filter_names,
        verbose=verbose
    )
    
    return asyncio.run(runner.run_tests(test_cases))


# Discovery helpers

def discover_tests(module_path: str, pattern: str = "test_*.py") -> List[Type[TestCase]]:
    """Discover test cases in a module."""
    import importlib.util
    import glob
    
    tests = []
    py_files = glob.glob(os.path.join(module_path, pattern))
    
    for py_file in py_files:
        module_name = os.path.splitext(os.path.basename(py_file))[0]
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, TestCase) and attr != TestCase:
                    tests.append(attr)
    
    return tests
