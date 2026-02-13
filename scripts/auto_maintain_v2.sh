#!/bin/bash
# 自主维护脚本 v2.0
# 特性：多维健康检查、渐进式修复、事件驱动、智能告警

set -e

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/auto_maintain_v2.log"
STATE_FILE="$WORKSPACE/.maintenance_state.json"
ALERT_FILE="$WORKSPACE/.maintenance_alerts.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 加载模块
source "$SCRIPT_DIR/modules/health_checks.sh"
source "$SCRIPT_DIR/modules/fix_strategies.sh"

# 初始化
init_state

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# 保存状态
save_state() {
    local status=$1
    local checks=$2
    
    cat > "$STATE_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "status": "$status",
  "checks": $checks
}
EOF
}

# 发送告警
send_alert() {
    local level=$1
    local message=$2
    
    # 保存告警到文件（供心跳任务读取）
    cat > "$ALERT_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "level": "$level",
  "message": "$message"
}
EOF
    
    log "ALERT" "[$level] $message"
    
    # 如果是严重告警，发送飞书通知（如果配置了）
    if [ "$level" = "CRITICAL" ]; then
        # TODO: 集成飞书通知
        log "ALERT" "严重告警，建议立即人工介入"
    fi
}

# 渐进式修复流程
progressive_fix() {
    local check_name=$1
    local check_output=$2
    local max_attempts=3
    local attempt=1
    
    log "INFO" "开始修复: $check_name"
    
    while [ $attempt -le $max_attempts ]; do
        log "INFO" "修复尝试 $attempt/$max_attempts"
        
        # 调用修复策略
        if smart_fix "$check_name"; then
            # 验证修复结果
            log "INFO" "验证修复结果..."
            
            case "$check_name" in
                gateway)
                    check_gateway
                    ;;
                webdav)
                    check_webdav
                    ;;
                api_health)
                    check_api_health
                    ;;
                vnc)
                    check_vnc
                    ;;
                bt_panel)
                    check_bt_panel
                    ;;
                disk_space)
                    check_disk_space
                    ;;
                git_sync)
                    check_git_sync
                    ;;
            esac
            
            if [ $? -eq 0 ]; then
                log "SUCCESS" "✅ $check_name 修复成功"
                return 0
            fi
        fi
        
        ((attempt++))
        sleep 5
    done
    
    log "ERROR" "❌ $check_name 修复失败（已尝试 $max_attempts 次）"
    send_alert "WARNING" "$check_name 自动修复失败，需要人工介入"
    return 1
}

