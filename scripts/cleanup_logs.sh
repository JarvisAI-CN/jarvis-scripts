#!/bin/bash
# 日志清理脚本
# 功能: 检查、归档和清理项目日志文件
# 作者: Jarvis (贾维斯)
# 创建时间: 2026-02-07

set -e

# 配置
WORKSPACE="/home/ubuntu/.openclaw/workspace"
ARCHIVE_DIR="$WORKSPACE/logs/archives"
MAX_LOG_SIZE="10M"  # 超过10MB的日志将被归档
ARCHIVE_AFTER_DAYS=30  # 30天后的日志将被归档

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 查找所有日志文件
log_info "扫描项目日志文件..."
LOG_FILES=$(find "$WORKSPACE/PARA/Projects/" -name "*.log" -type f 2>/dev/null)

if [ -z "$LOG_FILES" ]; then
    log_info "未找到日志文件"
    exit 0
fi

# 统计信息
TOTAL_SIZE=0
FILE_COUNT=0
ARCHIVED_COUNT=0
LARGE_FILES=""

# 检查每个日志文件
while IFS= read -r log_file; do
    if [ ! -f "$log_file" ]; then
        continue
    fi

    FILE_COUNT=$((FILE_COUNT + 1))
    FILE_SIZE=$(stat -c%s "$log_file" 2>/dev/null || stat -f%z "$log_file" 2>/dev/null)
    TOTAL_SIZE=$((TOTAL_SIZE + FILE_SIZE))

    # 转换为人类可读格式
    SIZE_MB=$(echo "scale=2; $FILE_SIZE / 1024 / 1024" | bc)

    # 检查文件大小
    if [ "$FILE_SIZE" -gt 10485760 ]; then  # 10MB
        log_warn "发现大文件: $log_file (${SIZE_MB}MB)"
        LARGE_FILES="$LARGE_FILES\n$log_file"

        # 归档大文件
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        PROJECT_NAME=$(basename $(dirname $(dirname "$log_file")))
        ARCHIVE_NAME="${PROJECT_NAME}_$(basename "$log_file")_${TIMESTAMP}.tar.gz"

        log_info "归档: $log_file -> $ARCHIVE_DIR/$ARCHIVE_NAME"
        tar -czf "$ARCHIVE_DIR/$ARCHIVE_NAME" -C "$(dirname "$log_file")" "$(basename "$log_file")"

        # 清空原文件
        > "$log_file"
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
    fi

    # 检查文件年龄
    FILE_AGE_DAYS=$(( ($(date +%s) - $(stat -c%Y "$log_file" 2>/dev/null || stat -f%m "$log_file" 2>/dev/null)) / 86400 ))

    if [ "$FILE_AGE_DAYS" -gt "$ARCHIVE_AFTER_DAYS" ]; then
        log_info "旧日志文件 (${FILE_AGE_DAYS}天): $log_file"

        # 归档旧文件
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        PROJECT_NAME=$(basename $(dirname $(dirname "$log_file")))
        ARCHIVE_NAME="${PROJECT_NAME}_$(basename "$log_file")_${TIMESTAMP}.tar.gz"

        log_info "归档: $log_file -> $ARCHIVE_DIR/$ARCHIVE_NAME"
        tar -czf "$ARCHIVE_DIR/$ARCHIVE_NAME" -C "$(dirname "$log_file")" "$(basename "$log_file")"

        # 删除旧文件
        rm "$log_file"
        ARCHIVED_COUNT=$((ARCHIVED_COUNT + 1))
    fi

done <<< "$LOG_FILES"

# 输出统计
TOTAL_SIZE_MB=$(echo "scale=2; $TOTAL_SIZE / 1024 / 1024" | bc)

echo ""
log_info "========== 日志清理报告 =========="
log_info "扫描文件数: $FILE_COUNT"
log_info "总大小: ${TOTAL_SIZE_MB}MB"
log_info "归档文件数: $ARCHIVED_COUNT"

if [ -n "$LARGE_FILES" ]; then
    log_warn "发现大文件:"
    echo -e "$LARGE_FILES"
fi

# 清理旧归档（保留最近30天）
log_info "清理30天前的归档文件..."
find "$ARCHIVE_DIR" -name "*.tar.gz" -type f -mtime +30 -delete

# 显示归档目录大小
ARCHIVE_SIZE=$(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)
log_info "归档目录大小: $ARCHIVE_SIZE"

log_info "========== 清理完成 =========="
