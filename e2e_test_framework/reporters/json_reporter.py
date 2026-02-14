"""
JSON report generator for CI/CD integration.
"""

import json
from typing import Any, Dict, List
from pathlib import Path
from datetime import datetime

from ..core.runner import TestRunSummary


class JSONReporter:
    """Generate JSON test reports."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(
        self,
        summary: TestRunSummary,
        filename: str = None,
        pretty: bool = True,
        include_details: bool = True
    ) -> str:
        """Generate JSON report."""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = self.output_dir / filename
        
        data = {
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "framework": "E2E Test Framework",
                "version": "1.0.0"
            },
            "summary": {
                "total": summary.total,
                "passed": summary.passed,
                "failed": summary.failed,
                "skipped": summary.skipped,
                "timeout": summary.timeout,
                "duration": summary.duration,
                "success_rate": summary.success_rate()
            },
            "tests": [r.to_dict() for r in summary.results] if include_details else []
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        return str(output_path)


class JUnitReporter:
    """Generate JUnit XML format for CI/CD systems."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, summary: TestRunSummary, filename: str = "junit.xml") -> str:
        """Generate JUnit XML report."""
        output_path = self.output_dir / filename
        
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append(f'<testsuites name="E2E Tests" tests="{summary.total}" failures="{summary.failed}" skipped="{summary.skipped}" time="{summary.duration:.3f}">')
        
        for result in summary.results:
            status_attr = ""
            if result.status == "skipped":
                status_attr = ' skipped="true"'
            elif result.status == "failed":
                status_attr = ' failure="true"'
            
            xml_lines.append(f'  <testcase name="{result.name}" time="{result.duration:.3f}"{status_attr}>')
            
            if result.status == "failed" and result.error:
                error_msg = str(result.error).replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
                xml_lines.append(f'    <failure message="{error_msg}">')
                if result.error_trace:
                    trace = result.error_trace.replace('<', '&lt;').replace('>', '&gt;')
                    xml_lines.append(f'<![CDATA[{trace}]]>')
                xml_lines.append('    </failure>')
            
            elif result.status == "skipped":
                skip_reason = result.metadata.get("skip_reason", "Test skipped")
                xml_lines.append(f'    <skipped message="{skip_reason}"/>')
            
            xml_lines.append('  </testcase>')
        
        xml_lines.append('</testsuites>')
        
        xml_content = '\n'.join(xml_lines)
        output_path.write_text(xml_content, encoding='utf-8')
        
        return str(output_path)


# CI/CD format helpers

def generate_json_report(summary: TestRunSummary, output_dir: str = "reports") -> str:
    """Generate JSON report."""
    reporter = JSONReporter(output_dir)
    return reporter.generate(summary)


def generate_junit_report(summary: TestRunSummary, output_dir: str = "reports") -> str:
    """Generate JUnit XML report."""
    reporter = JUnitReporter(output_dir)
    return reporter.generate(summary)


# GitHub Actions annotations

def generate_github_annotations(summary: TestRunSummary) -> List[str]:
    """Generate GitHub Actions workflow annotations."""
    annotations = []
    
    for result in summary.results:
        if result.status == "failed":
            annotations.append(
                f"::error file=test.py,title=Test Failed::{result.name}: {result.error}"
            )
        elif result.status == "skipped":
            skip_reason = result.metadata.get("skip_reason", "Test skipped")
            annotations.append(
                f"::warning file=test.py,title=Test Skipped::{result.name}: {skip_reason}"
            )
    
    return annotations


# TeamCity format

def generate_teamcity_messages(summary: TestRunSummary) -> List[str]:
    """Generate TeamCity service messages."""
    messages = []
    
    for result in summary.results:
        test_name = result.name.replace("'", "|'")
        
        messages.append(f"##teamcity[testStarted name='{test_name}']")
        
        if result.status == "passed":
            messages.append(f"##teamcity[testFinished name='{test_name}' duration='{int(result.duration * 1000)}']")
        elif result.status == "failed":
            error = str(result.error).replace("'", "|'").replace("[", "|[").replace("]", "|]")
            messages.append(f"##teamcity[testFailed name='{test_name}' message='{error}']")
            messages.append(f"##teamcity[testFinished name='{test_name}' duration='{int(result.duration * 1000)}']")
        elif result.status == "skipped":
            messages.append(f"##teamcity[testIgnored name='{test_name}' message='Test skipped']")
    
    return messages
