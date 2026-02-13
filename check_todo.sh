#!/bin/bash
# 待办文件自动检查脚本

TODO_FILE="/home/ubuntu/.openclaw/workspace/TODO.md"
LOG_FILE="/tmp/todo-check.log"

echo "===== 待办文件检查: $(date) =====" >> $LOG_FILE

# 检查待办文件是否存在
if [ ! -f "$TODO_FILE" ]; then
    echo "❌ 待办文件不存在: $TODO_FILE" >> $LOG_FILE
    exit 1
fi

# 统计各象限任务数
URGENT=$(grep -c "🔴 第一象限" "$TODO_FILE" || echo 0)
URGENT_NOT_IMPORTANT=$(grep -c "🟠 第二象限" "$TODO_FILE" || echo 0)
IMPORTANT_NOT_URGENT=$(grep -c "🟡 第三象限" "$TODO_FILE" || echo 0)
NOT_URGENT=$(grep -c "🟢 第四象限" "$TODO_FILE" || echo 0)

echo "📊 当前任务分布:" >> $LOG_FILE
echo "  🔴 重要且紧急: $URGENT 项" >> $LOG_FILE
echo "  🟠 紧急但不重要: $URGENT_NOT_IMPORTANT 项" >> $LOG_FILE
echo "  🟡 重要但不紧急: $IMPORTANT_NOT_URGENT 项" >> $LOG_FILE
echo "  🟢 不重要且不紧急: $NOT_URGENT 项" >> $LOG_FILE

# 检查是否有紧急未处理任务
if grep -q "## 🔴 第一象限：重要且紧急" "$TODO_FILE"; then
    echo "⚠️  提醒: 有重要且紧急的任务需要处理" >> $LOG_FILE

    # 提取第一象限的任务标题
    echo "任务列表:" >> $LOG_FILE
    awk '/## 🔴 第一象限：重要且紧急/,/## 🟠 第二象限/' "$TODO_FILE" | \
        grep "^####" | \
        sed 's/^#### /  - /' >> $LOG_FILE
fi

echo "检查完成" >> $LOG_FILE
echo "" >> $LOG_FILE

# 如果有紧急任务，发送系统事件（如果OpenClaw支持）
if [ $URGENT -gt 0 ]; then
    # 这里可以添加发送通知的逻辑
    echo "发现 $URGENT 项紧急任务，请及时处理" >> $LOG_FILE
fi
