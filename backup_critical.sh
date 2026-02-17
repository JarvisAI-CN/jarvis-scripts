#!/bin/bash
# 立即备份到123盘 - 确保最新状态

echo "=== 开始备份 ==="
echo "时间: $(date)"

# 备份关键文件到123盘
cp /home/ubuntu/.openclaw/workspace/MEMORY.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/TOOLS.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/IDENTITY.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/USER.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/SOUL.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/AGENTS.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/贾维斯系统状态快照.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/灾难恢复指南.md /home/ubuntu/123pan/备份/
cp /home/ubuntu/.openclaw/workspace/.current_task.json /home/ubuntu/123pan/备份/

# 创建完整备份压缩包
cd /home/ubuntu/.openclaw/workspace
tar -czf /home/ubuntu/123pan/备份/jarvis_complete_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    MEMORY.md \
    TOOLS.md \
    IDENTITY.md \
    USER.md \
    SOUL.md \
    AGENTS.md \
    贾维斯系统状态快照.md \
    灾难恢复指南.md \
    .current_task.json \
    PARA/ \
    scripts/ \
    Zettelkasten/ \
    memory/ 2>/dev/null

echo "✅ 备份完成"
echo ""
echo "备份文件:"
ls -lht /home/ubuntu/123pan/备份/ | head -10
