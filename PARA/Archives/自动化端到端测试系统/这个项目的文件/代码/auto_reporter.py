#!/usr/bin/env python3
"""
自动化端到端测试系统 - 自动报告生成器

功能:
1. TrendAnalyzer: 加载历史测试数据，对比分析趋势，识别性能退化
2. AlertManager: 根据测试结果生成告警摘要
3. Markdown生成: 生成详细的Markdown测试报告
4. 飞书集成: 支持将报告发送到飞书

版本: v1.0
创建: 2026-02-16
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import statistics

# 导入测试框架
try:
    from test_framework import TestStatus, logger
except ImportError:
    # 如果无法导入，定义最小化的枚举
    class TestStatus:
        PENDING = "pending"
        RUNNING = "running"
        PASSED = "passed"
        FAILED = "failed"
        SKIPPED = "skipped"
        ERROR = "error"

    import logging
    logger = logging.getLogger(__name__)


# ==================== 数据结构 ====================

@dataclass
class TestMetric:
    """测试指标数据类"""
    name: str
    duration: float
    status: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestMetric':
        """从字典创建 TestMetric"""
        return cls(
            name=data.get("name", ""),
            duration=data.get("duration", 0.0),
            status=data.get("status", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {})
        )


@dataclass
class ComparisonResult:
    """对比结果数据类"""
    test_name: str
    current_duration: float
    baseline_duration: float
    duration_change_percent: float
    current_status: str
    baseline_status: str
    is_regression: bool
    is_improvement: bool
    metadata_current: Dict[str, Any] = field(default_factory=dict)
    metadata_baseline: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """告警数据类"""
    level: str  # "critical", "warning", "info"
    category: str  # "test_failure", "performance_regression", "error"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


# ==================== TrendAnalyzer ====================

class TrendAnalyzer:
    """
    趋势分析器

    功能:
    1. 加载 test_results/ 目录中的历史 JSON 数据
    2. 对比当前结果与历史基准
    3. 识别显著的性能退化（如耗时增加 > 20%）
    """

    def __init__(self, results_dir: Optional[Path] = None):
        """
        初始化趋势分析器

        Args:
            results_dir: 测试结果目录（默认为代码目录/test_results/）
        """
        if results_dir is None:
            # 默认为代码目录下的 test_results/
            self.results_dir = Path(__file__).parent / "test_results"
        else:
            self.results_dir = Path(results_dir)

        self.historical_data: List[Dict[str, Any]] = []
        self.comparison_results: List[ComparisonResult] = []

    def load_historical_data(self, max_results: int = 10) -> None:
        """
        加载历史测试数据

        Args:
            max_results: 最多加载的历史结果数量
        """
        if not self.results_dir.exists():
            logger.warning(f"Results directory not found: {self.results_dir}")
            return

        # 获取所有 JSON 文件
        json_files = sorted(self.results_dir.glob("report_*.json"), reverse=True)

        # 加载最近的 N 个结果
        for json_file in json_files[:max_results]:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.historical_data.append(data)
                    logger.info(f"Loaded historical data: {json_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {json_file}: {e}")

        logger.info(f"Total historical records loaded: {len(self.historical_data)}")

    def get_baseline(self, test_name: str, metric_type: str = "duration") -> Optional[float]:
        """
        获取指定测试的基准值（历史平均值）

        Args:
            test_name: 测试名称
            metric_type: 指标类型（duration, success_rate等）

        Returns:
            基准值，如果没有历史数据则返回 None
        """
        if not self.historical_data:
            return None

        values = []
        for record in self.historical_data:
            # 跳过当前结果（如果已包含）
            for test_case in record.get("test_cases", []):
                if test_case.get("name") == test_name:
                    if metric_type == "duration":
                        values.append(test_case.get("duration", 0.0))
                    elif metric_type == "success_rate":
                        # 从 suite 级别获取
                        values.append(record.get("success_rate", 0.0))

        if not values:
            return None

        # 返回平均值作为基准
        return statistics.mean(values)

    def compare_with_baseline(
        self,
        current_result: Dict[str, Any],
        regression_threshold: float = 20.0
    ) -> List[ComparisonResult]:
        """
        对比当前结果与历史基准

        Args:
            current_result: 当前测试结果（TestSuiteResult.to_dict()的输出）
            regression_threshold: 退化阈值（百分比）

        Returns:
            对比结果列表
        """
        self.comparison_results = []

        for test_case in current_result.get("test_cases", []):
            test_name = test_case.get("name", "")
            current_duration = test_case.get("duration", 0.0)
            current_status = test_case.get("status", "")

            # 获取基准值
            baseline_duration = self.get_baseline(test_name, "duration")
            baseline_status = self.get_baseline_status(test_name)

            if baseline_duration is None:
                # 没有历史数据，跳过
                continue

            # 计算变化百分比
            if baseline_duration > 0:
                duration_change_percent = ((current_duration - baseline_duration) / baseline_duration) * 100
            else:
                duration_change_percent = 0.0

            # 判断是否退化或改进
            is_regression = (
                duration_change_percent > regression_threshold and
                current_status != TestStatus.PASSED
            )
            is_improvement = (
                duration_change_percent < -regression_threshold or
                (baseline_status != TestStatus.PASSED and current_status == TestStatus.PASSED)
            )

            comparison = ComparisonResult(
                test_name=test_name,
                current_duration=current_duration,
                baseline_duration=baseline_duration,
                duration_change_percent=duration_change_percent,
                current_status=current_status,
                baseline_status=baseline_status or TestStatus.PENDING,
                is_regression=is_regression,
                is_improvement=is_improvement,
                metadata_current=test_case.get("metadata", {}),
                metadata_baseline={}
            )

            self.comparison_results.append(comparison)

        return self.comparison_results

    def get_baseline_status(self, test_name: str) -> Optional[str]:
        """获取测试的历史状态（最近一次）"""
        for record in self.historical_data:
            for test_case in record.get("test_cases", []):
                if test_case.get("name") == test_name:
                    return test_case.get("status", "")
        return None

    def get_suite_summary(self) -> Dict[str, Any]:
        """获取测试套件摘要统计"""
        if not self.historical_data:
            return {}

        # 计算平均成功率
        success_rates = [r.get("success_rate", 0) for r in self.historical_data]
        avg_success_rate = statistics.mean(success_rates) if success_rates else 0

        # 计算平均总耗时
        durations = [r.get("duration", 0) for r in self.historical_data]
        avg_duration = statistics.mean(durations) if durations else 0

        return {
            "avg_success_rate": round(avg_success_rate, 2),
            "avg_duration": round(avg_duration, 2),
            "total_runs": len(self.historical_data)
        }


# ==================== AlertManager ====================

class AlertManager:
    """
    告警管理器

    功能:
    1. 定义告警逻辑
    2. 生成告警摘要
    """

    def __init__(
        self,
        failure_threshold: float = 100.0,
        regression_threshold: float = 20.0
    ):
        """
        初始化告警管理器

        Args:
            failure_threshold: 成功率告警阈值（低于此值触发告警）
            regression_threshold: 性能退化阈值（百分比）
        """
        self.failure_threshold = failure_threshold
        self.regression_threshold = regression_threshold
        self.alerts: List[Alert] = []

    def check_suite_result(self, result: Dict[str, Any]) -> List[Alert]:
        """
        检查测试套件结果并生成告警

        Args:
            result: 测试套件结果

        Returns:
            告警列表
        """
        self.alerts = []

        success_rate = result.get("success_rate", 0)
        total = result.get("total", 0)
        passed = result.get("passed", 0)
        failed = result.get("failed", 0)
        errors = result.get("errors", 0)

        # 1. 检查成功率
        if success_rate < self.failure_threshold:
            if success_rate < 50:
                level = "critical"
            elif success_rate < 80:
                level = "warning"
            else:
                level = "info"

            self.alerts.append(Alert(
                level=level,
                category="test_failure",
                message=f"测试成功率 {success_rate}% 低于阈值 {self.failure_threshold}%",
                details={
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "success_rate": success_rate
                }
            ))

        # 2. 检查失败的测试用例
        failed_tests = []
        error_tests = []

        for test_case in result.get("test_cases", []):
            status = test_case.get("status", "")
            if status == TestStatus.FAILED:
                failed_tests.append(test_case.get("name", ""))
            elif status == TestStatus.ERROR:
                error_tests.append(test_case.get("name", ""))

        if failed_tests:
            self.alerts.append(Alert(
                level="warning",
                category="test_failure",
                message=f"有 {len(failed_tests)} 个测试失败",
                details={"failed_tests": failed_tests}
            ))

        if error_tests:
            self.alerts.append(Alert(
                level="critical",
                category="test_failure",
                message=f"有 {len(error_tests)} 个测试出错",
                details={"error_tests": error_tests}
            ))

        return self.alerts

    def check_performance_regression(
        self,
        comparisons: List[ComparisonResult]
    ) -> List[Alert]:
        """
        检查性能退化并生成告警

        Args:
            comparisons: 对比结果列表

        Returns:
            告警列表
        """
        regression_alerts = []

        for comp in comparisons:
            if comp.is_regression:
                regression_alerts.append(Alert(
                    level="warning",
                    category="performance_regression",
                    message=f"测试 '{comp.test_name}' 性能退化: 耗时增加 {comp.duration_change_percent:.1f}%",
                    details={
                        "test_name": comp.test_name,
                        "current_duration": comp.current_duration,
                        "baseline_duration": comp.baseline_duration,
                        "change_percent": comp.duration_change_percent
                    }
                ))

        self.alerts.extend(regression_alerts)
        return regression_alerts

    def generate_alert_summary(self) -> str:
        """生成告警摘要文本"""
        if not self.alerts:
            return "✅ 无告警"

        lines = []
        critical_count = sum(1 for a in self.alerts if a.level == "critical")
        warning_count = sum(1 for a in self.alerts if a.level == "warning")
        info_count = sum(1 for a in self.alerts if a.level == "info")

        if critical_count > 0:
            lines.append(f"🔴 严重告警: {critical_count}")
        if warning_count > 0:
            lines.append(f"⚠️ 警告: {warning_count}")
        if info_count > 0:
            lines.append(f"ℹ️ 信息: {info_count}")

        return "\n".join(lines)


# ==================== Markdown报告生成器 ====================

class MarkdownReporter:
    """
    Markdown报告生成器

    功能:
    1. 生成详细且排版精美的Markdown测试报告
    2. 支持趋势分析和告警信息
    """

    def __init__(
        self,
        result: Dict[str, Any],
        analyzer: Optional[TrendAnalyzer] = None,
        alerts: Optional[List[Alert]] = None
    ):
        """
        初始化报告生成器

        Args:
            result: 测试套件结果
            analyzer: 趋势分析器（可选）
            alerts: 告警列表（可选）
        """
        self.result = result
        self.analyzer = analyzer
        self.alerts = alerts or []

    def generate(self) -> str:
        """生成完整的Markdown报告"""
        lines = []

        # 标题和概览
        lines.extend(self._generate_header())
        lines.append("")

        # 执行摘要
        lines.extend(self._generate_summary())
        lines.append("")

        # 告警信息
        if self.alerts:
            lines.extend(self._generate_alerts())
            lines.append("")

        # 趋势分析
        if self.analyzer and self.analyzer.comparison_results:
            lines.extend(self._generate_trend_analysis())
            lines.append("")

        # 测试用例详情
        lines.extend(self._generate_test_details())
        lines.append("")

        # 失败/错误详情
        lines.extend(self._generate_failure_details())
        lines.append("")

        # 页脚
        lines.extend(self._generate_footer())

        return "\n".join(lines)

    def _generate_header(self) -> List[str]:
        """生成报告头部"""
        suite_name = self.result.get("suite_name", "TestSuite")
        start_time = self.result.get("start_time", "")
        end_time = self.result.get("end_time", "")

        return [
            "# 📊 自动化端到端测试报告",
            "",
            f"**测试套件**: {suite_name}",
            f"**开始时间**: {self._format_datetime(start_time)}",
            f"**结束时间**: {self._format_datetime(end_time)}",
            f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---"
        ]

    def _generate_summary(self) -> List[str]:
        """生成执行摘要"""
        total = self.result.get("total", 0)
        passed = self.result.get("passed", 0)
        failed = self.result.get("failed", 0)
        errors = self.result.get("errors", 0)
        skipped = self.result.get("skipped", 0)
        duration = self.result.get("duration", 0)
        success_rate = self.result.get("success_rate", 0)

        # 根据成功率选择emoji
        if success_rate == 100:
            status_emoji = "✅"
        elif success_rate >= 80:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        return [
            "## 📋 执行摘要",
            "",
            f"{status_emoji} **状态**: {self._get_status_text(success_rate)}",
            "",
            "| 指标 | 数值 |",
            "|------|------|",
            f"| 总用例数 | {total} |",
            f"| ✅ 通过 | {passed} |",
            f"| ❌ 失败 | {failed} |",
            f"| ⚠️ 错误 | {errors} |",
            f"| ⏭️ 跳过 | {skipped} |",
            f"| 📈 成功率 | {success_rate}% |",
            f"| ⏱️ 总耗时 | {duration:.2f}s |",
            "",
            "### 成功率分布",
            "",
            self._generate_progress_bar(success_rate),
            f"**{success_rate}%**",
        ]

    def _generate_alerts(self) -> List[str]:
        """生成告警信息"""
        lines = [
            "## 🚨 告警信息",
            ""
        ]

        # 按级别分组
        critical = [a for a in self.alerts if a.level == "critical"]
        warning = [a for a in self.alerts if a.level == "warning"]
        info = [a for a in self.alerts if a.level == "info"]

        if critical:
            lines.append("### 🔴 严重告警")
            lines.append("")
            for alert in critical:
                lines.append(f"- **{alert.message}**")
                if alert.details:
                    lines.append(f"  - 详情: `{json.dumps(alert.details, ensure_ascii=False)}`")
            lines.append("")

        if warning:
            lines.append("### ⚠️ 警告")
            lines.append("")
            for alert in warning:
                lines.append(f"- **{alert.message}**")
                if alert.details:
                    lines.append(f"  - 详情: `{json.dumps(alert.details, ensure_ascii=False)}`")
            lines.append("")

        if info:
            lines.append("### ℹ️ 信息")
            lines.append("")
            for alert in info:
                lines.append(f"- {alert.message}")
            lines.append("")

        return lines

    def _generate_trend_analysis(self) -> List[str]:
        """生成趋势分析"""
        lines = [
            "## 📈 趋势分析",
            ""
        ]

        comparisons = self.analyzer.comparison_results if self.analyzer else []

        if not comparisons:
            lines.append("*暂无历史数据对比*")
            return lines

        # 统计
        regressions = [c for c in comparisons if c.is_regression]
        improvements = [c for c in comparisons if c.is_improvement]

        lines.append(f"- 📊 对比测试用例: **{len(comparisons)}**")
        lines.append(f"- ⚠️ 性能退化: **{len(regressions)}**")
        lines.append(f"- ✅ 性能改进: **{len(improvements)}**")
        lines.append("")

        # 退化详情
        if regressions:
            lines.append("### 性能退化详情")
            lines.append("")
            lines.append("| 测试用例 | 当前耗时 | 基准耗时 | 变化 |")
            lines.append("|----------|----------|----------|------|")

            for comp in regressions:
                change_str = f"+{comp.duration_change_percent:.1f}%"
                lines.append(
                    f"| {comp.test_name} | "
                    f"{comp.current_duration:.3f}s | "
                    f"{comp.baseline_duration:.3f}s | "
                    f"🔴 {change_str} |"
                )
            lines.append("")

        # 改进详情
        if improvements:
            lines.append("### 性能改进详情")
            lines.append("")
            lines.append("| 测试用例 | 当前耗时 | 基准耗时 | 变化 |")
            lines.append("|----------|----------|----------|------|")

            for comp in improvements:
                change_str = f"{comp.duration_change_percent:.1f}%"
                emoji = "✅" if comp.current_status == TestStatus.PASSED else "🟢"
                lines.append(
                    f"| {comp.test_name} | "
                    f"{comp.current_duration:.3f}s | "
                    f"{comp.baseline_duration:.3f}s | "
                    f"{emoji} {change_str} |"
                )
            lines.append("")

        return lines

    def _generate_test_details(self) -> List[str]:
        """生成测试用例详情"""
        lines = [
            "## 🧪 测试用例详情",
            "",
            "| 测试用例 | 状态 | 耗时 | 元数据 |",
            "|----------|------|------|--------|"
        ]

        for test_case in self.result.get("test_cases", []):
            name = test_case.get("name", "")
            status = test_case.get("status", "")
            duration = test_case.get("duration", 0)
            metadata = test_case.get("metadata", {})

            # 状态emoji
            status_emoji = self._get_status_emoji(status)

            # 元数据摘要
            metadata_str = ""
            if metadata:
                items = [f"{k}={v}" for k, v in list(metadata.items())[:3]]
                metadata_str = "`" + ", ".join(items) + "`"

            lines.append(
                f"| {name} | "
                f"{status_emoji} {status} | "
                f"{duration:.3f}s | "
                f"{metadata_str} |"
            )

        return lines

    def _generate_failure_details(self) -> List[str]:
        """生成失败/错误详情"""
        lines = [
            "## ❌ 失败/错误详情",
            ""
        ]

        failures = [
            tc for tc in self.result.get("test_cases", [])
            if tc.get("status") in [TestStatus.FAILED, TestStatus.ERROR]
        ]

        if not failures:
            lines.append("*无失败或错误*")
            return lines

        for tc in failures:
            name = tc.get("name", "")
            status = tc.get("status", "")
            error_msg = tc.get("error_message", "")
            error_trace = tc.get("error_trace", "")
            steps = tc.get("steps", [])

            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"**状态**: {status}")
            lines.append("")

            if error_msg:
                lines.append("**错误信息**:")
                lines.append("```")
                lines.append(error_msg)
                lines.append("```")
                lines.append("")

            if steps:
                lines.append("**执行步骤**:")
                lines.append("")
                for step in steps:
                    step_name = step.get("name", "")
                    step_status = step.get("status", "")
                    step_duration = step.get("duration", 0)
                    step_error = step.get("error", "")

                    step_emoji = self._get_status_emoji(step_status)
                    lines.append(f"- {step_emoji} **{step_name}** ({step_status}) - {step_duration:.3f}s")

                    if step_error:
                        lines.append(f"  - 错误: {step_error}")
                lines.append("")

        return lines

    def _generate_footer(self) -> List[str]:
        """生成页脚"""
        return [
            "---",
            "",
            "*本报告由自动化端到端测试系统生成*",
            f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ]

    def _format_datetime(self, dt_str: str) -> str:
        """格式化日期时间"""
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str

    def _get_status_text(self, success_rate: float) -> str:
        """根据成功率获取状态文本"""
        if success_rate == 100:
            return "全部通过"
        elif success_rate >= 80:
            return "基本通过"
        elif success_rate >= 50:
            return "部分失败"
        else:
            return "严重失败"

    def _get_status_emoji(self, status: str) -> str:
        """根据状态获取emoji"""
        emoji_map = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.ERROR: "⚠️",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.PENDING: "⏳",
            TestStatus.RUNNING: "🔄"
        }
        return emoji_map.get(status, "❓")

    def _generate_progress_bar(self, percentage: float, width: int = 20) -> str:
        """生成进度条"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)

        # 根据百分比选择颜色
        if percentage >= 80:
            color = "🟢"
        elif percentage >= 50:
            color = "🟡"
        else:
            color = "🔴"

        return f"{color} [{bar}]"


