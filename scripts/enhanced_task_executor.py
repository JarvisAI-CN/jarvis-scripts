#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的任务执行器 - Enhanced Task Executor
实现自主编程项目的三大增强功能

核心功能:
1. 修复任务循环问题 - 改进任务类型检测逻辑
2. 增强监控任务 - Gateway/WebDAV/阈值检查 + 飞书告警
3. 增强知识管理 - PARA索引 + Obsidian双链 + 知识图谱
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 导入项目模块
scripts_dir = Path(__file__).parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

try:
    from modules.feishu_notifier import FeishuNotifier
    import todo_to_tasklist
except ImportError as e:
    print(f"警告: 模块导入失败 - {e}")
    FeishuNotifier = None
    todo_to_tasklist = None

# 配置
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
LOG_DIR = WORKSPACE / "logs"
HEALTH_CHECK_SCRIPT = scripts_dir / "modules" / "health_checks.sh"


class EnhancedTaskExecutor:
    """增强的任务执行器"""
    
    def __init__(self, logger=None):
        self.workspace = WORKSPACE
        self.logger = logger
        
        # 初始化飞书通知器
        if FeishuNotifier:
            try:
                self.feishu = FeishuNotifier()
            except Exception as e:
                self.logger.warning(f"飞书通知器初始化失败: {e}")
                self.feishu = None
        else:
            self.feishu = None
    
    def log(self, level: str, module: str, message: str):
        """日志记录"""
        if self.logger:
            if level == "INFO":
                self.logger.info(module, message)
            elif level == "SUCCESS":
                self.logger.success(module, message)
            elif level == "ERROR":
                self.logger.error(module, message)
            elif level == "WARNING":
                self.logger.warning(module, message)
        else:
            print(f"[{level}] [{module}] {message}")
    
    def check_gateway_status(self) -> Tuple[bool, str]:
        """检查Gateway状态"""
        try:
            result = subprocess.run(
                ["openclaw", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                
                # 检查Gateway是否running
                gateway = status_data.get("gateway", {})
                if "running" not in gateway.get("state", ""):
                    return False, "Gateway未运行"
                
                return True, f"Gateway运行正常 - {gateway.get('state', '')}"
            else:
                return False, f"命令执行失败: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Gateway状态检查超时"
        except Exception as e:
            return False, f"Gateway状态检查异常: {str(e)}"
    
    def check_webdav_response_time(self) -> Tuple[bool, float, str]:
        """检查WebDAV响应时间"""
        try:
            start = datetime.now()
            
            # 测试123盘挂载点
            test_file = self.workspace / "123pan" / ".test_write.tmp"
            
            # 写入测试
            with open(test_file, "w") as f:
                f.write("test")
            
            # 读取测试
            with open(test_file, "r") as f:
                f.read()
            
            # 删除测试文件
            test_file.unlink()
            
            elapsed = (datetime.now() - start).total_seconds()
            
            if elapsed > 5.0:
                return False, elapsed, f"WebDAV响应过慢: {elapsed:.2f}秒"
            else:
                return True, elapsed, f"WebDAV响应正常: {elapsed:.2f}秒"
                
        except Exception as e:
            elapsed = (datetime.now() - start).total_seconds()
            return False, elapsed, f"WebDAV检查失败: {str(e)}"
    
    def check_alert_thresholds(self, metrics: Dict) -> List[Dict]:
        """检查告警阈值"""
        alerts = []
        
        # Gateway状态告警
        if not metrics.get("gateway_ok", False):
            alerts.append({
                "type": "critical",
                "source": "gateway",
                "message": metrics.get("gateway_status", "Gateway异常")
            })
        
        # WebDAV响应时间告警
        webdav_time = metrics.get("webdav_response_time", 0)
        if webdav_time > 5.0:
            alerts.append({
                "type": "warning",
                "source": "webdav",
                "message": f"WebDAV响应时间过长: {webdav_time:.2f}秒"
            })
        
        # 磁盘空间告警
        disk_usage = metrics.get("disk_usage_percent", 0)
        if disk_usage > 80:
            alerts.append({
                "type": "warning",
                "source": "disk",
                "message": f"磁盘使用率过高: {disk_usage}%"
            })
        
        return alerts
    
    def send_feishu_alert(self, alerts: List[Dict]) -> bool:
        """发送飞书告警通知"""
        if not self.feishu:
            self.log("WARNING", "ENHANCED_EXECUTOR", "飞书通知器不可用")
            return False
        
        if not alerts:
            return True
        
        # 构建告警消息
        critical_alerts = [a for a in alerts if a["type"] == "critical"]
        warning_alerts = [a for a in alerts if a["type"] == "warning"]
        
        message_parts = ["🚨 **系统监控告警**\n"]
        
        if critical_alerts:
            message_parts.append("### 🔴 严重告警\n")
            for alert in critical_alerts:
                message_parts.append(f"- **{alert['source']}**: {alert['message']}\n")
        
        if warning_alerts:
            message_parts.append("### ⚠️ 警告\n")
            for alert in warning_alerts:
                message_parts.append(f"- **{alert['source']}**: {alert['message']}\n")
        
        message = "".join(message_parts)
        
        try:
            result = self.feishu.send_message(message)
            if result:
                self.log("SUCCESS", "ENHANCED_EXECUTOR", "飞书告警已发送")
                return True
            else:
                self.log("ERROR", "ENHANCED_EXECUTOR", "飞书告警发送失败")
                return False
        except Exception as e:
            self.log("ERROR", "ENHANCED_EXECUTOR", f"飞书告警异常: {str(e)}")
            return False
    
    def execute_enhanced_monitoring(self, task: Dict) -> bool:
        """执行增强的监控任务"""
        task_id = task.get("id")
        self.log("INFO", "ENHANCED_EXECUTOR", f"开始增强监控任务: {task_id}")
        
        try:
            # 1. 检查Gateway状态
            gateway_ok, gateway_status = self.check_gateway_status()
            self.log("INFO", "ENHANCED_EXECUTOR", f"Gateway检查: {gateway_status}")
            
            # 2. 检查WebDAV响应时间
            webdav_ok, webdav_time, webdav_status = self.check_webdav_response_time()
            self.log("INFO", "ENHANCED_EXECUTOR", f"WebDAV检查: {webdav_status}")
            
            # 3. 检查磁盘空间
            df_result = subprocess.run(
                ["df", "/home/ubuntu/123pan"],
                capture_output=True,
                text=True
            )
            disk_usage_line = df_result.stdout.split('\n')[1].split()
            disk_usage_percent = int(disk_usage_line[4].rstrip('%'))
            
            # 4. 汇总指标
            metrics = {
                "gateway_ok": gateway_ok,
                "gateway_status": gateway_status,
                "webdav_ok": webdav_ok,
                "webdav_response_time": webdav_time,
                "disk_usage_percent": disk_usage_percent,
                "timestamp": datetime.now().isoformat()
            }
            
            # 5. 检查告警阈值
            alerts = self.check_alert_thresholds(metrics)
            
            # 6. 发送飞书告警（如有）
            if alerts:
                self.send_feishu_alert(alerts)
            
            # 7. 保存监控日志
            monitor_log = LOG_DIR / "enhanced_monitoring.jsonl"
            with open(monitor_log, "a") as f:
                f.write(json.dumps(metrics) + "\n")
            
            self.log("SUCCESS", "ENHANCED_EXECUTOR", f"增强监控任务完成: {task_id}")
            return True
            
        except Exception as e:
            self.log("ERROR", "ENHANCED_EXECUTOR", f"增强监控任务失败: {str(e)}")
            return False
    
    def scan_para_resources(self) -> List[Dict]:
        """扫描PARA/Resources目录"""
        resources_dir = self.workspace / "PARA" / "Resources"
        if not resources_dir.exists():
            self.log("WARNING", "ENHANCED_EXECUTOR", "PARA/Resources目录不存在")
            return []
        
        resources = []
        for item in resources_dir.iterdir():
            if item.is_file() and item.suffix in ['.md', '.txt']:
                resources.append({
                    "path": str(item),
                    "name": item.name,
                    "size": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
        
        return resources
    
    def detect_obsidian_broken_links(self, file_path: Path) -> List[str]:
        """检测Obsidian断裂的双链"""
        broken_links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找所有[[wikilinks]]
            import re
            pattern = r'\[\[([^\]]+)\]\]'
            links = re.findall(pattern, content)
            
            # 检查每个链接的文件是否存在
            for link in links:
                # 支持相对路径和绝对路径
                potential_paths = [
                    self.workspace / f"{link}.md",
                    self.workspace / "PARA" / "Resources" / f"{link}.md",
                    self.workspace / "Zettelkasten" / f"{link}.md",
                ]
                
                exists = any(p.exists() for p in potential_paths)
                if not exists:
                    broken_links.append(link)
        
        except Exception as e:
            self.log("WARNING", "ENHANCED_EXECUTOR", f"检测双链失败: {str(e)}")
        
        return broken_links
    
    def build_knowledge_graph_index(self) -> Dict:
        """构建知识图谱索引"""
        index = {
            "nodes": [],
            "edges": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # 扫描所有Markdown文件
        for md_file in self.workspace.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取双链
                import re
                links = re.findall(r'\[\[([^\]]+)\]\]', content)
                
                # 添加节点
                node_id = str(md_file.relative_to(self.workspace))
                index["nodes"].append({
                    "id": node_id,
                    "name": md_file.stem,
                    "path": str(md_file),
                    "link_count": len(links)
                })
                
                # 添加边
                for link in links:
                    index["edges"].append({
                        "from": node_id,
                        "to": link,
                        "type": "wikilink"
                    })
            
            except Exception as e:
                continue  # 跳过无法读取的文件
        
        return index
    
    def execute_enhanced_knowledge(self, task: Dict) -> bool:
        """执行增强的知识管理任务"""
        task_id = task.get("id")
        self.log("INFO", "ENHANCED_EXECUTOR", f"开始增强知识管理任务: {task_id}")
        
        try:
            results = {
                "task_id": task_id,
                "started_at": datetime.now().isoformat()
            }
            
            # 1. PARA系统索引
            resources = self.scan_para_resources()
            results["para_resources_count"] = len(resources)
            self.log("INFO", "ENHANCED_EXECUTOR", f"扫描到 {len(resources)} 个资源文件")
            
            # 2. Obsidian双链优化检测
            broken_links_count = 0
            checked_files = 0
            
            for md_file in self.workspace.rglob("*.md"):
                if checked_files >= 50:  # 限制检查数量
                    break
                
                broken = self.detect_obsidian_broken_links(md_file)
                if broken:
                    broken_links_count += len(broken)
                
                checked_files += 1
            
            results["obsidian_checked_files"] = checked_files
            results["obsidian_broken_links"] = broken_links_count
            self.log("INFO", "ENHANCED_EXECUTOR", f"检查了 {checked_files} 个文件，发现 {broken_links_count} 个断裂链接")
            
            # 3. 知识图谱更新
            knowledge_graph = self.build_knowledge_graph_index()
            graph_file = LOG_DIR / "knowledge_graph.json"
            with open(graph_file, 'w') as f:
                json.dump(knowledge_graph, f, indent=2, ensure_ascii=False)
            
            results["knowledge_graph_nodes"] = len(knowledge_graph["nodes"])
            results["knowledge_graph_edges"] = len(knowledge_graph["edges"])
            self.log("INFO", "ENHANCED_EXECUTOR", f"知识图谱已更新: {len(knowledge_graph['nodes'])} 个节点，{len(knowledge_graph['edges'])} 条边")
            
            results["completed_at"] = datetime.now().isoformat()
            results["status"] = "completed"
            
            # 保存结果
            result_file = LOG_DIR / f"knowledge_task_{task_id}.json"
            with open(result_file, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.log("SUCCESS", "ENHANCED_EXECUTOR", f"增强知识管理任务完成: {task_id}")
            return True
            
        except Exception as e:
            self.log("ERROR", "ENHANCED_EXECUTOR", f"增强知识管理任务失败: {str(e)}")
            return False


def main():
    """测试增强任务执行器"""
    import logging as logging_module
    
    # 配置日志
    logging_module.basicConfig(level=logging_module.INFO)
    
    # 创建简单日志记录器
    class SimpleLogger:
        def info(self, module, message):
            logging_module.info(f"[{module}] {message}")
        def success(self, module, message):
            logging_module.info(f"[{module}] ✅ {message}")
        def warning(self, module, message):
            logging_module.warning(f"[{module}] ⚠️ {message}")
        def error(self, module, message):
            logging_module.error(f"[{module}] ❌ {message}")
    
    logger = SimpleLogger()
    executor = EnhancedTaskExecutor(logger=logger)
    
    print("测试增强任务执行器\n")
    
    # 测试1: 增强监控
    print("=" * 50)
    print("测试1: 增强监控任务")
    print("=" * 50)
    monitor_task = {
        "id": "TEST-001",
        "type": "monitoring",
        "title": "测试监控任务"
    }
    result1 = executor.execute_enhanced_monitoring(monitor_task)
    print(f"结果: {'成功' if result1 else '失败'}\n")
    
    # 测试2: 增强知识管理
    print("=" * 50)
    print("测试2: 增强知识管理任务")
    print("=" * 50)
    knowledge_task = {
        "id": "TEST-002",
        "type": "knowledge",
        "title": "测试知识管理任务"
    }
    result2 = executor.execute_enhanced_knowledge(knowledge_task)
    print(f"结果: {'成功' if result2 else '失败'}\n")
    
    print("测试完成！")


if __name__ == "__main__":
    main()
