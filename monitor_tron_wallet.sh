#!/bin/bash
# TRON钱包监控脚本
# 用途: 监控TRON钱包余额和交易
# 作者: Jarvis
# 创建时间: 2026-02-04

WALLET_ADDRESS="TTBd7MnnjWtqf5wgZdtYeVW7PHELVgbscu"
LOG_FILE="/home/ubuntu/.openclaw/workspace/tron_wallet_log.txt"
ALERT_THRESHOLD_TRX=100
ALERT_THRESHOLD_USDT=100

# TRONGrid API
API_BASE="https://api.trongrid.io"

# 创建日志文件
touch "$LOG_FILE"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 获取账户信息
get_account_info() {
    # 使用wallet/getaccount端点（更可靠）
    local response=$(curl -s "$API_BASE/wallet/getaccount" \
        -H "Content-Type: application/json" \
        -d "{\"address\": \"$WALLET_ADDRESS\", \"visible\": true}")
    echo "$response"
}

# 获取TRC20代币余额（USDT）
get_trc20_balance() {
    # USDT contract address on TRON
    local usdt_contract="TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

    local response=$(curl -s "$API_BASE/v1/accounts/$WALLET_ADDRESS/tokens?limit=200")

    # 提取USDT余额（需要从response中解析）
    echo "$response"
}

# 获取最近交易
get_recent_transactions() {
    local response=$(curl -s "$API_BASE/v1/accounts/$WALLET_ADDRESS/transactions/trc20?only_confirmed=true&limit=5")
    echo "$response"
}

# 主监控函数
monitor_wallet() {
    log_message "=== 开始监控钱包 $WALLET_ADDRESS ==="

    # 获取账户信息
    local account_info=$(get_account_info)

    # 检查是否有错误
    if echo "$account_info" | grep -q "error"; then
        log_message "❌ API错误: $account_info"
        return 1
    fi

    # 解析TRX余额
    # 空对象{}表示地址未激活，余额为0
    if [ "$account_info" = "{}" ]; then
        log_message "💰 TRX余额: 0 TRX (地址未激活或无余额)"
    else
        local balance=$(echo "$account_info" | grep -o '"balance":"[0-9]*"' | grep -o '[0-9]*' | head -1)

        if [ -n "$balance" ]; then
            # TRX单位转换：1 TRX = 1,000,000 SUN
            local balance_trx=$(echo "scale=6; $balance / 1000000" | bc)
            log_message "💰 TRX余额: $balance_trx TRX"

            # 检查是否超过提醒阈值
            local balance_int=$(echo "$balance_trx" | cut -d. -f1)
            if [ "$balance_int" -ge "$ALERT_THRESHOLD_TRX" ]; then
                log_message "🚨 余额提醒: TRX余额超过 ${ALERT_THRESHOLD_TRX} TRX！"
            fi
        else
            log_message "💰 TRX余额: 0 TRX"
        fi
    fi

    # 获取TRC20代币信息
    local tokens=$(curl -s "$API_BASE/v1/accounts/$WALLET_ADDRESS/tokens?limit=200")

    # 查找USDT-TRC20
    local usdt_balance=$(echo "$tokens" | grep -o '"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"[^}]*' | grep -o '"amount":"[0-9.]*"' | grep -o '[0-9.]*' | head -1)

    if [ -n "$usdt_balance" ]; then
        # USDT单位转换：通常需要除以1,000,000（6位小数）
        local usdt_value=$(echo "scale=2; $usdt_balance / 1000000" | bc 2>/dev/null || echo "$usdt_balance")
        log_message "💵 USDT-TRC20余额: ${usdt_value} USDT"

        # 检查是否超过提醒阈值
        local usdt_int=$(echo "$usdt_value" | cut -d. -f1)
        if [ "$usdt_int" -ge "$ALERT_THRESHOLD_USDT" ]; then
            log_message "🚨 余额提醒: USDT余额超过 ${ALERT_THRESHOLD_USDT} USDT！"
        fi
    else
        log_message "ℹ️ 未检测到USDT-TRC20余额"
    fi

    # 获取最近交易
    local transactions=$(get_recent_transactions)
    local tx_count=$(echo "$transactions" | grep -o '"transaction_id"' | wc -l)

    if [ "$tx_count" -gt 0 ]; then
        log_message "📊 最近有 $tx_count 笔TRC20交易"
    fi

    log_message "=== 监控完成 ==="
    echo ""
}

# 执行监控
monitor_wallet

# 显示最新日志
tail -10 "$LOG_FILE"
