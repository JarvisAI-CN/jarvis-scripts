#!/bin/bash
# 贾维斯自动化维护脚本
# 执行健康检查、TODO更新、代码同步

WORKSPACE="/home/ubuntu/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/auto_maintain.log"

echo "--- $(date) 开始自动化维护 ---" >> "$LOG_FILE"

# 1. API 健康检查
/usr/bin/python3 "$WORKSPACE/scripts/api_health_monitor_v2.py" >> "$LOG_FILE" 2>&1

# 2. TODO 更新
/usr/bin/python3 "$WORKSPACE/update_todo.py" >> "$LOG_FILE" 2>&1

# 3. 自动同步到 GitHub
cd "$WORKSPACE"
git add . >> "$LOG_FILE" 2>&1
if git commit -m "Auto-maintenance: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1; then
    TOKEN=$(python3 "$WORKSPACE/scripts/get_github_token.py")
    if [ -n "$TOKEN" ]; then
        git push -f "https://$TOKEN@github.com/JarvisAI-CN/jarvis-scripts.git" main >> "$LOG_FILE" 2>&1
        echo "✅ GitHub 同步成功 (Security Enhanced)" >> "$LOG_FILE"
    else
        git push origin main >> "$LOG_FILE" 2>&1
        echo "✅ GitHub 同步成功" >> "$LOG_FILE"
    fi
else
    echo "ℹ️ 无代码变更需要提交" >> "$LOG_FILE"
fi

echo "--- 维护完成 ---" >> "$LOG_FILE"
