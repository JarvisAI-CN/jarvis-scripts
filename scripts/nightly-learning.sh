#!/bin/bash
# 凌晨自主学习启动脚本
# 每天凌晨0点触发，执行5小时学习计划

LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/nightly-learning.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "===== $DATE: 启动凌晨自主学习 =====" >> "$LOG_FILE"

# 检查是否已经有一个学习任务在运行 (排除当前进程)
if [ "$(pgrep -f "nightly-learning.sh" | grep -v "$$" | wc -l)" -gt 0 ]; then
    echo "学习任务已在运行中，跳过" >> "$LOG_FILE"
    exit 0
fi

# 触发OpenClaw heartbeat来启动学习任务
# 通过发送系统事件
echo "触发自主学习模式..." >> "$LOG_FILE"

# 方法1: 使用curl触发webhook（如果配置了）
# curl -X POST http://127.0.0.1:18789/hooks/wake \
#   -H "Authorization: Bearer YOUR_HOOK_TOKEN" \
#   -H "Content-Type: application/json" \
#   -d '{"text": "凌晨自主学习开始", "mode": "now"}' >> "$LOG_FILE" 2>&1

# 方法2: 直接调用agent（通过消息）
# 这需要在Gateway中配置

# 方法3: 创建标记文件，让下次心跳时触发
mkdir -p /tmp/nightly-learning
echo "$DATE" > /tmp/nightly-learning/start_time
echo "pending" > /tmp/nightly-learning/status

echo "自主学习标记已创建，等待心跳触发" >> "$LOG_FILE"
echo "===== 脚本完成 =====" >> "$LOG_FILE"
