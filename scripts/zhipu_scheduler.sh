#!/bin/bash
# 智谱持续工作启动脚本
# 让智谱（glm-4.7）24/7自动工作，最大化付费资源利用

WORKSPACE="/home/ubuntu/.openclaw/workspace"
SCHEDULER="$WORKSPACE/scripts/zhipu_continuous_scheduler.py"
LOG_DIR="$WORKSPACE/logs"
PID_FILE="$WORKSPACE/.zhipu_scheduler.pid"

# 创建日志目录
mkdir -p "$LOG_DIR"

case "$1" in
    start)
        echo "🚀 启动智谱持续任务调度器..."

        # 检查是否已运行
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "⚠️  调度器已在运行 (PID: $PID)"
                exit 1
            else
                echo "🧹 清理旧PID文件"
                rm -f "$PID_FILE"
            fi
        fi

        # 后台启动调度器
        nohup python3 "$SCHEDULER" run > "$LOG_DIR/zhipu_scheduler.log" 2>&1 &

        # 保存PID
        echo $! > "$PID_FILE"

        echo "✅ 智谱持续任务调度器已启动 (PID: $!)"
        echo "📝 日志: $LOG_DIR/zhipu_scheduler.log"
        ;;

    stop)
        echo "⏹️  停止智谱持续任务调度器..."

        if [ ! -f "$PID_FILE" ]; then
            echo "⚠️  调度器未运行"
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null

        # 等待进程结束
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done

        # 强制杀死（如果还在运行）
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  强制终止进程..."
            kill -9 "$PID" 2>/dev/null
        fi

        rm -f "$PID_FILE"
        echo "✅ 智谱持续任务调度器已停止"
        ;;

    restart)
        $0 stop
        sleep 2
        $0 start
        ;;

    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ 智谱持续任务调度器运行中 (PID: $PID)"

                # 显示最近的工作日志
                if [ -f "$WORKSPACE/logs/zhipu_continuous_work.jsonl" ]; then
                    echo ""
                    echo "📊 最近的工作记录:"
                    tail -5 "$WORKSPACE/logs/zhipu_continuous_work.jsonl" | jq -r '[.timestamp, .task_title, .status] | @tsv' 2>/dev/null || tail -5 "$WORKSPACE/logs/zhipu_continuous_work.jsonl"
                fi
            else
                echo "❌ PID文件存在但进程未运行"
                exit 1
            fi
        else
            echo "⏸️  智谱持续任务调度器未运行"
        fi
        ;;

    stats)
        python3 "$SCHEDULER" stats
        ;;

    scan)
        python3 "$SCHEDULER" scan
        ;;

    log)
        if [ -f "$LOG_DIR/zhipu_scheduler.log" ]; then
            tail -f "$LOG_DIR/zhipu_scheduler.log"
        else
            echo "❌ 日志文件不存在"
            exit 1
        fi
        ;;

    *)
        echo "智谱持续任务调度器 - 管理脚本"
        echo ""
        echo "用法: $0 {start|stop|restart|status|stats|scan|log}"
        echo ""
        echo "命令:"
        echo "  start   - 启动调度器（后台运行）"
        echo "  stop    - 停止调度器"
        echo "  restart - 重启调度器"
        echo "  status  - 查看运行状态"
        echo "  stats   - 显示工作统计"
        echo "  scan    - 扫描TODO.md任务"
        echo "  log     - 实时查看日志"
        echo ""
        echo "示例:"
        echo "  $0 start   # 启动调度器"
        echo "  $0 status  # 查看状态"
        echo "  $0 stats   # 查看统计"
        exit 1
        ;;
esac

exit 0
