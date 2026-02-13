#!/bin/bash
# 健康检查函数库
# 用于 auto_maintain_v2.sh

# 配置
WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_DIR="$WORKSPACE/logs"
STATE_DIR="$WORKSPACE/.maintenance_state"
ALERT_FILE="$WORKSPACE/.maintenance_alerts.json"

# 初始化状态目录
init_state() {
    mkdir -p "$STATE_DIR"
    mkdir -p "$LOG_DIR"
}

# ========== Gateway 健康检查 ==========
check_gateway() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local gateway_status=$(/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw gateway status 2>&1)
    
    if echo "$gateway_status" | grep -q "running"; then
        echo "✅ Gateway: 运行正常"
        return 0
    else
        echo "❌ Gateway: 未运行"
        return 1
    fi
}

# ========== WebDAV 健康检查 ==========
check_webdav() {
    local mount_point="/home/ubuntu/123pan"
    
    # 检查挂载状态
    if ! mount | grep -q "$mount_point"; then
        echo "❌ WebDAV: 未挂载"
        return 1
    fi
    
    # 检查读写权限
    local test_file="$mount_point/.write_test_$$"
    if touch "$test_file" 2>/dev/null; then
        rm -f "$test_file"
        echo "✅ WebDAV: 挂载正常，读写正常"
        return 0
    else
        echo "❌ WebDAV: 挂载但无写权限"
        return 1
    fi
}

# ========== API 健康检查 ==========
check_api_health() {
    local api_status=$(/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw models status --json 2>&1)
    
    if echo "$api_status" | grep -q '"kind":"models"'; then
        # 检查主要供应商
        if echo "$api_status" | grep -q '"provider":"google-antigravity"'; then
            echo "✅ API: Google-antigravity 可用"
            return 0
        elif echo "$api_status" | grep -q '"provider":"zhipu"'; then
            echo "⚠️ API: 仅 Zhipu 可用"
            return 0
        fi
    fi
    
    echo "❌ API: 无可用供应商"
    return 1
}

# ========== VNC 服务检查 ==========
check_vnc() {
    if netstat -tln 2>/dev/null | grep -q ":5901 "; then
        echo "✅ VNC: 端口5901监听中"
        return 0
    else
        echo "⚠️ VNC: 端口5901未监听"
        return 1
    fi
}

# ========== 宝塔面板检查 ==========
check_bt_panel() {
    local bt_status=$(systemctl is-active bt 2>/dev/null)
    
    if [ "$bt_status" = "active" ]; then
        echo "✅ 宝塔面板: 服务运行中"
        return 0
    else
        echo "❌ 宝塔面板: 服务未运行"
        return 1
    fi
}

# ========== 磁盘空间检查 ==========
check_disk_space() {
    local usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 70 ]; then
        echo "✅ 磁盘: 使用率 ${usage}%"
        return 0
    elif [ "$usage" -lt 85 ]; then
        echo "⚠️ 磁盘: 使用率 ${usage}% (警告)"
        return 1
    else
        echo "❌ 磁盘: 使用率 ${usage}% (严重)"
        return 2
    fi
}

# ========== Git 同步状态检查 ==========
check_git_sync() {
    cd "$WORKSPACE"
    
    # 检查是否有未推送的提交
    if git status | grep -q "Your branch is ahead"; then
        echo "⚠️ Git: 有未推送的提交"
        return 1
    fi
    
    # 检查是否有未提交的更改
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo "⚠️ Git: 有未提交的更改"
        return 1
    fi
    
    echo "✅ Git: 工作区干净"
    return 0
}

# ========== GitHub 连接性检查 ==========
check_github_connectivity() {
    if ssh -T git@github.com -o ConnectTimeout=5 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ GitHub: SSH 连接正常"
        return 0
    elif curl -s --connect-timeout 5 https://github.com >/dev/null 2>&1; then
        echo "✅ GitHub: HTTPS 连接正常"
        return 0
    else
        echo "❌ GitHub: 连接失败"
        return 1
    fi
}

# ========== 综合健康检查 ==========
run_all_checks() {
    echo "=== 开始健康检查 ==="
    echo ""
    
    local results=()
    local failed=0
    local warnings=0
    
    # 执行所有检查
    check_gateway; results+=($?)
    check_webdav; results+=($?)
    check_api_health; results+=($?)
    check_vnc; results+=($?)
    check_bt_panel; results+=($?)
    check_disk_space; results+=($?)
    check_git_sync; results+=($?)
    check_github_connectivity; results+=($?)
    
    # 统计结果
    for code in "${results[@]}"; do
        if [ "$code" -eq 1 ]; then
            ((failed++))
        elif [ "$code" -eq 2 ]; then
            ((warnings++))
        fi
    done
    
    echo ""
    echo "=== 检查完成 ==="
    echo "失败: $failed | 警告: $warnings | 成功: $((${#results[@]} - failed - warnings))"
    
    return $failed
}

# 导出所有函数
export -f init_state
export -f check_gateway
export -f check_webdav
export -f check_api_health
export -f check_vnc
export -f check_bt_panel
export -f check_disk_space
export -f check_git_sync
export -f check_github_connectivity
export -f run_all_checks
