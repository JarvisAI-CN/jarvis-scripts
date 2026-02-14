"""
Console reporter with colored output and progress bars.
"""

from typing import List, Optional
from datetime import datetime, timedelta

from ..core.runner import TestRunSummary


class ConsoleReporter:
    """Rich console reporting with colors and formatting."""
    
    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bg_red": "\033[41m",
        "bg_green": "\033[42m",
        "bg_yellow": "\033[44m",
    }
    
    def __init__(self, use_colors: bool = True, show_progress: bool = True):
        self.use_colors = use_colors and self._supports_color()
        self.show_progress = show_progress
        self._start_time: Optional[datetime] = None
        self._test_index = 0
    
    def _color(self, text: str, color: str) -> str:
        """Apply color to text."""
        if not self.use_colors:
            return text
        code = self.COLORS.get(color, "")
        reset = self.COLORS["reset"]
        return f"{code}{text}{reset}"
    
    def _supports_color(self) -> bool:
        """Check if terminal supports colors."""
        import sys
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def on_run_start(self, total_tests: int):
        """Called when test run starts."""
        self._start_time = datetime.now()
        self._test_index = 0
        
        lines = [
            "",
            "=" * 70,
            self._color("🚀 Starting Test Run", "bold", "blue"),
            f"Total tests: {total_tests}",
            f"Started at: {self._start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            ""
        ]
        
        print("\n".join(lines))
    
    def on_test_start(self, test_name: str):
        """Called when a test starts."""
        self._test_index += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self._color(f'[{self._test_index}]', 'dim')} Running: {test_name}...")
    
    def on_test_complete(self, test_name: str, status: str, duration: float, error: Optional[str] = None):
        """Called when a test completes."""
        status_symbols = {
            "passed": self._color("✅ PASS", "green"),
            "failed": self._color("❌ FAIL", "red"),
            "timeout": self._color("⏱️ TIME", "yellow"),
            "skipped": self._color("⏭️ SKIP", "dim")
        }
        
        status_text = status_symbols.get(status, status.upper())
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] {status_text} {test_name} ({duration:.3f}s)")
        
        if status == "failed" and error:
            print(f"       {self._color('Error:', 'red')} {error}")
    
    def on_run_complete(self, summary: TestRunSummary):
        """Called when test run completes."""
        duration = summary.duration
        success_rate = summary.success_rate()
        
        # Calculate duration
        elapsed = datetime.now() - self._start_time if self._start_time else timedelta(seconds=duration)
        
        lines = [
            "",
            "=" * 70,
            self._color("📊 Test Run Complete", "bold"),
            "",
            f"  Total:     {summary.total}",
            f"  {self._color('Passed:', 'green')}   {summary.passed} ✅",
            f"  {self._color('Failed:', 'red')}   {summary.failed} ❌",
            f"  {self._color('Skipped:', 'dim')}   {summary.skipped} ⏭️",
            f"  {self._color('Timeout:', 'yellow')}  {summary.timeout} ⏱️",
            "",
            f"  Duration:  {duration:.2f}s",
            f"  Success:   {self._color(f'{success_rate:.1f}%', 'green' if success_rate >= 80 else 'yellow')}",
            "=" * 70,
        ]
        
        if summary.failed > 0:
            lines.extend([
                "",
                self._color("❌ Failed Tests:", "bold", "red"),
                ""
            ])
            
            for result in summary.results:
                if result.status == "failed":
                    lines.append(f"  • {result.name}")
                    lines.append(f"    {self._color(str(result.error), 'red')}")
        
        if summary.failed == 0 and summary.total > 0:
            lines.append("")
            lines.append(self._color("🎉 All tests passed!", "bold", "green"))
        
        print("\n".join(lines))
    
    def print_summary_table(self, summary: TestRunSummary):
        """Print summary table."""
        from tabulate import tabulate
        
        headers = ["Status", "Count", "Percentage"]
        rows = [
            ["✅ Passed", summary.passed, f"{(summary.passed/summary.total)*100:.1f}%" if summary.total > 0 else "0%"],
            ["❌ Failed", summary.failed, f"{(summary.failed/summary.total)*100:.1f}%" if summary.total > 0 else "0%"],
            ["⏭️ Skipped", summary.skipped, f"{(summary.skipped/summary.total)*100:.1f}%" if summary.total > 0 else "0%"],
            ["⏱️ Timeout", summary.timeout, f"{(summary.timeout/summary.total)*100:.1f}%" if summary.total > 0 else "0%"],
        ]
        
        table = tabulate(rows, headers=headers, tablefmt="grid")
        print(table)
    
    def print_durations(self, summary: TestRunSummary, top_n: int = 10):
        """Print slowest tests."""
        sorted_results = sorted(summary.results, key=lambda r: r.duration, reverse=True)[:top_n]
        
        lines = [
            "",
            self._color(f"⏱️ Top {top_n} Slowest Tests", "bold"),
            ""
        ]
        
        for i, result in enumerate(sorted_results, 1):
            status_symbol = "✅" if result.status == "passed" else "❌"
            lines.append(f"  {i}. {status_symbol} {result.name} - {result.duration:.3f}s")
        
        print("\n".join(lines))


class ProgressReporter:
    """Show progress bar during test run."""
    
    def __init__(self, total_tests: int):
        self.total = total_tests
        self.completed = 0
        self.passed = 0
        self.failed = 0
    
    def update(self, status: str):
        """Update progress."""
        self.completed += 1
        
        if status == "passed":
            self.passed += 1
        elif status == "failed":
            self.failed += 1
        
        self._print_progress()
    
    def _print_progress(self):
        """Print progress bar."""
        progress = self.completed / self.total
        bar_length = 50
        filled = int(bar_length * progress)
        
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r[{bar}] {self.completed}/{self.total} | ✅ {self.passed} | ❌ {self.failed}", end="", flush=True)
        
        if self.completed == self.total:
            print()  # New line when complete


def print_test_summary(summary: TestRunSummary):
    """Simple summary print."""
    reporter = ConsoleReporter()
    reporter.on_run_complete(summary)


def create_console_reporter(use_colors: bool = True) -> ConsoleReporter:
    """Factory function."""
    return ConsoleReporter(use_colors=use_colors)
