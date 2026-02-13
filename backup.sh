#!/bin/bash
# 贾维斯的备份脚本 - Rclone 优化版 v2.1
# 策略：云端永久保留所有历史，本地保留最近 3 份压缩包

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="workspace-backup-${BACKUP_DATE}.tar.gz"
LOCAL_BACKUP="/tmp/${BACKUP_NAME}"
LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/backup_123pan.log"
SOURCE_DIR="/home/ubuntu/.openclaw/workspace"
REMOTE_TARGET="123pan:备份/$(date +%Y)/$(date +%m)月/$(date +%d)/"

echo "===== 开始备份: $(date) =====" >> "$LOG_FILE"

# 1. 创建本地压缩包 (排除大目录)
echo "创建本地压缩包 (排除 ruanjian, logs, temp)..." >> "$LOG_FILE"
tar --exclude='ruanjian' \
    --exclude='logs/*.log' \
    --exclude='temp' \
    -czf "$LOCAL_BACKUP" -C "$SOURCE_DIR" . 2>&1 | head -n 20 >> "$LOG_FILE"

if [ ! -f "$LOCAL_BACKUP" ]; then
    echo "错误: 本地备份创建失败" >> "$LOG_FILE"
    exit 1
fi

BACKUP_SIZE=$(du -h "$LOCAL_BACKUP" | cut -f1)
echo "本地备份完成: $BACKUP_SIZE" >> "$LOG_FILE"

# 2. 上传至 123 盘 (使用 rclone copy，不会删除云端旧文件)
echo "正在使用 rclone 上传至 123 盘..." >> "$LOG_FILE"
rclone copy "$LOCAL_BACKUP" "$REMOTE_TARGET" --verbose >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 备份上传成功" >> "$LOG_FILE"
    
    # 3. 维护本地留存策略：仅保留最近 3 份
    echo "维护本地留存：保留最近 3 份备份包..." >> "$LOG_FILE"
    ls -t /tmp/workspace-backup-*.tar.gz 2>/dev/null | tail -n +4 | xargs -r rm -f
    
    echo "目前本地留存列表：" >> "$LOG_FILE"
    ls -lh /tmp/workspace-backup-*.tar.gz >> "$LOG_FILE" 2>&1
    
    echo "备份任务结束: $(date)" >> "$LOG_FILE"
    exit 0
else
    echo "❌ 备份上传失败 (rclone 错误码: $?)" >> "$LOG_FILE"
    exit 1
fi
