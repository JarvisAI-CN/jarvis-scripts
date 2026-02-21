#!/bin/bash
# Agent健康检查脚本
# 检查所有Agent的状态和健康度

set -euo pipefail

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/agent_health.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Agent健康检查开始"
log "=========================================="

# 检查agents-manager技能
if [ ! -d "$WORKSPACE/skills/agents-manager" ]; then
    log "❌ agents-manager技能未安装"
    exit 1
fi

# 1. 扫描所有Agent
log ""
log "【检查1】扫描所有Agent..."

SCAN_OUTPUT=$(node "$WORKSPACE/skills/agents-manager/scripts/scan_agents.js" 2>&1)
log "$SCAN_OUTPUT"

# 统计Agent数量
AGENT_COUNT=$(echo "$SCAN_OUTPUT" | grep "Total:" | awk '{print $2}')
log "✓ 发现 $AGENT_COUNT 个Agent"

# 2. 健康检查
log ""
log "【检查2】Agent健康检查..."

if [ -f "$WORKSPACE/skills/agents-manager/scripts/health_check.js" ]; then
    HEALTH_OUTPUT=$(node "$WORKSPACE/skills/agents-manager/scripts/health_check.js" 2>&1)
    log "$HEALTH_OUTPUT"
else
    log "⚠️ health_check.js不存在"
fi

# 3. 检查我的3个Agent
log ""
log "【检查3】检查3-Agent工作流..."

MY_AGENTS=("the-architect" "tdd-developer" "regression-guard")
AGENT_DIR="/home/ubuntu/.openclaw/agents"

for agent in "${MY_AGENTS[@]}"; do
    if [ -d "$AGENT_DIR/$agent" ]; then
        if [ -f "$AGENT_DIR/$agent/agent/SYSTEM.md" ]; then
            log "  ✅ $agent - 系统提示词存在"
        else
            log "  ⚠️ $agent - 缺少SYSTEM.md"
        fi

        if [ -f "$AGENT_DIR/$agent/agent.json" ]; then
            log "  ✅ $agent - 配置文件存在"
        else
            log "  ⚠️ $agent - 缺少agent.json"
        fi
    else
        log "  ❌ $agent - 目录不存在"
    fi
done

# 4. 权限检查
log ""
log "【检查4】检查Agent权限..."

if [ -f "$WORKSPACE/skills/agents-manager/scripts/can_assign.js" ]; then
    # 检查main能否分配给the-architect
    PERMISSION_CHECK=$(node "$WORKSPACE/skills/agents-manager/scripts/can_assign.js" main the-architect 2>&1)
    log "  main → the-architect: $PERMISSION_CHECK"
fi

log ""
log "=========================================="
log "Agent健康检查完成"
log "=========================================="

exit 0
