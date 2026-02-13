#!/bin/bash
# 等待到15:22然后发布Post 15-20

CURRENT_TIME=$(date +%s)
TARGET_TIME=$(date -d "15:22" +%s)
WAIT_SECONDS=$((TARGET_TIME - CURRENT_TIME))

echo "当前时间: $(date '+%H:%M:%S')"
echo "目标时间: 15:22:00"
echo "等待时间: $WAIT_SECONDS 秒"
echo ""

if [ $WAIT_SECONDS -gt 0 ]; then
    echo "⏰ 等待中..."
    sleep $WAIT_SECONDS
fi

echo ""
echo "✅ 到达15:22，开始发布！"
echo ""

python3 /home/ubuntu/.openclaw/workspace/quick_publish.py