# ==================== 飞书集成 ====================

class FeishuIntegration:
    """
    飞书集成

    功能:
    1. 将测试报告转换为飞书卡片格式
    2. 发送到飞书群（使用飞书webhook或OpenClaw message工具）
    """

    def __init__(
        self,
        result: Dict[str, Any],
        alerts: Optional[List[Alert]] = None
    ):
        """
        初始化飞书集成

        Args:
            result: 测试套件结果
            alerts: 告警列表（可选）
        """
        self.result = result
        self.alerts = alerts or []

    def generate_card_content(self) -> Dict[str, Any]:
        """
        生成飞书卡片内容

        Returns:
            飞书卡片格式的字典
        """
        success_rate = self.result.get("success_rate", 0)
        total = self.result.get("total", 0)
        passed = self.result.get("passed", 0)
        failed = self.result.get("failed", 0)
        errors = self.result.get("errors", 0)
        duration = self.result.get("duration", 0)

        # 状态颜色
        if success_rate == 100:
            status_color = "green"
            status_text = "✅ 全部通过"
        elif success_rate >= 80:
            status_color = "yellow"
            status_text = "⚠️ 基本通过"
        else:
            status_color = "red"
            status_text = "❌ 存在失败"

        # 构建卡片
        card = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "📊 测试报告"
                    },
                    "template": status_color
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**状态**: {status_text}\n"
                                      f"**成功率**: {success_rate}%\n"
                                      f"**总耗时**: {duration:.2f}s"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**测试统计**:\n"
                                      f"- 总用例: {total}\n"
                                      f"- ✅ 通过: {passed}\n"
                                      f"- ❌ 失败: {failed}\n"
                                      f"- ⚠️ 错误: {errors}"
                        }
                    }
                ]
            }
        }

        # 添加告警信息
        if self.alerts:
            alert_lines = []
            for alert in self.alerts[:5]:  # 最多显示5条
                if alert.level == "critical":
                    alert_lines.append(f"🔴 {alert.message}")
                elif alert.level == "warning":
                    alert_lines.append(f"⚠️ {alert.message}")
                else:
                    alert_lines.append(f"ℹ️ {alert.message}")

            if alert_lines:
                card["card"]["elements"].append(
                    {
                        "tag": "hr"
                    }
                )
                card["card"]["elements"].append(
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": "**告警信息**:\n" + "\n".join(alert_lines)
                        }
                    }
                )

        return card

    def send_summary(self) -> str:
        """
        生成文本摘要（用于发送到飞书）

        Returns:
            摘要文本
        """
        success_rate = self.result.get("success_rate", 0)
        total = self.result.get("total", 0)
        passed = self.result.get("passed", 0)
        failed = self.result.get("failed", 0)
        errors = self.result.get("errors", 0)
        duration = self.result.get("duration", 0)
        end_time = self.result.get("end_time", "")

        # 状态emoji
        if success_rate == 100:
            status_emoji = "✅"
        elif success_rate >= 80:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"

        summary = f"""{status_emoji} 自动化端到端测试报告

📊 测试统计:
• 总用例: {total}
• ✅ 通过: {passed}
• ❌ 失败: {failed}
• ⚠️ 错误: {errors}

📈 成功率: {success_rate}%
⏱️ 总耗时: {duration:.2f}s

⏰ 完成时间: {self._format_datetime(end_time)}
"""

        # 添加告警
        if self.alerts:
            summary += "\n🚨 告警:\n"
            for alert in self.alerts[:3]:
                if alert.level == "critical":
                    summary += f"🔴 {alert.message}\n"
                elif alert.level == "warning":
                    summary += f"⚠️ {alert.message}\n"

        return summary.strip()

    def _format_datetime(self, dt_str: str) -> str:
        """格式化日期时间"""
        try:
            dt = datetime.fromisoformat(dt_str)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return dt_str


