#!/bin/bash
# 邮件转发监控脚本 - 有输出时自动发送飞书通知

OUTPUT=$(python3 /home/ubuntu/.openclaw/workspace/scripts/email_poll.py --limit 25 2>&1)

if [ -n "$OUTPUT" ]; then
    # 有输出，说明有新的转发邮件，返回输出内容
    echo "$OUTPUT"
else
    # 无输出，说明没有新邮件
    echo "NO_REPLY"
fi
