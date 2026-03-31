#!/bin/bash
# 更新123盘WebDAV README文件
# 任务ID: f777ec0b-a213-4245-a30a-68427f44e017

set -e

WEBDAV_MOUNT="/mnt/123pan-webdav"
README_FILE="$WEBDAV_MOUNT/readme.md"
LOG_FILE="/home/ubuntu/.openclaw/workspace/logs/readme_update.log"
BACKUP_SCRIPT="/home/ubuntu/.openclaw/workspace/backup.sh"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查WebDAV是否可访问
check_webdav() {
    # 检查挂载状态
    if ! mount | grep -q "$WEBDAV_MOUNT"; then
        log "⚠️  WebDAV未挂载，尝试挂载..."
        sudo mkdir -p "$WEBDAV_MOUNT"
        sudo mount -t davfs https://webdav.123pan.cn/webdav "$WEBDAV_MOUNT" 2>/dev/null || {
            log "❌ WebDAV挂载失败"
            return 1
        }
        sleep 3
    fi

    # 检查是否可访问
    if ! ls "$WEBDAV_MOUNT" &>/dev/null; then
        log "❌ WebDAV挂载点不可访问"
        return 1
    fi

    return 0
}

# 生成README内容
generate_readme() {
    local update_time=$(date '+%Y-%m-%d %H:%M:%S')

    cat << EOF
# 123盘 WebDAV 服务器

## 📁 目录结构

\`\`\`
/mnt/123pan-webdav/
├── 备份/           # 系统备份文件
├── 博客/           # 博客文章
├── 播客/           # 播客资源
├── 共享资源/       # 共享文件
├── 项目留存/       # 项目归档
├── 截图日志/       # 系统截图
├── 记忆恢复指南.md # 系统恢复文档
├── readme.md       # 本文件
└── lost+found/     # 系统目录
\`\`\`

## 🔄 自动备份

- **备份脚本**: \`/home/ubuntu/.openclaw/workspace/backup.sh\`
- **备份日志**: \`/home/ubuntu/.openclaw/workspace/logs/backup_123pan.log\`
- **备份频率**: 每日凌晨 3:00
- **备份内容**: 工作区、配置文件、重要数据

## 🛠️ 维护命令

### 检查挂载状态
\`\`\`bash
mount | grep 123pan
\`\`\`

### 重新挂载WebDAV
\`\`\`bash
sudo umount /mnt/123pan-webdav
sudo mount -t davfs https://webdav.123pan.cn/webdav /mnt/123pan-webdav
\`\`\`

### 查看备份日志
\`\`\`bash
tail -f /home/ubuntu/.openclaw/workspace/logs/backup_123pan.log
\`\`\`

### 手动备份
\`\`\`bash
bash /home/ubuntu/.openclaw/workspace/backup.sh
\`\`\`

## 📊 系统信息

- **服务器**: Ubuntu 22.04 LTS
- **WebDAV服务**: 123盘 (https://www.123pan.com)
- **WebDAV URL**: https://webdav.123pan.cn/webdav
- **本地路径**: \`/mnt/123pan-webdav\`
- **最后更新**: ${update_time}

## ⚠️ 注意事项

1. **不要删除**: \`备份/\` 目录中的文件是系统恢复的关键
2. **定期检查**: 每月检查挂载状态和备份完整性
3. **网络稳定**: WebDAV需要稳定的网络连接
4. **权限管理**: 备份脚本需要root权限

## 📞 联系方式

- **维护者**: 贾维斯 (AI助手)
- **邮箱**: jarvis.openclaw@email.cn
- **GitHub**: https://github.com/JarvisAI-CN

---

*本文档由自动化脚本生成并维护*
*任务ID: f777ec0b-a213-4245-a30a-68427f44e017*
EOF
}

# 主函数
main() {
    log "🚀 开始更新README..."

    # 检查WebDAV
    if ! check_webdav; then
        log "⚠️  WebDAV不可用，跳过更新"
        exit 0
    fi

    # 生成新README
    TEMP_README=$(mktemp)
    generate_readme > "$TEMP_README"

    # 备份旧README（如果存在且可读）
    if [ -r "$README_FILE" ]; then
        cp "$README_FILE" "${README_FILE}.bak.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
        log "📦 已备份旧README"
    fi

    # 写入新README（尝试普通用户，失败则用sudo）
    if cp "$TEMP_README" "$README_FILE" 2>/dev/null; then
        log "✅ README更新成功"
        rm -f "$TEMP_README"
    elif [ "$EUID" -ne 0 ] && sudo cp "$TEMP_README" "$README_FILE" 2>/dev/null; then
        log "✅ README更新成功（使用sudo）"
        rm -f "$TEMP_README"
    else
        log "❌ README更新失败"
        rm -f "$TEMP_README"
        exit 1
    fi

    # 显示文件大小
    if [ -f "$README_FILE" ]; then
        SIZE=$(wc -c < "$README_FILE")
        log "📄 README大小: $SIZE 字节"
    fi

    log "✨ 任务完成"
}

# 执行
main
