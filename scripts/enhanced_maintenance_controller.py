#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强维护控制器 - Enhanced Maintenance Controller
集成三大增强功能:
1. 任务循环问题修复
2. 增强监控任务
3. 增强知识管理
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict

# 添加脚本目录到路径
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# 导入基础控制器
try:
    from autonomous_controller import (
        AutonomousController,
        TaskManager,
        ProgressFlowLogger,
        GitOperator,
        E2EVerifier
    )
    from enhanced_task_executor import EnhancedTaskExecutor
except ImportError as e:
    print(f"错误: 模块导入失败 - {e}")
    sys.exit(1)


class EnhancedMaintenanceController(AutonomousController):
    """增强维护控制器 - 继承自主控制器"""
    
    def __init__(self):
        super().__init__()
        self.enhanced_executor = EnhancedTaskExecutor(logger=self.logger)
    
    def execute_enhanced_task(self, task: Dict) -> bool:
        """执行增强任务"""
        task_type = task.get("type", "").lower()
        title = task.get("title", "")
        description = task.get("description", "")
        
        # 判断任务类型并执行相应增强功能
        if any(kw in title.lower() or kw in description.lower() 
               for kw in ["监控", "monitor", "检查", "check", "健康", "health"]):
            self.logger.info("ENHANCED_CONTROLLER", "识别为增强监控任务")
            return self.enhanced_executor.execute_enhanced_monitoring(task)
        
        elif any(kw in title.lower() or kw in description.lower() 
                     for kw in ["知识", "knowledge", "para", "obsidian", "双链", "链接"]):
            self.logger.info("ENHANCED_CONTROLLER", "识别为增强知识管理任务")
            return self.enhanced_executor.execute_enhanced_knowledge(task)
        
        else:
            # 回退到基础任务执行
            self.logger.info("ENHANCED_CONTROLLER", "使用基础任务执行")
            return self.execute_task(task)
    
    def run_enhanced_task(self, task_id: str):
        """运行增强任务"""
        task = self.task_manager.get_task(task_id)
        if not task:
            self.logger.error("ENHANCED_CONTROLLER", f"任务不存在: {task_id}")
            return False
        
        self.logger.info("ENHANCED_CONTROLLER", f"开始执行增强任务: {task_id}")
        
        # 更新任务状态为进行中
        self.task_manager.update_task_status(
            task_id,
            TaskStatus.IN_PROGRESS
        )
        
        # 执行任务
        try:
            success = self.execute_enhanced_task(task)
            
            if success:
                # 更新为完成
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.DONE
                )
                self.logger.success("ENHANCED_CONTROLLER", f"增强任务完成: {task_id}")
                return True
            else:
                # 更新为失败
                self.task_manager.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error="增强任务执行失败"
                )
                return False
                
        except Exception as e:
            self.logger.error("ENHANCED_CONTROLLER", f"增强任务异常: {str(e)}")
            self.task_manager.update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e)
            )
            return False


def main():
    """主函数"""
    import logging
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    controller = EnhancedMaintenanceController()
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "run" and len(sys.argv) > 2:
            # 运行特定增强任务
            task_id = sys.argv[2]
            success = controller.run_enhanced_task(task_id)
            sys.exit(0 if success else 1)
        
        elif command == "test":
            # 测试增强功能
            print("测试增强维护控制器\n")
            
            # 测试1: 增强监控
            print("=" * 60)
            print("测试1: 增强监控任务")
            print("=" * 60)
            monitor_task = {
                "id": "TEST-MONITOR-001",
                "type": "monitoring",
                "title": "测试增强监控",
                "description": "测试增强监控功能"
            }
            result1 = controller.execute_enhanced_task(monitor_task)
            print(f"✅ 监控测试: {'成功' if result1 else '失败'}\n")
            
            # 测试2: 增强知识管理
            print("=" * 60)
            print("测试2: 增强知识管理任务")
            print("=" * 60)
            knowledge_task = {
                "id": "TEST-KNOWLEDGE-001",
                "type": "knowledge",
                "title": "测试增强知识管理",
                "description": "测试增强知识管理功能"
            }
            result2 = controller.execute_enhanced_task(knowledge_task)
            print(f"✅ 知识管理测试: {'成功' if result2 else '失败'}\n")
            
            print("所有测试完成！")
            sys.exit(0)
        
        else:
            # 回退到基础控制器
            print("回退到基础自主控制器")
            super().main()
    else:
        print("用法:")
        print("  python3 enhanced_maintenance_controller.py run <task_id>  # 运行增强任务")
        print("  python3 enhanced_maintenance_controller.py test             # 测试增强功能")
        print("  python3 enhanced_maintenance_controller.py                 # 运行基础控制器")
        sys.exit(1)


if __name__ == "__main__":
    main()
