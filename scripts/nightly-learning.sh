#!/bin/bash
# 凌晨自主学习启动脚本
# 由 crontab 在每天 01:00 触发（见 crontab -l），创建标记文件供心跳在 01:00-05:00 执行学习计划

set -euo pipefail

LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/nightly-learning.log"
NOW_HUMAN=$(date '+%Y-%m-%d %H:%M:%S')
NOW_EPOCH=$(date '+%s')
STATE_DIR="/tmp/nightly-learning"
STATUS_FILE="$STATE_DIR/status"
START_TIME_FILE="$STATE_DIR/start_time"
RUN_ID_FILE="$STATE_DIR/run_id"

echo "===== $NOW_HUMAN: 启动凌晨自主学习 =====" >> "$LOG_FILE"

mkdir -p "$STATE_DIR"

# 如果已经有一个 pending 标记且很新（6小时内），认为上一轮还没被心跳消化，避免反复覆盖
if [ -f "$STATUS_FILE" ] && [ "$(cat "$STATUS_FILE" 2>/dev/null || true)" = "pending" ] && [ -f "$START_TIME_FILE" ]; then
    START_EPOCH=$(date -d "$(cat "$START_TIME_FILE")" '+%s' 2>/dev/null || echo 0)
    AGE=$((NOW_EPOCH - START_EPOCH))
    if [ "$AGE" -ge 0 ] && [ "$AGE" -le $((6*3600)) ]; then
        echo "发现未消费的 pending 标记（${AGE}s），跳过重复创建" >> "$LOG_FILE"
        exit 0
    fi
fi

echo "触发自主学习模式（创建标记文件，等待心跳触发）..." >> "$LOG_FILE"

# 方法1: 使用curl触发webhook（如果配置了）
# curl -X POST http://127.0.0.1:18789/hooks/wake \
#   -H "Authorization: Bearer YOUR_HOOK_TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "凌晨自主学习开始", "mode": "now"}' >> "$LOG_FILE" 2>&1

# 方法2: 直接调用agent（通过消息）
# 这需要在Gateway中配置

# 方法3: 创建标记文件，让下次心跳在 01:00-05:00 时段触发
# 约定：status=pending 表示待执行；心跳完成后应写回 completed（由心跳逻辑负责）
RUN_ID="nl-$(date '+%Y%m%d-%H%M%S')"
echo "$NOW_HUMAN" > "$START_TIME_FILE"
echo "$RUN_ID" > "$RUN_ID_FILE"
echo "pending" > "$STATUS_FILE"

echo "自主学习标记已创建（run_id=$RUN_ID），等待心跳触发" >> "$LOG_FILE"
echo "===== 脚本完成 =====" >> "$LOG_FILE"
