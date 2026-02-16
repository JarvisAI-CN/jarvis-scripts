#!/bin/bash
# ========================================
# health_checks.sh
# 健康检查函数库
# ========================================

# WebDAV 检查 - 挂载状态
webdav_check_mount() {
    local mount_point="/home/ubuntu/123pan"
    
    if mount | grep -q "${mount_point}"; then
        echo "mounted"
        return 0
    else
        echo "not_mounted"
        return 1
    fi
}

# WebDAV 检查 - 读写测试
webdav_check_rw() {
    local mount_point="/home/ubuntu/123pan"
    local test_file="${mount_point}/.rw_test_$$"
    
    # 写入测试
    if ! echo "test" > "${test_file}" 2>/dev/null; then
        echo "write_failed"
        return 1
    fi
    
    # 读取测试
    if ! grep -q "test" "${test_file}" 2>/dev/null; then
        rm -f "${test_file}"
        echo "read_failed"
        return 1
    fi
    
    # 清理
    rm -f "${test_file}"
    echo "ok"
    return 0
}

# VNC 检查 - 端口监听
vnc_check_port() {
    local port=${1:-5901}
    
    if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
        echo "listening"
        return 0
    else
        echo "not_listening"
        return 1
    fi
}

# VNC 检查 - 进程状态
vnc_check_process() {
    if pgrep -f "Xtightvnc|Xvnc" > /dev/null 2>&1; then
        echo "running"
        return 0
    else
        echo "not_running"
        return 1
    fi
}

# 宝塔面板检查 - 端口监听
bt_check_port() {
    local port=${1:-8888}
    
    if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
        echo "listening"
        return 0
    else
        echo "not_listening"
        return 1
    fi
}

# 宝塔面板检查 - HTTP响应
bt_check_http() {
    local port=${1:-8888}
    local url="http://localhost:${port}"
    
    if ! command -v curl >/dev/null 2>&1; then
        echo "curl_not_available"
        return 2
    fi
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" "${url}" 2>/dev/null)
    
    if echo "${status}" | grep -qE "200|301|302"; then
        echo "ok:${status}"
        return 0
    else
        echo "error:${status}"
        return 1
    fi
}

# 宝塔面板检查 - 进程状态
bt_check_process() {
    if pgrep -f "BT-Panel" > /dev/null 2>&1; then
        echo "running"
        return 0
    else
        echo "not_running"
        return 1
    fi
}

# Gateway 检查
gateway_check_status() {
    if ! command -v openclaw >/dev/null 2>&1; then
        echo "command_not_found"
        return 2
    fi
    
    if openclaw gateway status >/dev/null 2>&1; then
        echo "running"
        return 0
    else
        echo "not_running"
        return 1
    fi
}

# 磁盘空间检查
disk_check_usage() {
    local path=${1:-/}
    local usage=$(df -h "${path}" | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "${usage}"
    
    # 返回使用率是否超过85%
    if [ "${usage}" -gt 85 ]; then
        return 1
    else
        return 0
    fi
}
