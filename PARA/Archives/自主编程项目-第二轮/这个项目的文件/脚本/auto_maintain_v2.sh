#!/bin/bash
# ========================================
# auto_maintain_v2.sh
# 自主编程系统 v2.0 - 自动维护脚本
# 
# 功能:
# 1. WebDAV、VNC、宝塔面板健康检查
# 2. 渐进式修复逻辑
# 3. 完整日志记录
# ========================================

set -euo pipefail

# ========================================
# 配置
# ========================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/auto_maintain_$(date +%Y%m%d).log"
LOCK_FILE="/tmp/auto_maintain_v2.lock"
ALERT_LOG="${LOG_DIR}/alerts.log"

# 创建日志目录
mkdir -p "${LOG_DIR}"

# ========================================
# 日志函数
# ========================================
log() {
    local level=$1
    shift
    local message="[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] $*"
    echo "${message}" | tee -a "${LOG_FILE}"
}

log_info() {
    log "INFO" "$@"
}

log_success() {
    log "SUCCESS" "$@"
}

log_warning() {
    log "WARNING" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_alert() {
    log "ALERT" "$@"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $*" >> "${ALERT_LOG}"
}

# ========================================
# 加载模块
# ========================================
source "${SCRIPT_DIR}/modules/health_checks.sh"
source "${SCRIPT_DIR}/modules/fix_strategies.sh"

# ========================================
# 健康检查函数
# ========================================

# WebDAV 健康检查
check_webdav() {
    log_info "检查 WebDAV 挂载状态..."
    
    local mount_point="/home/ubuntu/123pan"
    local test_file="${mount_point}/.maintain_test_$(date +%s)"
    
    # 1. 检查是否挂载
    if ! mount | grep -q "${mount_point}"; then
        log_warning "WebDAV 未挂载"
        # 尝试修复
        fix_webdav_not_mounted
        return $?
    fi
    
    # 2. 检查读写权限
    if ! touch "${test_file}" 2>/dev/null; then
        log_warning "WebDAV 无法写入"
        # 尝试修复
        fix_webdav_readonly
        return $?
    fi
    
    # 清理测试文件
    rm -f "${test_file}"
    
    log_success "WebDAV 检查通过"
    return 0
}

# VNC 健康检查
check_vnc() {
    log_info "检查 VNC 服务..."
    
    local vnc_port=5901
    
    # 1. 检查端口是否监听
    if ! netstat -tuln 2>/dev/null | grep -q ":${vnc_port} "; then
        log_warning "VNC 端口 ${vnc_port} 未监听"
        # 尝试修复
        fix_vnc_not_listening
        return $?
    fi
    
    # 2. 检查进程是否存在
    if ! pgrep -f "Xtightvnc|Xvnc" > /dev/null; then
        log_warning "VNC 进程未运行"
        # 尝试修复
        fix_vnc_process_down
        return $?
    fi
    
    log_success "VNC 检查通过"
    return 0
}

# 宝塔面板健康检查
check_bt_panel() {
    log_info "检查宝塔面板..."
    
    local bt_port=8888
    local bt_url="http://localhost:${bt_port}"
    
    # 1. 检查端口是否监听
    if ! netstat -tuln 2>/dev/null | grep -q ":${bt_port} "; then
        log_warning "宝塔面板端口 ${bt_port} 未监听"
        # 尝试修复
        fix_bt_panel_not_listening
        return $?
    fi
    
    # 2. 尝试HTTP请求
    if command -v curl >/dev/null 2>&1; then
        if ! curl -s -o /dev/null -w "%{http_code}" "${bt_url}" | grep -q "200\|301\|302"; then
            log_warning "宝塔面板 HTTP 响应异常"
            # 尝试修复
            fix_bt_panel_http_error
            return $?
        fi
    fi
    
    # 3. 检查 bt 进程
    if ! pgrep -f "BT-Panel" > /dev/null; then
        log_warning "宝塔面板进程未运行"
        # 尝试修复
        fix_bt_panel_process_down
        return $?
    fi
    
    log_success "宝塔面板检查通过"
    return 0
}

# Gateway 健康检查
check_gateway() {
    log_info "检查 OpenClaw Gateway..."
    
    if ! command -v openclaw >/dev/null 2>&1; then
        log_error "openclaw 命令不可用"
        return 1
    fi
    
    if ! openclaw gateway status >/dev/null 2>&1; then
        log_warning "Gateway 未运行"
        # 尝试修复
        fix_gateway_not_running
        return $?
    fi
    
    log_success "Gateway 检查通过"
    return 0
}

# 磁盘空间检查
check_disk_space() {
    log_info "检查磁盘空间..."
    
    local threshold=85
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "${usage}" -gt "${threshold}" ]; then
        log_alert "磁盘使用率过高: ${usage}%"
        # 尝试修复
        fix_disk_space_high
        return $?
    fi
    
    log_success "磁盘空间检查通过 (使用率: ${usage}%)"
    return 0
}

# ========================================
# 主检查函数
# ========================================

run_all_checks() {
    log_info "=========================================="
    log_info "开始执行健康检查..."
    log_info "=========================================="
    
    local failed_checks=()
    
    # 执行所有检查
    check_webdav || failed_checks+=("WebDAV")
    check_vnc || failed_checks+=("VNC")
    check_bt_panel || failed_checks+=("宝塔面板")
    check_gateway || failed_checks+=("Gateway")
    check_disk_space || failed_checks+=("磁盘空间")
    
    # 总结报告
    log_info "=========================================="
    if [ ${#failed_checks[@]} -eq 0 ]; then
        log_success "所有检查通过! ✓"
    else
        log_warning "以下检查失败: ${failed_checks[*]}"
        log_alert "需要人工介入: ${failed_checks[*]}"
    fi
    log_info "=========================================="
    
    return ${#failed_checks[@]}
}

# ========================================
# 锁管理
# ========================================

acquire_lock() {
    if [ -f "${LOCK_FILE}" ]; then
        local pid=$(cat "${LOCK_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            log_warning "已有实例在运行 (PID: ${pid})"
            exit 1
        else
            log_info "清理过期锁文件"
            rm -f "${LOCK_FILE}"
        fi
    fi
    
    echo $$ > "${LOCK_FILE}"
    log_info "获取锁文件: ${LOCK_FILE}"
}

release_lock() {
    if [ -f "${LOCK_FILE}" ]; then
        rm -f "${LOCK_FILE}"
        log_info "释放锁文件"
    fi
}

# ========================================
# 清理函数
# ========================================

cleanup() {
    log_info "清理资源..."
    release_lock
}

# ========================================
# 主函数
# ========================================

main() {
    # 设置清理钩子
    trap cleanup EXIT INT TERM
    
    # 获取锁
    acquire_lock
    
    # 执行检查
    run_all_checks
    
    log_info "执行完成"
}

# ========================================
# 入口点
# ========================================

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