# 主维护流程
main_maintenance() {
    log "INFO" "========================================="
    log "INFO" "自主维护 v2.0 开始"
    log "INFO" "========================================="
    
    # 1. 执行健康检查
    log "INFO" "阶段1: 执行健康检查"
    
    local checks_result='{}'
    local failed_checks=()
    
    # Gateway
    if ! check_gateway > /dev/null 2>&1; then
        failed_checks+=("gateway")
        checks_result=$(echo "$checks_result" | jq '.gateway = "failed"')
    else
        checks_result=$(echo "$checks_result" | jq '.gateway = "ok"')
    fi
    
    # WebDAV
    if ! check_webdav > /dev/null 2>&1; then
        failed_checks+=("webdav")
        checks_result=$(echo "$checks_result" | jq '.webdav = "failed"')
    else
        checks_result=$(echo "$checks_result" | jq '.webdav = "ok"')
    fi
    
    # API
    if ! check_api_health > /dev/null 2>&1; then
        failed_checks+=("api_health")
        checks_result=$(echo "$checks_result" | jq '.api_health = "failed"')
    else
        checks_result=$(echo "$checks_result" | jq '.api_health = "ok"')
    fi
    
    # VNC
    if ! check_vnc > /dev/null 2>&1; then
        failed_checks+=("vnc")
        checks_result=$(echo "$checks_result" | jq '.vnc = "failed"')
    else
        checks_result=$(echo "$checks_result" | jq '.vnc = "ok"')
    fi
    
    # 宝塔面板
    if ! check_bt_panel > /dev/null 2>&1; then
        failed_checks+=("bt_panel")
        checks_result=$(echo "$checks_result" | jq '.bt_panel = "failed"')
    else
        checks_result=$(echo "$checks_result" | jq '.bt_panel = "ok"')
    fi
    
    # 磁盘空间
    local disk_code=0
    check_disk_space > /dev/null 2>&1 || disk_code=$?
    if [ $disk_code -eq 1 ]; then
        failed_checks+=("disk_space")
        checks_result=$(echo "$checks_result" | jq '.disk_space = "warning"')
    elif [ $disk_code -eq 2 ]; then
        failed_checks+=("disk_space")
        checks_result=$(echo "$checks_result" | jq '.disk_space = "critical"')
    else
        checks_result=$(echo "$checks_result" | jq '.disk_space = "ok"')
    fi
    
    # Git 同步
    if ! check_git_sync > /dev/null 2>&1; then
        failed_checks+=("git_sync")
        checks_result=$(echo "$checks_result" | jq '.git_sync = "needs_sync"')
    else
        checks_result=$(echo "$checks_result" | jq '.git_sync = "ok"')
    fi
    
    # 保存检查结果
    save_state "checked" "$checks_result"
    
    # 2. 自动修复
    if [ ${#failed_checks[@]} -gt 0 ]; then
        log "INFO" "阶段2: 发现 ${#failed_checks[@]} 个问题，开始自动修复"
        
        local still_failed=()
        
        for check in "${failed_checks[@]}"; do
            if progressive_fix "$check"; then
                log "SUCCESS" "✅ $check 修复成功"
            else
                still_failed+=("$check")
            fi
        done
        
        # 更新状态
        if [ ${#still_failed[@]} -gt 0 ]; then
            save_state "partial_fix" "$checks_result"
            send_alert "WARNING" "部分问题未能自动修复: ${still_failed[*]}"
        else
            save_state "fixed" "$checks_result"
            log "SUCCESS" "✅ 所有问题已自动修复"
        fi
    else
        log "INFO" "阶段2: 所有检查正常，无需修复"
        save_state "healthy" "$checks_result"
    fi
    
    # 3. TODO 更新
    log "INFO" "阶段3: 更新 TODO.md"
    if [ -f "$WORKSPACE/update_todo.py" ]; then
        /usr/bin/python3 "$WORKSPACE/update_todo.py" >> "$LOG_FILE" 2>&1
    fi
    
    # 4. Git 同步
    log "INFO" "阶段4: 同步到 GitHub"
    cd "$WORKSPACE"
    
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        git add .
        if git commit -m "Auto-maintenance v2.0: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1; then
            if git push origin main >> "$LOG_FILE" 2>&1; then
                log "SUCCESS" "✅ GitHub 同步成功"
            else
                log "ERROR" "❌ GitHub 推送失败"
                send_alert "INFO" "GitHub 同步失败，请检查网络或凭证"
            fi
        else
            log "INFO" "无代码变更需要提交"
        fi
    else
        log "INFO" "工作区干净，无需同步"
    fi
    
    # 5. 生成报告
    log "INFO" "========================================="
    log "INFO" "自主维护 v2.0 完成"
    log "INFO" "========================================="
    
    # 清理过期告警
    if [ -f "$ALERT_FILE" ]; then
        local alert_age=$(( $(date +%s) - $(stat -c %Y "$ALERT_FILE") ))
        if [ $alert_age -gt 3600 ]; then  # 1小时前的告警
            rm -f "$ALERT_FILE"
        fi
    fi
}

# 事件驱动模式（监听日志变化）
event_mode() {
    log "INFO" "启动事件驱动模式..."
    
    # 监控 Gateway 日志
    local gateway_log="/home/ubuntu/.openclaw/logs/gateway.log"
    
    if [ -f "$gateway_log" ]; then
        # 使用 inotifywait 监听日志变化
        inotifywait -m -e modify "$gateway_log" 2>/dev/null | while read path action file; do
            log "INFO" "检测到日志变化，执行快速检查"
            
            # 只检查关键服务
            if ! check_gateway > /dev/null 2>&1; then
                log "WARN" "Gateway 异常，触发修复"
                progressive_fix "gateway"
            fi
        done
    else
        log "WARN" "Gateway 日志文件不存在，事件驱动模式不可用"
    fi
}

# 主入口
main() {
    case "${1:-run}" in
        run)
            main_maintenance
            ;;
        event)
            event_mode
            ;;
        check)
            # 仅检查，不修复
            init_state
            run_all_checks
            ;;
        fix)
            # 强制修复指定项目
            if [ -n "$2" ]; then
                progressive_fix "$2"
            else
                echo "用法: $0 fix <check_name>"
                echo "可用的检查项: gateway, webdav, api_health, vnc, bt_panel, disk_space, git_sync"
                exit 1
            fi
            ;;
        *)
            echo "用法: $0 {run|event|check|fix [check_name]}"
            exit 1
            ;;
    esac
}

main "$@"
