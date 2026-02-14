#!/bin/bash
# NCM转换器Web应用启动脚本

echo "============================================================"
echo "🚀 启动NCM转换器Web应用"
echo "============================================================"
echo ""

# 检查Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask未安装"
    echo "📥 安装Flask..."
    pip3 install --break-system-packages flask
fi

# 创建必要的目录
mkdir -p /tmp/ncm_web_uploads
mkdir -p /tmp/ncm_web_output

# 检查端口
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口5000已被占用"
    echo "🔄 停止旧进程..."
    pkill -f "ncm_web_app.py"
    sleep 2
fi

# 启动应用
echo "🌐 启动Web应用..."
cd /home/ubuntu/.openclaw/workspace/scripts
python3 ncm_web_app.py &

APP_PID=$!

echo ""
echo "============================================================"
echo "✅ Web应用已启动"
echo "============================================================"
echo ""
echo "📋 信息:"
echo "   PID: $APP_PID"
echo "   端口: 5000"
echo "   地址: http://localhost:5000"
echo ""
echo "🌐 访问方式:"
echo "   本地: http://localhost:5000"
echo "   VNC: http://服务器IP:5000"
echo ""
echo "🔧 宝塔面板反向代理配置:"
echo "   1. 创建网站: ncm.dhmip.cn"
echo "   2. 设置反向代理 -> http://127.0.0.1:5000"
echo "   3. 启用SSL证书"
echo ""
echo "⏹️  停止应用: pkill -f 'ncm_web_app.py'"
echo ""