# ==================== 主执行函数 ====================

def generate_report(
    result_path: Optional[Path] = None,
    result_data: Optional[Dict[str, Any]] = None,
    output_path: Optional[Path] = None,
    enable_trend_analysis: bool = True,
    regression_threshold: float = 20.0
) -> Tuple[str, Dict[str, Any]]:
    """
    生成完整的测试报告

    Args:
        result_path: 测试结果JSON文件路径
        result_data: 测试结果数据（与result_path二选一）
        output_path: Markdown报告输出路径（默认为 ../文档/测试报告_latest.md）
        enable_trend_analysis: 是否启用趋势分析
        regression_threshold: 性能退化阈值（百分比）

    Returns:
        (Markdown报告内容, 报告元数据)
    """
    # 加载测试结果
    if result_data is None:
        if result_path is None:
            raise ValueError("必须提供 result_path 或 result_data")

        with open(result_path, 'r', encoding='utf-8') as f:
            result_data = json.load(f)

    # 趋势分析
    analyzer = None
    if enable_trend_analysis:
        analyzer = TrendAnalyzer()
        analyzer.load_historical_data(max_results=10)
        analyzer.compare_with_baseline(result_data, regression_threshold)

    # 告警检查
    alert_manager = AlertManager(regression_threshold=regression_threshold)
    alerts = alert_manager.check_suite_result(result_data)

    if analyzer:
        alerts.extend(alert_manager.check_performance_regression(analyzer.comparison_results))

    # 生成Markdown报告
    reporter = MarkdownReporter(result_data, analyzer, alerts)
    markdown_report = reporter.generate()

    # 保存报告
    if output_path is None:
        # 默认保存到 ../文档/测试报告_latest.md
        output_path = Path(__file__).parent.parent / "文档" / "测试报告_latest.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown_report, encoding='utf-8')

    logger.info(f"Markdown report saved to: {output_path}")

    # 返回报告和元数据
    metadata = {
        "output_path": str(output_path),
        "alerts_count": len(alerts),
        "has_regressions": any(c.is_regression for c in analyzer.comparison_results) if analyzer else False,
        "success_rate": result_data.get("success_rate", 0)
    }

    return markdown_report, metadata


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="自动化端到端测试系统 - 自动报告生成器"
    )
    parser.add_argument(
        "--result",
        type=str,
        required=True,
        help="测试结果JSON文件路径"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Markdown报告输出路径"
    )
    parser.add_argument(
        "--no-trend",
        action="store_true",
        help="禁用趋势分析"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=20.0,
        help="性能退化阈值（百分比，默认：20%%）"
    )

    args = parser.parse_args()

    # 生成报告
    report, metadata = generate_report(
        result_path=Path(args.result),
        output_path=Path(args.output) if args.output else None,
        enable_trend_analysis=not args.no_trend,
        regression_threshold=args.threshold
    )

    # 打印摘要
    print("\n" + "=" * 70)
    print("报告生成完成")
    print("=" * 70)
    print(f"输出路径: {metadata['output_path']}")
    print(f"告警数量: {metadata['alerts_count']}")
    print(f"性能退化: {'是' if metadata['has_regressions'] else '否'}")
    print(f"成功率: {metadata['success_rate']}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
