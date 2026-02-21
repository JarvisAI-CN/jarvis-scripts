#!/bin/bash
# GitHub状态检查脚本
# 检查PR状态、Issues、Releases等

set -euo pipefail

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/github_status.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "GitHub状态检查开始"
log "=========================================="

# 检查gh命令是否可用
if ! command -v gh &> /dev/null; then
    log "❌ gh命令未安装"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    log "❌ 未登录GitHub，请运行: gh auth login"
    exit 1
fi

# 1. 检查主要仓库的PR状态
log ""
log "【检查1】最新PR状态..."

# 检查jarvis-scripts仓库
MAIN_REPO="JarvisAI-CN/jarvis-scripts"

# 获取最新的PR
LATEST_PR=$(gh pr list --repo "$MAIN_REPO" --limit 1 --json number,title,state,headRefName --jq '.[0]' 2>/dev/null || echo "{}")

if [ "$LATEST_PR" != "{}" ]; then
    PR_NUMBER=$(echo "$LATEST_PR" | jq -r '.number')
    PR_TITLE=$(echo "$LATEST_PR" | jq -r '.title')
    PR_STATE=$(echo "$LATEST_PR" | jq -r '.state')
    PR_BRANCH=$(echo "$LATEST_PR" | jq -r '.headRefName')

    log "  最新PR: #$PR_NUMBER - $PR_TITLE"
    log "  状态: $PR_STATE | 分支: $PR_BRANCH"

    # 如果PR是开放的，检查CI状态
    if [ "$PR_STATE" = "OPEN" ]; then
        log "  → 检查CI状态..."
        CI_STATUS=$(gh pr view "$PR_NUMBER" --repo "$MAIN_REPO" --json statusCheckRollup --jq '.statusCheckRollup | length' 2>/dev/null || echo "0")
        log "  ✓ CI检查项: $CI_STATUS 个"
    fi
else
    log "  没有找到PR"
fi

# 2. 检查开放的Issues
log ""
log "【检查2】开放的Issues..."

ISSUE_COUNT=$(gh issue list --repo "$MAIN_REPO" --state open --limit 100 --json number --jq 'length' 2>/dev/null || echo "0")
log "  开放Issues: $ISSUE_COUNT 个"

if [ "$ISSUE_COUNT" -gt 0 ]; then
    log "  最新5个Issues:"
    gh issue list --repo "$MAIN_REPO" --state open --limit 5 --json number,title --jq '.[] | "#\(.number): \(.title)"' | while read -r line; do
        log "    - $line"
    done
fi

# 3. 检查最新Release
log ""
log "【检查3】最新Release..."

LATEST_RELEASE=$(gh release view --repo "$MAIN_REPO" --json tagName,name,createdAt --jq '.' 2>/dev/null || echo "{}")

if [ "$LATEST_RELEASE" != "{}" ]; then
    RELEASE_TAG=$(echo "$LATEST_RELEASE" | jq -r '.tagName')
    RELEASE_NAME=$(echo "$LATEST_RELEASE" | jq -r '.name')
    RELEASE_DATE=$(echo "$LATEST_RELEASE" | jq -r '.createdAt' | cut -d'T' -f1)

    log "  最新Release: $RELEASE_TAG - $RELEASE_NAME"
    log "  发布日期: $RELEASE_DATE"
else
    log "  没有找到Release"
fi

# 4. 检查保质期系统仓库
log ""
log "【检查4】保质期系统仓库..."

EXPIRY_REPO="JarvisAI-CN/expiry-management-system-clean"

EXPIRY_RELEASE=$(gh release view --repo "$EXPIRY_REPO" --json tagName,name,createdAt --jq '.' 2>/dev/null || echo "{}")

if [ "$EXPIRY_RELEASE" != "{}" ]; then
    EXPIRY_TAG=$(echo "$EXPIRY_RELEASE" | jq -r '.tagName')
    EXPIRY_NAME=$(echo "$EXPIRY_RELEASE" | jq -r '.name')
    EXPIRY_DATE=$(echo "$EXPIRY_RELEASE" | jq -r '.createdAt' | cut -d'T' -f1)

    log "  最新Release: $EXPIRY_TAG - $EXPIRY_NAME"
    log "  发布日期: $EXPIRY_DATE"
fi

log ""
log "=========================================="
log "GitHub状态检查完成"
log "=========================================="

exit 0
