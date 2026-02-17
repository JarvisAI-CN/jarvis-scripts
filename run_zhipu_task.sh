#!/bin/bash
# 智谱任务执行包装器

LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/zhipu_$(date +%Y%m%d_%H%M%S).log"
PYTHON_SCRIPT="/home/ubuntu/.openclaw/workspace/zhipu_scheduler.py"

echo "=== 智谱任务开始 $(date) ===" >> $LOG_FILE
/usr/bin/python3 $PYTHON_SCRIPT --run >> $LOG_FILE 2>&1
EXIT_CODE=$?
echo "=== 智谱任务完成 $(date) 退出码: $EXIT_CODE ===" >> $LOG_FILE

# 保留最近7天的日志
find /home/ubuntu/.openclaw/workspace/logs/zhipu_*.log -mtime +7 -delete 2>/dev/null
