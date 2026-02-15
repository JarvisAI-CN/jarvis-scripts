#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# 添加当前目录到 sys.path 以支持导入
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from test_framework import run_tests
from security_test import VulnerabilityScanner, ConfigAuditor, PermissionChecker, DependencyChecker

def main():
    print("🚀 开始安全测试模块验证...")
    
    # 确保 test_results 目录存在
    Path("test_results").mkdir(exist_ok=True)
    
    project_root = current_dir.parent
    config_path = project_root / "配置/test_config.yaml"
    
    # 确保配置文件存在用于测试
    if not config_path.exists():
        print(f"⚠️ 配置文件未找到: {config_path}")
    
    tests = [
        VulnerabilityScanner(target_path=str(current_dir), name="代码漏洞扫描"),
        ConfigAuditor(config_file=str(config_path), name="配置审计"),
        PermissionChecker(target_dir=str(current_dir), name="权限检查"),
        DependencyChecker(name="依赖漏洞检查")
    ]
    
    # 执行测试
    run_tests(
        tests, 
        suite_name="SecurityModuleVerification",
        parallel=False # 安全测试涉及磁盘和子进程，建议顺序执行
    )

if __name__ == "__main__":
    main()
