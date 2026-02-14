"""
HTML report generator with charts and filtering.
"""

from typing import Optional
from datetime import datetime
from pathlib import Path

from ..core.case import TestResult
from ..core.runner import TestRunSummary


class HTMLReporter:
    """Generate HTML test reports."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, summary: TestRunSummary, filename: str = None) -> str:
        """Generate HTML report."""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        output_path = self.output_dir / filename
        html = self._render_html(summary)
        
        output_path.write_text(html, encoding='utf-8')
        
        return str(output_path)
    
    def _render_html(self, summary: TestRunSummary) -> str:
        """Render HTML content."""
        passed_count = summary.passed
        failed_count = summary.failed
        skipped_count = summary.skipped
        total_count = summary.total
        success_rate = summary.success_rate()
        
        # Calculate stats
        avg_duration = sum(r.duration for r in summary.results) / len(summary.results) if summary.results else 0
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.total .stat-value {{ color: #3498db; }}
        .stat-card.passed .stat-value {{ color: #27ae60; }}
        .stat-card.failed .stat-value {{ color: #e74c3c; }}
        .stat-card.skipped .stat-value {{ color: #f39c12; }}
        
        .progress-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .progress-bar {{
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            display: flex;
        }}
        
        .progress-segment {{
            height: 100%;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.8em;
        }}
        
        .segment-passed {{ background: #27ae60; }}
        .segment-failed {{ background: #e74c3c; }}
        .segment-skipped {{ background: #f39c12; }}
        
        .filters {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .filter-btn:hover {{ transform: translateY(-2px); }}
        .filter-btn.active {{ box-shadow: 0 4px 8px rgba(0,0,0,0.2); }}
        
        .filter-all {{ background: #3498db; color: white; }}
        .filter-passed {{ background: #27ae60; color: white; }}
        .filter-failed {{ background: #e74c3c; color: white; }}
        .filter-skipped {{ background: #f39c12; color: white; }}
        
        .test-list {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .test-item {{
            padding: 15px 20px;
            border-bottom: 1px solid #ecf0f1;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .test-item:hover {{
            background: #f8f9fa;
        }}
        
        .test-item.passed {{ border-left: 4px solid #27ae60; }}
        .test-item.failed {{ border-left: 4px solid #e74c3c; }}
        .test-item.skipped {{ border-left: 4px solid #f39c12; }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .test-name {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        
        .test-meta {{
            display: flex;
            gap: 15px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .test-details {{
            display: none;
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #ecf0f1;
        }}
        
        .test-item.expanded .test-details {{
            display: block;
        }}
        
        .status-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .status-badge.passed {{ background: #d4edda; color: #155724; }}
        .status-badge.failed {{ background: #f8d7da; color: #721c24; }}
        .status-badge.skipped {{ background: #fff3cd; color: #856404; }}
        
        .error-box {{
            background: #fff3cd;
            border-left: 4px solid #f39c12;
            padding: 15px;
            margin-top: 10px;
            border-radius: 5px;
        }}
        
        .error-title {{
            font-weight: 600;
            margin-bottom: 10px;
            color: #856404;
        }}
        
        .error-message {{
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        .hidden {{ display: none !important; }}
        
        footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Test Report</h1>
            <div class="subtitle">
                Generated: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} | 
                Duration: {summary.duration:.2f}s
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-value">{total_count}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card passed">
                <div class="stat-value">{passed_count}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-value">{failed_count}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card skipped">
                <div class="stat-value">{skipped_count}</div>
                <div class="stat-label">Skipped</div>
            </div>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-segment segment-passed" style="width: {(passed_count/total_count)*100:.1f}%" title="{passed_count} passed">
                    {passed_count if passed_count > 0 else ''}
                </div>
                <div class="progress-segment segment-failed" style="width: {(failed_count/total_count)*100:.1f}%" title="{failed_count} failed">
                    {failed_count if failed_count > 0 else ''}
                </div>
                <div class="progress-segment segment-skipped" style="width: {(skipped_count/total_count)*100:.1f}%" title="{skipped_count} skipped">
                    {skipped_count if skipped_count > 0 else ''}
                </div>
            </div>
        </div>
        
        <div class="filters">
            <button class="filter-btn filter-all active" onclick="filterTests('all')">All ({total_count})</button>
            <button class="filter-btn filter-passed" onclick="filterTests('passed')">✅ Passed ({passed_count})</button>
            <button class="filter-btn filter-failed" onclick="filterTests('failed')">❌ Failed ({failed_count})</button>
            <button class="filter-btn filter-skipped" onclick="filterTests('skipped')">⏭️ Skipped ({skipped_count})</button>
        </div>
        
        <div class="test-list">
"""
        
        # Add test items
        for result in summary.results:
            status_badge = f'<span class="status-badge {result.status}">{result.status}</span>'
            duration = f'{result.duration:.3f}s'
            retry_info = f' (retry {result.retry_count})' if result.retry_count > 0 else ''
            
            error_details = ""
            if result.status == "failed" and result.error:
                error_details = f"""
                <div class="error-box">
                    <div class="error-title">Error Details</div>
                    <div class="error-message">{result.error_trace or result.error}</div>
                </div>
                """
            
            html += f"""
            <div class="test-item {result.status}" data-status="{result.status}" onclick="toggleTest(this)">
                <div class="test-header">
                    <div class="test-name">{result.name}</div>
                    <div class="test-meta">
                        {status_badge}
                        <span>⏱️ {duration}{retry_info}</span>
                    </div>
                </div>
                <div class="test-details">
                    {error_details}
                    <div style="margin-top: 10px; color: #7f8c8d; font-size: 0.9em;">
                        <strong>Started:</strong> {result.start_time.strftime('%H:%M:%S') if result.start_time else 'N/A'} |
                        <strong>Duration:</strong> {result.duration:.3f}s |
                        <strong>Attempts:</strong> {len(result.attempts)}
                    </div>
                </div>
            </div>
            """
        
        html += """
        </div>
        
        <footer>
            Generated by E2E Test Framework | 
            <a href="https://github.com" target="_blank">GitHub</a>
        </footer>
    </div>
    
    <script>
        function filterTests(status) {
            // Update buttons
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`.filter-${status}`).classList.add('active');
            
            // Filter tests
            document.querySelectorAll('.test-item').forEach(item => {
                if (status === 'all' || item.dataset.status === status) {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });
        }
        
        function toggleTest(element) {
            element.classList.toggle('expanded');
        }
    </script>
</body>
</html>
"""
        
        return html


def generate_html_report(summary: TestRunSummary, output_dir: str = "reports") -> str:
    """Convenience function to generate HTML report."""
    reporter = HTMLReporter(output_dir)
    return reporter.generate(summary)
