#!/bin/bash
# API额度检测和任务暂停示例
# 贾维斯 - API Quota Management

QUOTA_STATUS_FILE="/home/ubuntu/.openclaw/workspace/quota-status.json"

# 检测API错误是否为额度问题
function is_quota_error() {
    local error_output="$1"
    # 常见额度错误关键词
    local quota_keywords="quota|rate limit|insufficient|exceeded|limit"

    if echo "$error_output" | grep -iE "$quota_keywords" > /dev/null; then
        return 0  # 是额度问题
    else
        return 1  # 不是额度问题
    fi
}

# 保存暂停任务状态
function save_paused_task() {
    local task_id="$1"
    local task_name="$2"
    local progress="$3"
    local next_step="$4"

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local refresh_time=$(date -u -d "+5 hours" +"%Y-%m-%dT%H:%M:%SZ")

    # 更新JSON（简化版，实际应该用jq）
    cat > "$QUOTA_STATUS_FILE" << EOF
{
  "quota_status": {
    "last_check": "$timestamp",
    "last_pause": "$timestamp",
    "paused_tasks": ["$task_id"],
    "quota_refresh_cycle": "5 hours",
    "next_refresh_estimate": "$refresh_time"
  },
  "paused_tasks": [
    {
      "task_id": "$task_id",
      "task_name": "$task_name",
      "paused_at": "$timestamp",
      "progress": "$progress",
      "next_step": "$next_step",
      "reason": "quota_exceeded",
      "can_resume_after": "$refresh_time"
    }
  ]
}
EOF

    echo "✅ 任务已暂停: $task_name"
    echo "📊 已保存状态到: $QUOTA_STATUS_FILE"
    echo "⏰ 预计恢复时间: $refresh_time"
}

# 检查是否可以恢复暂停的任务
function check_paused_tasks() {
    if [ ! -f "$QUOTA_STATUS_FILE" ]; then
        return 1  # 没有暂停的任务
    fi

    local now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local pause_time=$(grep -o '"paused_at": "[^"]*"' "$QUOTA_STATUS_FILE" | cut -d'"' -f4)
    local can_resume_after=$(grep -o '"can_resume_after": "[^"]*"' "$QUOTA_STATUS_FILE" | cut -d'"' -f4)

    if [ -z "$can_resume_after" ]; then
        return 1  # 没有暂停的任务
    fi

    # 转换为时间戳比较
    local now_timestamp=$(date -d "$now" +%s)
    local resume_timestamp=$(date -d "$can_resume_after" +%s)

    if [ $now_timestamp -ge $resume_timestamp ]; then
        return 0  # 可以恢复
    else
        return 1  # 还需要等待
    fi
}

# 示例：带额度检测的任务执行
function execute_task_with_quota_check() {
    local task_name="$1"
    local task_command="$2"

    echo "🚀 执行任务: $task_name"

    # 尝试执行命令
    if output=$(eval "$task_command" 2>&1); then
        echo "✅ 任务完成: $task_name"
        echo "$output"
        return 0
    else
        local exit_code=$?
        echo "❌ 任务错误 (退出码: $exit_code)"

        # 检查是否是额度问题
        if is_quota_error "$output"; then
            echo "⚠️  检测到API额度耗尽"
            save_paused_task \
                "$(date +%s)" \
                "$task_name" \
                "执行失败" \
                "重新执行: $task_command"

            # 通知主人
            echo "🔔 主人，API额度用完了，任务已暂停。"
            echo "   任务: $task_name"
            echo "   预计5小时后自动恢复。"

            return 2  # 特殊退出码：额度耗尽
        else
            echo "⚠️  其他错误，非额度问题"
            echo "$output"
            return $exit_code
        fi
    fi
}

# 恢复暂停的任务
function resume_paused_tasks() {
    if ! check_paused_tasks; then
        echo "ℹ️  没有需要恢复的任务"
        return 0
    fi

    echo "🔄 发现暂停的任务，准备恢复..."

    # 读取任务信息
    local task_name=$(grep -o '"task_name": "[^"]*"' "$QUOTA_STATUS_FILE" | cut -d'"' -f4 | head -1)
    local next_step=$(grep -o '"next_step": "[^"]*"' "$QUOTA_STATUS_FILE" | cut -d'"' -f4 | head -1)

    echo "📋 恢复任务: $task_name"
    echo "📝 执行: $next_step"

    # 清除暂停状态
    cat > "$QUOTA_STATUS_FILE" << EOF
{
  "quota_status": {
    "last_check": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "last_pause": null,
    "paused_tasks": [],
    "quota_refresh_cycle": "5 hours",
    "next_refresh_estimate": "unknown"
  },
  "paused_tasks": []
}
EOF

    # 执行恢复的任务
    if eval "$next_step"; then
        echo "✅ 任务已恢复并完成: $task_name"
        echo "🔔 主人，暂停的任务已成功恢复并完成。"
        return 0
    else
        echo "❌ 任务恢复失败: $task_name"
        return 1
    fi
}

# 导出函数供其他脚本使用
export -f is_quota_error
export -f save_paused_task
export -f check_paused_tasks
export -f execute_task_with_quota_check
export -f resume_paused_tasks
