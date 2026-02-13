#!/bin/bash
# 贾维斯的备份脚本 - 直接API上传版本（不依赖WebDAV挂载）
# 优化版：按年份/月份/日期组织备份文件

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="workspace-backup-${BACKUP_DATE}.tar.gz"
LOCAL_BACKUP="/tmp/${BACKUP_NAME}"
LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/backup_123pan.log"
SOURCE_DIR="/home/ubuntu/.openclaw/workspace"
WEBDAV_URL="https://webdav.123pan.cn/webdav"
WEBDAV_USER="13220103449"
WEBDAV_PASS="ls8h74pb"

# 获取当前日期信息
YEAR=$(date +%Y)
MONTH=$(date +%m)
DAY=$(date +%d)

# 构建云端目录路径：备份/2026/02月/05/
REMOTE_DIR="${WEBDAV_URL}/备份/${YEAR}/${MONTH}月/${DAY}/"
REMOTE_PATH="${REMOTE_DIR}${BACKUP_NAME}"

echo "===== 开始备份: $(date) =====" >> "$LOG_FILE"
echo "备份方案: 直接API上传（不依赖WebDAV挂载）" >> "$LOG_FILE"
echo "目标目录: 备份/${YEAR}/${MONTH}月/${DAY}/" >> "$LOG_FILE"

# 创建本地备份tar包
echo "创建本地备份: $LOCAL_BACKUP" >> "$LOG_FILE"
tar czf "$LOCAL_BACKUP" -C "$SOURCE_DIR" . 2>&1 | head -20 >> "$LOG_FILE"

if [ ! -f "$LOCAL_BACKUP" ]; then
    echo "错误: 本地备份创建失败" >> "$LOG_FILE"
    exit 1
fi

# 显示备份大小
BACKUP_SIZE=$(du -h "$LOCAL_BACKUP" | cut -f1)
echo "本地备份大小: $BACKUP_SIZE" >> "$LOG_FILE"

# 创建云端目录结构（如果不存在）
echo "创建云端目录结构..." >> "$LOG_FILE"

# 使用MKCOL方法创建WebDAV目录
# 1. 创建年份目录
curl -X MKCOL \
  -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
  -s \
  "${WEBDAV_URL}/备份/${YEAR}" >> "$LOG_FILE" 2>&1

# 2. 创建月份目录
curl -X MKCOL \
  -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
  -s \
  "${WEBDAV_URL}/备份/${YEAR}/${MONTH}月" >> "$LOG_FILE" 2>&1

# 3. 创建日期目录
curl -X MKCOL \
  -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
  -s \
  "${WEBDAV_URL}/备份/${YEAR}/${MONTH}月/${DAY}" >> "$LOG_FILE" 2>&1

echo "目录结构创建完成" >> "$LOG_FILE"

# 上传到123盘（使用curl PUT）
echo "上传到123盘..." >> "$LOG_FILE"
HTTP_CODE=$(curl -X PUT \
  -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
  -T "$LOCAL_BACKUP" \
  -w "%{http_code}" \
  -o /dev/null \
  -s \
  "$REMOTE_PATH" 2>&1)

# 检查HTTP响应码
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "204" ]; then
    echo "✅ 上传成功 (HTTP $HTTP_CODE)" >> "$LOG_FILE"
    echo "文件路径: 备份/${YEAR}/${MONTH}月/${DAY}/${BACKUP_NAME}" >> "$LOG_FILE"

    # 清理本地临时备份文件（保留最近3个本地文件，云端保留所有历史）
    ls -t /tmp/workspace-backup-*.tar.gz 2>/dev/null | tail -n +4 | xargs -r rm -f
    echo "已清理本地临时文件，保留最新3个" >> "$LOG_FILE"
    echo "云端保留所有历史备份（空间充足）" >> "$LOG_FILE"

    # 列出当天云端备份
    echo "当天云端备份:" >> "$LOG_FILE"
    curl -s -u "${WEBDAV_USER}:${WEBDAV_PASS}" \
      "${REMOTE_DIR}" | grep -o "href=\"[^\"]*workspace-backup" | sed 's/href="//;s/"//' >> "$LOG_FILE" 2>&1

    echo "备份完成: $(date)" >> "$LOG_FILE"
    echo "备份文件: ${BACKUP_NAME} (${BACKUP_SIZE})" >> "$LOG_FILE"

    # 清理本次本地临时文件
    rm -f "$LOCAL_BACKUP"

    exit 0
else
    echo "❌ 上传失败 (HTTP $HTTP_CODE)" >> "$LOG_FILE"
    echo "错误: 备份上传失败，本地文件保留在: $LOCAL_BACKUP" >> "$LOG_FILE"
    exit 1
fi
