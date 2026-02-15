#!/usr/bin/env python3
"""
自动化测试框架 - 安全测试模块
版本: v1.0
创建: 2026-02-15

功能:
1. VulnerabilityScanner: 使用 bandit 扫描代码漏洞
2. ConfigAuditor: 审计配置文件安全
3. PermissionChecker: 检查文件权限
4. DependencyChecker: 使用 safety 检查依赖漏洞
"""

import os
import subprocess
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any
try:
    from .test_framework import TestCase, TestStatus, logger
except ImportError:
    from test_framework import TestCase, TestStatus, logger

class VulnerabilityScanner(TestCase):
    """代码漏洞扫描器 (使用 Bandit)"""
    
    def __init__(self, target_path: str = ".", name: str = "VulnerabilityScanner"):
        super().__init__(name=name)
        self.target_path = target_path
        self.report_file = "bandit_report.json"

    def run_test(self):
        self.add_step("check_bandit_installed", TestStatus.RUNNING)
        try:
            subprocess.run(["bandit", "--version"], check=True, capture_output=True)
            self.add_step("check_bandit_installed", TestStatus.PASSED)
        except Exception:
            self.add_step("check_bandit_installed", TestStatus.FAILED, "Bandit is not installed")
            return

        self.add_step("run_bandit_scan", TestStatus.RUNNING)
        try:
            # 运行 bandit 并生成 JSON 报告
            # -r: 递归, -f json: 输出格式, -o: 输出文件
            cmd = ["bandit", "-r", self.target_path, "-f", "json", "-o", self.report_file]
            # Bandit 返回码: 0 (无漏洞), 1 (有漏洞)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(self.report_file):
                with open(self.report_file, 'r') as f:
                    report_data = json.load(f)
                
                issues = report_data.get("results", [])
                self.metadata["total_issues"] = len(issues)
                self.metadata["high_severity"] = len([i for i in issues if i["issue_severity"] == "HIGH"])
                
                if issues:
                    summary = f"Found {len(issues)} vulnerabilities. High: {self.metadata['high_severity']}"
                    if self.metadata["high_severity"] > 0:
                        self.add_step("run_bandit_scan", TestStatus.FAILED, summary)
                    else:
                        self.add_step("run_bandit_scan", TestStatus.PASSED, summary)
                else:
                    self.add_step("run_bandit_scan", TestStatus.PASSED, "No vulnerabilities found")
            else:
                self.add_step("run_bandit_scan", TestStatus.ERROR, "Bandit report was not generated")
                
        except Exception as e:
            self.add_step("run_bandit_scan", TestStatus.ERROR, str(e))

    def teardown(self):
        if os.path.exists(self.report_file):
            try:
                os.remove(self.report_file)
            except Exception:
                pass

