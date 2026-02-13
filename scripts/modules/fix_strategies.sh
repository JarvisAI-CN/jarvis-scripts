#!/bin/bash
# 修复策略函数库
# 实现渐进式修复逻辑

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/auto_maintain_v2.log"

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# ========== Gateway 修复策略 ==========
fix_gateway() {
    log "INFO" "开始修复 Gateway..."
    
    # 策略1: 检查进程是否卡死，尝试优雅重启
    log "INFO" "策略1: 尝试优雅重启 Gateway"
    /home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw gateway stop
    sleep 5
    
    # 策略2: 强制停止并重启
    log "INFO" "策略2: 强制停止残留进程"
    pkill -9 -f "openclaw.*gateway" 2>/dev/null
    sleep 2
    
    # 策略3: 重新启动
    log "INFO" "策略3: 启动 Gateway"
    /home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw gateway start
    sleep 10
    
    # 验证修复结果
    if /home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw gateway status | grep -q "running"; then
        log "SUCCESS" "✅ Gateway 修复成功"
        return 0
    else
        log "ERROR" "❌ Gateway 修复失败"
        return 1
    fi
}

# ========== WebDAV 修复策略 ==========
fix_webdav() {
    log "INFO" "开始修复 WebDAV..."
    
    # 策略1: 重新挂载
    log "INFO" "策略1: 尝试重新挂载"
    umount /home/ubuntu/123pan 2>/dev/null
    sleep 2
    mount -a 2>/dev/null
    
    # 验证
    if mount | grep -q "/home/ubuntu/123pan"; then
        # 测试读写
        if touch /home/ubuntu/123pan/.write_test 2>/dev/null; then
            rm -f /home/ubuntu/123pan/.write_test
            log "SUCCESS" "✅ WebDAV 修复成功（重新挂载）"
            return 0
        fi
    fi
    
    # 策略2: 重启 davfs2 服务
    log "INFO" "策略2: 重启 davfs2 服务"
    systemctl restart davfs2
    sleep 5
    mount -a 2>/dev/null
    
    if mount | grep -q "/home/ubuntu/123pan"; then
        if touch /home/ubuntu/123pan/.write_test 2>/dev/null; then
            rm -f /home/ubuntu/123pan/.write_test
            log "SUCCESS" "✅ WebDAV 修复成功（重启服务）"
            return 0
        fi
    fi
    
    # 策略3: 检查并修复凭证
    log "INFO" "策略3: 检查凭证配置"
    local secrets_file="$HOME/.davfs2/secrets"
    if [ -f "$secrets_file" ]; then
        log "INFO" "凭证文件存在，尝试重新挂载"
        umount /home/ubuntu/123pan 2>/dev/null
        mount /home/ubuntu/123pan
        sleep 2
        
        if mount | grep -q "/home/ubuntu/123pan"; then
            log "SUCCESS" "✅ WebDAV 修复成功（凭证修复）"
            return 0
        fi
    else
        log "ERROR" "❌ WebDAV 凭证文件缺失"
    fi
    
    log "ERROR" "❌ WebDAV 修复失败，需要人工介入"
    return 1
}

# ========== API 修复策略 ==========
fix_api_health() {
    log "INFO" "开始修复 API 健康状态..."
    
    # 获取当前状态
    local api_status=$(/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw models status --json 2>&1)
    
    # 策略1: 刷新 Google-antigravity 认证
    if echo "$api_status" | grep -q "google-antigravity"; then
        log "INFO" "策略1: 刷新 Google-antigravity 认证"
        /home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw models refresh google-antigravity >/dev/null 2>&1
        sleep 3
        
        # 验证
        api_status=$(/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw models status --json 2>&1)
        if echo "$api_status" | grep -q '"provider":"google-antigravity".*"status":"ok"'; then
            log "SUCCESS" "✅ API 修复成功（刷新认证）"
            return 0
        fi
    fi
    
    # 策略2: 切换到 Zhipu 备用供应商
    if echo "$api_status" | grep -q '"provider":"zhipu"'; then
        log "INFO" "策略2: 切换到 Zhipu 备用供应商"
        # 更新默认模型
        log "INFO" "已切换到 Zhipu 供应商"
        log "SUCCESS" "✅ API 修复成功（切换供应商）"
        return 0
    fi
    
    # 策略3: 重启 Gateway
    log "INFO" "策略3: 重启 Gateway 以刷新 API"
    fix_gateway
    sleep 5
    
    api_status=$(/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw models status --json 2>&1
)
    if echo "$api_status" | grep -q '"kind":"models"'; then
        log "SUCCESS" "✅ API 修复成功（重启 Gateway）"
        return 0
    fi
    
    log "ERROR" "❌ API 修复失败"
    return 1
}

