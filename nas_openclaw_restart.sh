#!/bin/bash
# NAS OpenClaw 重启脚本
# 用途：通过SSH重启NAS上的OpenClaw Gateway

NAS_HOST="fsnas.top"
NAS_USER="shuaishuai"
NAS_PASS="fs159753."
START_SCRIPT="/volume2/homes/shuaishuai/start-openclaw.sh"

echo "=== NAS OpenClaw 重启脚本 ==="
echo "目标: $NAS_USER@$NAS_HOST"
echo "时间: $(date)"
echo ""

# 检查sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass未安装，正在安装..."
    sudo apt-get update -qq && sudo apt-get install -y sshpass
fi

# 1. 检查OpenClaw进程
echo "步骤1：检查OpenClaw进程..."
sshpass -p "$NAS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    "$NAS_USER@$NAS_HOST" "pgrep -l openclaw || echo 'OpenClaw未运行'"

# 2. 停止旧进程（如果存在）
echo ""
echo "步骤2：停止旧进程..."
sshpass -p "$NAS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    "$NAS_USER@$NAS_HOST" "pkill -f openclaw; sleep 2; echo '进程已终止'"

# 3. 启动OpenClaw
echo ""
echo "步骤3：启动OpenClaw Gateway..."
sshpass -p "$NAS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    "$NAS_USER@$NAS_HOST" "cd ~/.openclaw && nohup ./start-openclaw.sh > /dev/null 2>&1 & echo '启动命令已执行'"

# 4. 等待启动
echo ""
echo "步骤4：等待启动（5秒）..."
sleep 5

# 5. 验证状态
echo ""
echo "步骤5：验证启动状态..."
sshpass -p "$NAS_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    "$NAS_USER@$NAS_HOST" "pgrep -l openclaw && netstat -tlnp 2>/dev/null | grep 18789"

echo ""
echo "=== 重启完成 ==="
echo "如果需要查看日志："
echo "ssh $NAS_USER@$NAS_HOST 'tail -f /tmp/openclaw/openclaw-*.log'"
