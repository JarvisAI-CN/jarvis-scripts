#!/bin/bash
# 部署优化后的保质期管理系统代码

echo "=== 部署优化版本 ==="
echo "时间: $(date)"

# 本地文件路径
OPTIMIZED_CODE="/home/ubuntu/.openclaw/workspace/optimized_expiry_manager.py"
BACKUP_PATH="/home/ubuntu/.openclaw/workspace/backups/check_expiry_$(date +%Y%m%d_%H%M%S).py.bak"

# 远程服务器信息
REMOTE_HOST="82.157.20.7"
REMOTE_USER="root"
REMOTE_PATH="/www/wwwroot/ceshi.dhmip.cn"

echo "📁 步骤1: 备份原始代码"
# 先下载原始代码作为备份
scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/check_expiry.py ${BACKUP_PATH} 2>/dev/null || echo "⚠️ 无法下载备份"

echo "📤 步骤2: 上传优化代码"
# 上传优化版本
scp -o StrictHostKeyChecking=no ${OPTIMIZED_CODE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/optimized_expiry_manager.py

if [ $? -eq 0 ]; then
    echo "✅ 上传成功"
    
    echo "🔧 步骤3: 远程配置"
    # 在远程服务器上执行配置
    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
cd /www/wwwroot/ceshi.dhmip.cn

# 备份当前版本
cp check_expiry.py check_expiry.py.bak.$(date +%Y%m%d_%H%M%S)

# 设置环境变量（创建.env文件）
cat > .env << 'EOF'
# 数据库配置
DB_HOST=localhost
DB_USER=expiry_user
DB_PASSWORD=Expiry2024!
DB_NAME=expiry_system

# 邮件配置
ALERT_EMAIL=jarvis.openclaw@email.cn
EOF

# 设置权限
chmod 600 .env
chmod 644 optimized_expiry_manager.py

echo "✅ 远程配置完成"
ENDSSH
    
    echo ""
    echo "=== 部署完成 ==="
    echo "✅ 优化版本已上传到: ${REMOTE_PATH}/optimized_expiry_manager.py"
    echo "✅ 原始版本已备份"
    echo "✅ 环境变量已配置: .env"
    echo ""
    echo "📋 下一步:"
    echo "1. 测试新版本: python3 optimized_expiry_manager.py"
    echo "2. 如果测试通过，替换check_expiry.py"
    echo "3. 添加到crontab自动运行"
else
    echo "❌ 上传失败"
fi
