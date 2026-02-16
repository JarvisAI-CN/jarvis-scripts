#!/usr/bin/env python3
"""
性能测试模块
版本: v1.0
创建: 2026-02-15
"""

import time
import psutil
import statistics
import threading
from typing import List, Callable, Optional, Dict, Any
from test_framework import TestCase, TestStatus, logger

class PerformanceTestCase(TestCase):
    """性能测试基类"""
    def __init__(self, name: Optional[str] = None, timeout: float = 300.0, threshold: float = 1.0):
        super().__init__(name, timeout)
        self.threshold = threshold
        self.metrics: Dict[str, Any] = {}

class ResponseTimeTest(PerformanceTestCase):
    """响应时间测试"""
    def __init__(self, name: str, func: Callable, threshold: float = 1.0, iterations: int = 5):
        super().__init__(name, threshold=threshold)
        self.func = func
        self.iterations = iterations

    def run_test(self) -> None:
        durations = []
        for i in range(self.iterations):
            start = time.time()
            self.func()
            duration = time.time() - start
            durations.append(duration)
            logger.info(f"Iteration {i+1}: {duration:.4f}s")

        avg_duration = statistics.mean(durations)
        max_duration = max(durations)
        self.metadata['avg_duration'] = avg_duration
        self.metadata['max_duration'] = max_duration
        self.metadata['iterations'] = self.iterations

        self.assert_true(avg_duration <= self.threshold, 
                        f"Average duration {avg_duration:.4f}s exceeded threshold {self.threshold}s")

class ThroughputTest(PerformanceTestCase):
    """吞吐量测试 (TPS)"""
    def __init__(self, name: str, func: Callable, duration: float = 5.0, threshold: float = 10.0):
        super().__init__(name, threshold=threshold)
        self.func = func
        self.test_duration = duration

    def run_test(self) -> None:
        count = 0
        end_time = time.time() + self.test_duration
        start_time = time.time()
        
        while time.time() < end_time:
            self.func()
            count += 1
            
        actual_duration = time.time() - start_time
        tps = count / actual_duration if actual_duration > 0 else 0
        self.metadata['total_count'] = count
        self.metadata['tps'] = tps
        self.metadata['duration'] = actual_duration

        self.assert_true(tps >= self.threshold, 
                        f"TPS {tps:.2f} is lower than threshold {self.threshold}")

class ResourceUsageTest(PerformanceTestCase):
    """资源使用测试 (CPU/Memory)"""
    def __init__(self, name: str, func: Callable, cpu_threshold: float = 80.0, mem_threshold_mb: float = 512.0):
        super().__init__(name)
        self.func = func
        self.cpu_threshold = cpu_threshold
        self.mem_threshold_mb = mem_threshold_mb
        self.is_running = False

    def run_test(self) -> None:
        proc = psutil.Process()
        cpu_usages = []
        mem_usages = []
        
        def monitor():
            while self.is_running:
                cpu_usages.append(proc.cpu_percent(interval=0.1))
                mem_usages.append(proc.memory_info().rss / 1024 / 1024)
                time.sleep(0.1)

        self.is_running = True
        monitor_thread = threading.Thread(target=monitor, name="ResourceMonitor")
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            self.func()
        finally:
            self.is_running = False
            monitor_thread.join(timeout=1.0)

        if cpu_usages:
            max_cpu = max(cpu_usages)
            avg_cpu = statistics.mean(cpu_usages)
            max_mem = max(mem_usages)
            avg_mem = statistics.mean(mem_usages)
            
            self.metadata['max_cpu'] = max_cpu
            self.metadata['avg_cpu'] = avg_cpu
            self.metadata['max_mem_mb'] = max_mem
            self.metadata['avg_mem_mb'] = avg_mem
            
            self.assert_true(max_cpu <= self.cpu_threshold, f"Max CPU {max_cpu}% exceeded {self.cpu_threshold}%")
            self.assert_true(max_mem <= self.mem_threshold_mb, f"Max Memory {max_mem:.2f}MB exceeded {self.mem_threshold_mb}MB")

if __name__ == "__main__":
    # 示例测试：测试一个简单的排序操作
    import random
    
    def sorting_task():
        data = [random.random() for _ in range(100000)]
        data.sort()

    print("Running ResponseTimeTest...")
    rt_test = ResponseTimeTest("SortingResponseTime", sorting_task, threshold=0.5)
    result = rt_test.execute()
    print(f"Result: {result.status.value}, Avg Duration: {result.metadata.get('avg_duration'):.4f}s")

    print("\nRunning ThroughputTest...")
    tp_test = ThroughputTest("SortingThroughput", sorting_task, duration=2.0, threshold=5.0)
    result = tp_test.execute()
    print(f"Result: {result.status.value}, TPS: {result.metadata.get('tps'):.2f}")

    print("\nRunning ResourceUsageTest...")
    ru_test = ResourceUsageTest("SortingResourceUsage", sorting_task, cpu_threshold=90.0)
    result = ru_test.execute()
    print(f"Result: {result.status.value}, Max CPU: {result.metadata.get('max_cpu')}%, Max Mem: {result.metadata.get('max_mem_mb'):.2f}MB")