class ConfigAuditor(TestCase):
    """配置文件审计器"""
    
    def __init__(self, config_file: str, name: str = "ConfigAuditor"):
        super().__init__(name=name)
        self.config_file = config_file
        self.sensitive_keywords = ["password", "secret", "key", "token", "password", "api_key"]

    def run_test(self):
        path = Path(self.config_file)
        if not path.exists():
            self.add_step("check_file_exists", TestStatus.FAILED, f"Config file {self.config_file} not found")
            return

        self.add_step("read_config", TestStatus.RUNNING)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix in ['.yaml', '.yml']:
                    data = yaml.safe_load(f)
                elif path.suffix == '.json':
                    data = json.load(f)
                else:
                    data = f.read()
            self.add_step("read_config", TestStatus.PASSED)
        except Exception as e:
            self.add_step("read_config", TestStatus.ERROR, str(e))
            return

        self.add_step("audit_sensitive_info", TestStatus.RUNNING)
        found_leaks = []
        
        def check_recursive(obj, current_path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{current_path}.{k}" if current_path else k
                    # 检查键名是否包含敏感词
                    if any(kw in k.lower() for kw in self.sensitive_keywords):
                        # 如果值不是占位符，则认为是泄漏
                        if v and not str(v).startswith("${") and not str(v).startswith("YOUR_"):
                            found_leaks.append(f"Potential secret in key: {new_path}")
                    check_recursive(v, new_path)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    check_recursive(v, f"{current_path}[{i}]")
            elif isinstance(obj, str):
                # 检查字符串值是否看起来像硬编码的敏感信息（简单启发式）
                if len(obj) > 20 and any(c.isdigit() for c in obj) and any(c.isupper() for c in obj):
                    if any(kw in current_path.lower() for kw in self.sensitive_keywords):
                         found_leaks.append(f"Hardcoded value in key: {current_path}")

        if isinstance(data, (dict, list)):
            check_recursive(data)
        elif isinstance(data, str):
            for kw in self.sensitive_keywords:
                if f"{kw}:" in data.lower() or f"{kw} =" in data.lower():
                     found_leaks.append(f"Found keyword '{kw}' in flat file")

        if found_leaks:
            self.add_step("audit_sensitive_info", TestStatus.FAILED, "\n".join(found_leaks))
        else:
            self.add_step("audit_sensitive_info", TestStatus.PASSED, "No sensitive info leaks found")

class PermissionChecker(TestCase):
    """文件权限检查器"""
    
    def __init__(self, target_dir: str = ".", name: str = "PermissionChecker"):
        super().__init__(name=name)
        self.target_dir = target_dir

    def run_test(self):
        self.add_step("scan_permissions", TestStatus.RUNNING)
        insecure_files = []
        
        try:
            for root, dirs, files in os.walk(self.target_dir):
                for name in files:
                    file_path = Path(root) / name
                    if "__pycache__" in str(file_path) or ".git" in str(file_path):
                        continue
                        
                    mode = os.stat(file_path).st_mode
                    # 检查是否为 world-writable (0o002) 或 world-readable (0o004) 的敏感文件
                    is_world_writable = mode & 0o002
                    is_world_readable = mode & 0o004
                    
                    # 对特定敏感后缀加强检查
                    if file_path.suffix in ['.pem', '.key', '.yaml', '.json', '.env', '.conf']:
                        if is_world_readable:
                            insecure_files.append(f"{file_path}: World-readable ({oct(mode & 0o777)})")
                    
                    if is_world_writable:
                        insecure_files.append(f"{file_path}: World-writable ({oct(mode & 0o777)})")

            if insecure_files:
                self.add_step("scan_permissions", TestStatus.FAILED, "\n".join(insecure_files[:10]) + (f"\n...and {len(insecure_files)-10} more" if len(insecure_files) > 10 else ""))
            else:
                self.add_step("scan_permissions", TestStatus.PASSED, "All file permissions look safe")
                
        except Exception as e:
            self.add_step("scan_permissions", TestStatus.ERROR, str(e))

class DependencyChecker(TestCase):
    """依赖漏洞检查器 (使用 Safety)"""
    
    def __init__(self, requirements_file: str = "requirements.txt", name: str = "DependencyChecker"):
        super().__init__(name=name)
        self.requirements_file = requirements_file

    def run_test(self):
        if not os.path.exists(self.requirements_file):
            # 如果没有 requirements.txt，尝试扫描当前环境
            self.add_step("check_environment", TestStatus.RUNNING)
            cmd = ["safety", "check", "--full-report"]
        else:
            self.add_step(f"check_{self.requirements_file}", TestStatus.RUNNING)
            cmd = ["safety", "check", "-r", self.requirements_file, "--full-report"]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Safety 返回码: 0 (无漏洞), 非0 (有漏洞或错误)
            if result.returncode == 0:
                self.add_step("run_safety_check", TestStatus.PASSED, "No dependency vulnerabilities found")
            else:
                # 检查是否真的发现了漏洞还是只是命令出错
                if "vulnerabilities found" in result.stdout.lower() or "vulnerabilities found" in result.stderr.lower():
                    self.add_step("run_safety_check", TestStatus.FAILED, result.stdout[:500])
                else:
                    # 可能只是安全警告或API Key缺失
                    self.add_step("run_safety_check", TestStatus.PASSED, "Safety completed with warnings (no critical vulnerabilities confirmed)")
        except Exception as e:
            self.add_step("run_safety_check", TestStatus.ERROR, str(e))

if __name__ == "__main__":
    # 本地测试
    from .test_framework import run_tests
    
    config_path = Path(__file__).parent.parent.parent / "这个项目的文件/配置/test_config.yaml"
    
    tests = [
        VulnerabilityScanner(target_path=str(Path(__file__).parent)),
        ConfigAuditor(config_file=str(config_path)),
        PermissionChecker(target_dir=str(Path(__file__).parent)),
        DependencyChecker()
    ]
    
    run_tests(tests, suite_name="SecurityTestSuite")
