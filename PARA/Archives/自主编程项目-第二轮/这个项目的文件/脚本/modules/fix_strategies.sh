#!/bin/bash
# ========================================
# fix_strategies.sh
# 渐进式修复策略函数库
# ========================================

# 日志函数 (需要在主脚本中定义)
# log_info, log_warning, log_error, log_success

# ========================================
# WebDAV 修复策略
# ========================================

# 修复 WebDAV 未挂载 (渐进式: remount → restart service → fix config)
fix_webdav_not_mounted() {
    local mount_point="/home/ubuntu/123pan"
    
    log_warning "尝试修复 WebDAV 未挂载问题..."
    
    # 策略 1: 尝试重新挂载
    log_info "[策略 1/3] 尝试 mount -a 重新挂载..."
    if mount -a 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 2
        if mount | grep -q "${mount_point}"; then
            log_success "WebDAV 重新挂载成功"
            return 0
        fi
    fi
    log_warning "mount -a 失败,尝试下一个策略"
    
    # 策略 2: 重启 davfs2 服务
    log_info "[策略 2/3] 尝试重启 davfs2 服务..."
    if systemctl restart davfs2 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 5
        if mount "${mount_point}" 2>/dev/null; then
            log_success "WebDAV 重启服务并挂载成功"
            return 0
        fi
    fi
    log_warning "重启 davfs2 失败,尝试下一个策略"
    
    # 策略 3: 检查并修复配置
    log_info "[策略 3/3] 检查 WebDAV 配置..."
    if [ -f /etc/fstab ]; then
        if grep -q "${mount_point}" /etc/fstab; then
            log_info "fstab 配置存在,尝试手动挂载..."
            if mount "${mount_point}" 2>&1 | tee -a "${LOG_FILE}"; then
                log_success "WebDAV 手动挂载成功"
                return 0
            fi
        else
            log_error "fstab 中未找到 WebDAV 配置,需要手动配置"
        fi
    fi
    
    log_error "所有 WebDAV 修复策略均失败"
    return 1
}

# 修复 WebDAV 只读 (渐进式: remount → check permissions → restart)
fix_webdav_readonly() {
    local mount_point="/home/ubuntu/123pan"
    
    log_warning "尝试修复 WebDAV 只读问题..."
    
    # 策略 1: 尝试重新挂载为读写模式
    log_info "[策略 1/3] 尝试重新挂载为读写模式..."
    if mount -o remount,rw "${mount_point}" 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 2
        local test_file="${mount_point}/.rw_test_$$"
        if echo "test" > "${test_file}" 2>/dev/null; then
            rm -f "${test_file}"
            log_success "WebDAV 重新挂载为读写模式成功"
            return 0
        fi
    fi
    log_warning "重新挂载失败,尝试下一个策略"
    
    # 策略 2: 卸载并重新挂载
    log_info "[策略 2/3] 尝试卸载并重新挂载..."
    if umount "${mount_point}" 2>/dev/null; then
        sleep 2
        if mount "${mount_point}" 2>&1 | tee -a "${LOG_FILE}"; then
            sleep 2
            local test_file="${mount_point}/.rw_test_$$"
            if echo "test" > "${test_file}" 2>/dev/null; then
                rm -f "${test_file}"
                log_success "WebDAV 重新挂载成功"
                return 0
            fi
        fi
    fi
    log_warning "卸载重挂失败,尝试下一个策略"
    
    # 策略 3: 重启 davfs2 服务
    log_info "[策略 3/3] 尝试重启 davfs2 服务..."
    if systemctl restart davfs2 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 5
        if mount -a 2>&1 | tee -a "${LOG_FILE}"; then
            local test_file="${mount_point}/.rw_test_$$"
            if echo "test" > "${test_file}" 2>/dev/null; then
                rm -f "${test_file}"
                log_success "WebDAV 重启服务后挂载成功"
                return 0
            fi
        fi
    fi
    
    log_error "所有 WebDAV 只读修复策略均失败"
    return 1
}

# ========================================
# VNC 修复策略
# ========================================