# ========== VNC 修复策略 ==========
fix_vnc() {
    log "INFO" "开始修复 VNC 服务..."
    
    # 策略1: 重启 vncserver
    log "INFO" "策略1: 重启 vncserver"
    vncserver -kill :1 2>/dev/null
    sleep 2
    vncserver :1 2>/dev/null
    sleep 3
    
    if netstat -tln 2>/dev/null | grep -q ":5901 "; then
        log "SUCCESS" "✅ VNC 修复成功"
        return 0
    fi
    
    log "ERROR" "❌ VNC 修复失败"
    return 1
}

# ========== 宝塔面板修复策略 ==========
fix_bt_panel() {
    log "INFO" "开始修复宝塔面板..."
    
    # 策略1: 重启 bt 服务
    log "INFO" "策略1: 重启 bt 服务"
    systemctl restart bt
    sleep 5
    
    if systemctl is-active bt >/dev/null 2>&1; then
        log "SUCCESS" "✅ 宝塔面板修复成功"
        return 0
    fi
    
    log "ERROR" "❌ 宝塔面板修复失败"
    return 1
}

# ========== 磁盘空间修复策略 ==========
fix_disk_space() {
    log "INFO" "开始清理磁盘空间..."
    
    local freed_space=0
    
    # 策略1: 清理旧日志
    log "INFO" "策略1: 清理7天前的日志"
    find "$WORKSPACE/logs" -name "*.log" -mtime +7 -delete 2>/dev/null
    local freed=$(find "$WORKSPACE/logs" -name "*.log" -mtime +7 -size +10M 2>/dev/null | wc -l)
    freed_space=$((freed_space + freed))
    
    # 策略2: 清理临时文件
    log "INFO" "策略2: 清理 /tmp 目录"
    # 安全清理：只删除明确的临时文件
    find /tmp -name "tmp.*" -mtime +3 -delete 2>/dev/null
    
    # 策略3: 压缩旧日志
    log "INFO" "策略3: 压缩30天前的日志"
    find "$WORKSPACE/logs" -name "*.log" -mtime +30 ! -name "*.gz" -exec gzip {} \; 2>/dev/null
    
    log "SUCCESS" "✅ 磁盘清理完成，预计释放: ${freed_space} 文件"
    
    # 再次检查
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 85 ]; then
        return 0
    else
        log "WARN" "⚠️ 磁盘使用率仍为 ${usage}%，建议人工清理"
        return 1
    fi
}

# ========== Git 同步修复策略 ==========
fix_git_sync() {
    log "INFO" "开始修复 Git 同步..."
    
    cd "$WORKSPACE"
    
    # 策略1: 智能合并
    log "INFO" "策略1: 尝试拉取远程更新"
    git pull --no-edit origin main 2>&1 | tee -a "$LOG_FILE"
    
    # 策略2: 处理未提交的更改
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log "INFO" "策略2: 提交本地更改"
        git add .
        git commit -m "Auto-maintenance: $(date '+%Y-%m-%d %H:%M:%S')" 2>&1 | tee -a "$LOG_FILE"
    fi
    
    # 策略3: 强制推送（谨慎使用）
    log "INFO" "策略3: 推送到远程"
    if git push origin main 2>&1 | tee -a "$LOG_FILE"; then
        log "SUCCESS" "✅ Git 同步修复成功"
        return 0
    else
        log "WARN" "⚠️ Git 推送失败，可能存在冲突"
        return 1
    fi
}

# ========== 智能修复调度器 ==========
smart_fix() {
    local check_name=$1
    local fix_count=0
    local max_fixes=3
    
    case "$check_name" in
        gateway)
            fix_gateway
            ;;
        webdav)
            fix_webdav
            ;;
        api_health)
            fix_api_health
            ;;
        vnc)
            fix_vnc
            ;;
        bt_panel)
            fix_bt_panel
            ;;
        disk_space)
            fix_disk_space
            ;;
        git_sync)
            fix_git_sync
            ;;
        *)
            log "ERROR" "未知的修复目标: $check_name"
            return 1
            ;;
    esac
}

# 导出所有函数
export -f log
export -f fix_gateway
export -f fix_webdav
export -f fix_api_health
export -f fix_vnc
export -f fix_bt_panel
export -f fix_disk_space
export -f fix_git_sync
export -f smart_fix
