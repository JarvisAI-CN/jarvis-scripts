#!/bin/bash
# 邮件转发监控脚本 - 用于cron定时任务

OUTPUT=$(python3 /home/ubuntu/.openclaw/workspace/scripts/email_poll.py --limit 25 2>/dev/null)

if [ -z "$OUTPUT" ]; then
    echo "NO_REPLY"
else
    echo "$OUTPUT"
fi