# 修复 VNC 端口未监听 (渐进式: restart → kill & restart → reconfigure)
fix_vnc_not_listening() {
    local port=5901
    local display=:1
    
    log_warning "尝试修复 VNC 端口未监听问题..."
    
    # 策略 1: 尝试重启 VNC 服务
    log_info "[策略 1/3] 尝试重启 vncserver..."
    if vncserver -kill "${display}" 2>/dev/null; then
        sleep 2
    fi
    
    if vncserver "${display}" 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 3
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            log_success "VNC 重启成功,端口 ${port} 已监听"
            return 0
        fi
    fi
    log_warning "VNC 重启失败,尝试下一个策略"
    
    # 策略 2: 强制结束进程并重启
    log_info "[策略 2/3] 尝试强制结束 VNC 进程并重启..."
    pkill -9 -f "Xtightvnc|Xvnc" 2>/dev/null || true
    sleep 2
    
    if vncserver "${display}" 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 3
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            log_success "VNC 强制重启成功"
            return 0
        fi
    fi
    log_warning "VNC 强制重启失败,尝试下一个策略"
    
    # 策略 3: 使用不同显示号重启
    log_info "[策略 3/3] 尝试使用显示号 :2 启动 VNC..."
    if vncserver :2 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 3
        if netstat -tuln 2>/dev/null | grep -q ":5902 "; then
            log_success "VNC 在显示号 :2 (端口 5902) 上启动成功"
            return 0
        fi
    fi
    
    log_error "所有 VNC 修复策略均失败"
    return 1
}

# 修复 VNC 进程未运行
fix_vnc_process_down() {
    log_warning "尝试修复 VNC 进程未运行问题..."
    
    # 调用相同的修复策略
    fix_vnc_not_listening
    return $?
}

# ========================================
# 宝塔面板修复策略
# ========================================

# 修复宝塔面板端口未监听 (渐进式: restart service → check config → reinstall)
fix_bt_panel_not_listening() {
    log_warning "尝试修复宝塔面板端口未监听问题..."
    
    # 策略 1: 尝试重启 bt 服务
    log_info "[策略 1/3] 尝试重启 bt 服务..."
    if command -v bt >/dev/null 2>&1; then
        if bt restart 2>&1 | tee -a "${LOG_FILE}"; then
            sleep 5
            if netstat -tuln 2>/dev/null | grep -q ":8888 "; then
                log_success "宝塔面板重启成功"
                return 0
            fi
        fi
    fi
    log_warning "bt restart 失败,尝试下一个策略"
    
    # 策略 2: 使用 systemctl 重启
    log_info "[策略 2/3] 尝试使用 systemctl 重启..."
    local bt_service=$(systemctl list-units | grep -o "bt[[:space:]]*\.service" | head -1)
    if [ -n "${bt_service}" ]; then
        if systemctl restart "${bt_service}" 2>&1 | tee -a "${LOG_FILE}"; then
            sleep 5
            if netstat -tuln 2>/dev/null | grep -q ":8888 "; then
                log_success "宝塔面板通过 systemctl 重启成功"
                return 0
            fi
        fi
    fi
    log_warning "systemctl 重启失败,尝试下一个策略"
    
    # 策略 3: 尝试启动面板进程
    log_info "[策略 3/3] 尝试直接启动面板进程..."
    local panel_path="/www/server/panel/class/panel.py"
    if [ -f "${panel_path}" ]; then
        if python "${panel_path}" >/dev/null 2>&1 & then
            sleep 5
            if netstat -tuln 2>/dev/null | grep -q ":8888 "; then
                log_success "宝塔面板进程启动成功"
                return 0
            fi
        fi
    else
        log_error "未找到宝塔面板路径"
    fi
    
    log_error "所有宝塔面板修复策略均失败"
    return 1
}

# 修复宝塔面板 HTTP 错误
fix_bt_panel_http_error() {
    log_warning "尝试修复宝塔面板 HTTP 响应异常..."
    
    # 使用相同的修复策略
    fix_bt_panel_not_listening
    return $?
}

# 修复宝塔面板进程未运行
fix_bt_panel_process_down() {
    log_warning "尝试修复宝塔面板进程未运行问题..."
    
    # 使用相同的修复策略
    fix_bt_panel_not_listening
    return $?
}

