#!/bin/bash
# 贾维斯升级脚本 - 安装开发工具

echo "=== 贾维斯升级开始 ==="
echo "安装时间: $(date)"
echo ""

# 步骤1: 更新系统包
echo "📍 步骤1: 更新系统包"
sudo apt update >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ 系统包已更新"
echo ""

# 步骤2: 安装Python开发工具
echo "📍 步骤2: 安装Python开发工具"
pip3 install --upgrade pip --break-system-packages >> /tmp/jarvis_upgrade.log 2>&1
pip3 install --break-system-packages \
    black \
    ruff \
    mypy \
    pytest \
    pylint \
    isort \
    autoflake \
    bandit >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ Python工具已安装"
echo "   - black: 代码格式化"
echo "   - ruff: 快速linting"
echo "   - mypy: 类型检查"
echo "   - pytest: 测试框架"
echo "   - pylint: 代码质量"
echo ""

# 步骤3: 安装Git增强工具
echo "📍 步骤3: 安装Git增强工具"
sudo apt install -y jq gh git-lfs >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ Git工具已安装"
echo "   - jq: JSON处理"
echo "   - gh: GitHub CLI"
echo "   - git-lfs: 大文件支持"
echo ""

# 步骤4: 安装Node.js
echo "📍 步骤4: 安装Node.js"
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - >> /tmp/jarvis_upgrade.log 2>&1
sudo apt install -y nodejs >> /tmp/jarvis_upgrade.log 2>&1
npm install -g npm@latest >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ Node.js已安装"
node --version
npm --version
echo ""

# 步骤5: 安装常用命令行工具
echo "📍 步骤5: 安装命令行工具"
sudo apt install -y \
    build-essential \
    cmake \
    htop \
    iotop \
    ncdu \
    tree \
    ripgrep \
    fd-find \
    bat \
    exa \
    tldr \
    fzf >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ 命令行工具已安装"
echo "   - htop: 系统监控"
echo "   - ncdu: 磁盘分析"
echo "   - ripgrep: 快速搜索"
echo "   - bat: 更好的cat"
echo "   - exa: 更好的ls"
echo ""

# 步骤6: 安装AI SDK
echo "📍 步骤6: 安装AI SDK"
pip3 install --break-system-packages \
    anthropic \
    openai \
    google-generativeai >> /tmp/jarvis_upgrade.log 2>&1
echo "✅ AI SDK已安装"
echo "   - anthropic: Claude API"
echo "   - openai: GPT API"
echo "   - google-generativeai: Gemini API"
echo ""

# 步骤7: 安装Docker
echo "📍 步骤7: 安装Docker"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh >> /tmp/jarvis_upgrade.log 2>&1
    sudo sh get-docker.sh >> /tmp/jarvis_upgrade.log 2>&1
    sudo usermod -aG docker ubuntu
    echo "✅ Docker已安装"
else
    echo "✅ Docker已存在"
fi
echo ""

# 步骤8: 验证安装
echo "📍 步骤8: 验证安装"
echo ""
echo "=== Python工具 ==="
black --version 2>/dev/null || echo "black未安装"
ruff --version 2>/dev/null || echo "ruff未安装"
echo ""
echo "=== Git工具 ==="
gh --version 2>/dev/null || echo "gh未安装"
jq --version 2>/dev/null || echo "jq未安装"
echo ""
echo "=== Node.js ==="
node --version 2>/dev/null || echo "Node.js未安装"
npm --version 2>/dev/null || echo "npm未安装"
echo ""
echo "=== Docker ==="
docker --version 2>/dev/null || echo "Docker未安装"
echo ""
echo "=== AI SDK ==="
python3 -c "import anthropic; print('anthropic:', anthropic.__version__)" 2>/dev/null || echo "anthropic未安装"
python3 -c "import openai; print('openai:', openai.__version__)" 2>/dev/null || echo "openai未安装"
echo ""

echo "=== 🎉 升级完成 ==="
echo ""
echo "📊 安装日志: /tmp/jarvis_upgrade.log"
echo ""
echo "✨ 现在贾维斯更强大了！"
echo "   - 代码质量更高（black、ruff）"
echo "   - 可以写Node.js代码"
echo "   - 更好的项目管理（gh、jq）"
echo "   - 可以调用Claude/GPT API"
echo "   - 支持Docker容器化"
echo ""
echo "🚀 准备接受新任务！"
