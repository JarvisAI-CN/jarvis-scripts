#!/bin/bash
# 贾维斯的顺序备份脚本
# 规则：上传成功后等待 2 小时再进行下一次备份

WORKSPACE_DIR="/home/ubuntu/.openclaw/workspace"
BACKUP_SCRIPT="${WORKSPACE_DIR}/backup.sh"
LOG_FILE="${WORKSPACE_DIR}/logs/sequential_backup.log"
LOCK_FILE="/tmp/sequential_backup.lock"

# 单例检查
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if ps -p "$PID" > /dev/null; then
        # 已经在运行，退出
        exit 0
    fi
fi

# 记录当前 PID
echo $$ > "$LOCK_FILE"

echo "[$(date)] 顺序备份守护进程启动..." >> "$LOG_FILE"

while true; do
    echo "[$(date)] 开始执行备份任务..." >> "$LOG_FILE"
    
    # 执行备份脚本
    /bin/bash "$BACKUP_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] 备份上传成功！按照规则：等待 2 小时..." >> "$LOG_FILE"
        sleep 7200
    else
        echo "[$(date)] 备份任务失败，10 分钟后重试..." >> "$LOG_FILE"
        sleep 600
    fi
done