# ========================================
# Gateway 修复策略
# ========================================

# 修复 Gateway 未运行 (渐进式: start → restart → reinstall)
fix_gateway_not_running() {
    log_warning "尝试修复 Gateway 未运行问题..."
    
    # 策略 1: 尝试启动 Gateway
    log_info "[策略 1/3] 尝试启动 Gateway..."
    if openclaw gateway start 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 10
        if openclaw gateway status >/dev/null 2>&1; then
            log_success "Gateway 启动成功"
            return 0
        fi
    fi
    log_warning "Gateway 启动失败,尝试下一个策略"
    
    # 策略 2: 尝试重启 Gateway
    log_info "[策略 2/3] 尝试重启 Gateway..."
    if openclaw gateway restart 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 15
        if openclaw gateway status >/dev/null 2>&1; then
            log_success "Gateway 重启成功"
            return 0
        fi
    fi
    log_warning "Gateway 重启失败,尝试下一个策略"
    
    # 策略 3: 检查并修复
    log_info "[策略 3/3] 尝试停止并重新启动..."
    openclaw gateway stop 2>/dev/null || true
    sleep 5
    if openclaw gateway start 2>&1 | tee -a "${LOG_FILE}"; then
        sleep 15
        if openclaw gateway status >/dev/null 2>&1; then
            log_success "Gateway 重新启动成功"
            return 0
        fi
    fi
    
    log_error "所有 Gateway 修复策略均失败"
    return 1
}

# ========================================
# 磁盘空间修复策略
# ========================================

# 修复磁盘空间过高 (渐进式: clean logs → clean cache → alert)
fix_disk_space_high() {
    local threshold=85
    local path=${1:-/}
    local usage=$(df -h "${path}" | awk 'NR==2 {print $5}' | sed 's/%//')
    
    log_warning "尝试清理磁盘空间 (当前使用率: ${usage}%)..."
    
    # 策略 1: 清理旧日志
    log_info "[策略 1/3] 清理旧日志文件..."
    local log_dirs=(
        "/var/log"
        "${HOME}/.openclaw/workspace/logs"
        "${HOME}/.pm2/logs"
    )
    
    local cleaned=0
    for dir in "${log_dirs[@]}"; do
        if [ -d "${dir}" ]; then
            log_info "清理 ${dir} 中超过 7 天的日志..."
            find "${dir}" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
            cleaned=1
        fi
    done
    
    if [ ${cleaned} -eq 1 ]; then
        local new_usage=$(df -h "${path}" | awk 'NR==2 {print $5}' | sed 's/%//')
        log_success "日志清理完成,使用率: ${new_usage}%"
        
        if [ "${new_usage}" -lt "${threshold}" ]; then
            return 0
        fi
    fi
    log_warning "日志清理不足,尝试下一个策略"
    
    # 策略 2: 清理缓存
    log_info "[策略 2/3] 清理系统缓存..."
    if command -v apt-get >/dev/null 2>&1; then
        apt-get clean 2>&1 | tee -a "${LOG_FILE}" || true
        apt-get autoclean 2>&1 | tee -a "${LOG_FILE}" || true
    fi
    
    # 清理 npm 缓存
    if command -v npm >/dev/null 2>&1; then
        npm cache clean --force 2>&1 | tee -a "${LOG_FILE}" || true
    fi
    
    # 清理 pip 缓存
    if command -v pip >/dev/null 2>&1; then
        pip cache purge 2>&1 | tee -a "${LOG_FILE}" || true
    fi
    
    local new_usage=$(df -h "${path}" | awk 'NR==2 {print $5}' | sed 's/%//')
    log_success "缓存清理完成,使用率: ${new_usage}%"
    
    if [ "${new_usage}" -lt "${threshold}" ]; then
        return 0
    fi
    log_warning "缓存清理不足,尝试下一个策略"
    
    # 策略 3: 发送告警
    log_info "[策略 3/3] 磁盘空间仍然过高,发送告警..."
    log_alert "磁盘空间警告: 使用率 ${new_usage}% (阈值: ${threshold}%)"
    log_alert "建议手动清理或扩容磁盘"
    
    return 1
}
