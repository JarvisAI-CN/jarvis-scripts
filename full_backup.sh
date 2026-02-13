#!/bin/bash
# 贾维斯的全量级备份脚本 (v1.0)
# 作用：备份整个 .openclaw 目录（排除 node_modules）以及所有工作区内容

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="full-system-backup-${BACKUP_DATE}.tar.gz"
LOCAL_BACKUP="/tmp/${BACKUP_NAME}"
LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/full_backup.log"
WEBDAV_URL="https://webdav.123pan.cn/webdav"
WEBDAV_USER="13220103449"
WEBDAV_PASS="ls8h74pb"

YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)
REMOTE_DIR="${WEBDAV_URL}/备份/全量/${YEAR}/${MONTH}月/${DAY}/"
REMOTE_PATH="${REMOTE_DIR}${BACKUP_NAME}"

echo "===== 启动全量级备份: $(date) =====" >> "$LOG_FILE"
echo "范围: /home/ubuntu/.openclaw (排除 node_modules)" >> "$LOG_FILE"

# 创建本地全量包
# 排除 node_modules 和 临时文件
tar czf "$LOCAL_BACKUP" \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='*.gz' \
    -C /home/ubuntu .openclaw 2>&1 | head -n 20 >> "$LOG_FILE"

if [ ! -f "$LOCAL_BACKUP" ]; then
    echo "❌ 失败: 本地全量备份创建失败" >> "$LOG_FILE"
    exit 1
fi

BACKUP_SIZE=$(du -h "$LOCAL_BACKUP" | cut -f1)
echo "📦 全量备份大小: $BACKUP_SIZE" >> "$LOG_FILE"

# 创建云端目录
curl -X MKCOL -u "${WEBDAV_USER}:${WEBDAV_PASS}" -s "${WEBDAV_URL}/备份/全量" >> "$LOG_FILE" 2>&1
curl -X MKCOL -u "${WEBDAV_USER}:${WEBDAV_PASS}" -s "${WEBDAV_URL}/备份/全量/${YEAR}" >> "$LOG_FILE" 2>&1
curl -X MKCOL -u "${WEBDAV_USER}:${WEBDAV_PASS}" -s "${WEBDAV_URL}/备份/全量/${YEAR}/${MONTH}月" >> "$LOG_FILE" 2>&1
curl -X MKCOL -u "${WEBDAV_USER}:${WEBDAV_PASS}" -s "${WEBDAV_URL}/备份/全量/${YEAR}/${MONTH}月/${DAY}" >> "$LOG_FILE" 2>&1

# 上传
echo "🚀 正在向 123 盘全量传输..." >> "$LOG_FILE"
HTTP_CODE=$(curl -X PUT \
  -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
  -T "$LOCAL_BACKUP" \
  -w "%{http_code}" \
  -o /dev/null \
  -s \
  "$REMOTE_PATH")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "✅ 全量上传成功 (HTTP $HTTP_CODE)" >> "$LOG_FILE"
    echo "💾 文件: 备份/全量/${YEAR}/${MONTH}月/${DAY}/${BACKUP_NAME}" >> "$LOG_FILE"
    rm -f "$LOCAL_BACKUP"
    exit 0
else
    echo "❌ 上传失败 (HTTP $HTTP_CODE)" >> "$LOG_FILE"
    exit 1
fi
