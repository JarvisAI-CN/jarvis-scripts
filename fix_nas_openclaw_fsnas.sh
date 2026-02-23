#!/bin/bash

# NAS OpenClaw 模型配置修复脚本 (fsnas.top)
# 将默认模型从 SiliconFlow 改为智谱4.7

echo "=== NAS OpenClaw 模型配置修复 ==="

# 检查当前配置
CONFIG_PATH="/var/services/homes/shuaishuai/.openclaw/config.json"
AUTH_PATH="/var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json"

echo "1. 检查当前配置文件..."

if [ -f "$CONFIG_PATH" ]; then
    echo "当前 config.json 内容："
    cat "$CONFIG_PATH"
    echo ""
else
    echo "⚠️ config.json 文件不存在"
fi

if [ -f "$AUTH_PATH" ]; then
    echo "当前 auth-profiles.json 内容："
    cat "$AUTH_PATH"
    echo ""
else
    echo "⚠️ auth-profiles.json 文件不存在"
fi

echo "2. 修改默认模型为智谱4.7..."

# 创建或更新 config.json
cat > "$CONFIG_PATH" << 'EOF'
{
  "model": {
    "default": "zhipu/glm-4.7"
  }
}
EOF

echo "✅ config.json 已更新"

echo "3. 检查并创建认证配置..."

if [ ! -f "$AUTH_PATH" ]; then
    cat > "$AUTH_PATH" << 'EOF'
{
  "providers": {
    "zhipu": {
      "apiKey": "你的智谱API密钥"
    }
  }
}
EOF
    echo "✅ auth-profiles.json 已创建"
else
    echo "ℹ️ auth-profiles.json 已存在"
fi

echo "4. 重启 OpenClaw 服务..."

# 停止当前进程
pkill -f "openclaw gateway" 2>/dev/null
pkill -f "node.*openclaw" 2>/dev/null

# 等待进程结束
sleep 2

# 启动 OpenClaw Gateway
npm exec openclaw gateway -- --daemon > /dev/null 2>&1 &

# 等待启动
sleep 5

echo "5. 验证服务状态..."

if pgrep -f "openclaw gateway" > /dev/null; then
    echo "✅ OpenClaw Gateway 运行正常"
    PID=$(pgrep -f "openclaw gateway")
    echo "   PID: $PID"
else
    echo "❌ OpenClaw Gateway 启动失败"
fi

# 检查端口
if ss -tuln | grep -q 18789; then
    echo "✅ 端口 18789 正常监听"
else
    echo "❌ 端口 18789 未监听"
fi

echo ""
echo "=== 修复完成 ==="
echo "现在 OpenClaw 应该使用智谱4.7模型回复消息了"
echo "如果还有问题，请检查："
echo "1. 智谱API密钥是否正确"
echo "2. 网络连接是否正常"
echo "3. OpenClaw 日志是否有错误"
echo "   查看日志命令：openclaw logs --follow"
