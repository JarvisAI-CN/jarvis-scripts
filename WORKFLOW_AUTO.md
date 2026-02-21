# 工作流程自动化文档

## 概述
本文档定义了 OpenClaw 系统中任务和工作流程的自动化执行方式。

## 工作流程类型

### 1. 每日任务
- 时间：每天 00:00 - 05:00
- 类型：知识整理、内容准备、学习提升、系统维护
- 执行文件：execute-nightly-learning.sh
- 触发条件：/tmp/nightly-learning/status 文件存在且内容为 "pending"

### 2. 每小时任务
- 时间：每小时 00:00
- 类型：代码扫描、文档优化、日志分析、知识整理
- 执行文件：zhipu_scheduler.py
- 触发条件：Cron 定时任务

### 3. 每两小时任务
- 时间：每两小时
- 类型：系统巡检、安全扫描、性能分析
- 执行文件：backup.sh、github_status_check.sh
- 触发条件：Cron 定时任务

### 4. 每日任务（09:00）
- 时间：每天 09:00
- 类型：Agent 健康检查、项目状态检查
- 执行文件：agent_health_check.sh
- 触发条件：Cron 定时任务

## 任务执行流程

### 任务创建
- 任务定义：在 execute-nightly-learning.sh 中定义
- 任务分配：根据时间和类型分配任务
- 任务执行：自动执行任务

### 任务监控
- 日志文件：/home/ubuntu/.openclaw/workspace/logs/
- 状态文件：/tmp/nightly-learning/status
- 错误处理：任务失败时记录到日志

### 任务完成
- 状态更新：任务完成后更新状态文件
- 报告生成：生成任务报告

## 工作流程优化

### 任务优先级
- 01:05 成本报告
- 01:10 技能发现
- 01:15 GitHub 状态检查
- 01:20 Agent 健康检查

### 任务执行策略
- 凌晨 01:00 - 05:00：低 API 消耗任务
- 白天：高价值产出任务
- 持续任务：不受时间限制任务

## 相关文件
- execute-nightly-learning.sh：任务执行脚本
- zhipu_scheduler.py：任务调度器
- github_status_check.sh：GitHub 状态检查
- agent_health_check.sh：Agent 健康检查
- backup.sh：备份脚本
- pre_commit_check.sh：Git 提交前检查
