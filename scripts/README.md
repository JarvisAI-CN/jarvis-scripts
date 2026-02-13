# 自主编程系统 v2.0 - 核心脚本

**版本**: 2.0
**更新时间**: 2026-02-13
**作者**: GLM-4.7 (贾维斯)

---

## 📁 文件结构

```
scripts/
├── auto_maintain_v2.sh          # 主维护脚本
├── auto_maintain.sh             # 旧版本（保留）
├── api_health_monitor_v2.py     # API健康监控（保留）
├── modules/
│   ├── health_checks.sh         # 健康检查函数库
│   └── fix_strategies.sh        # 修复策略函数库
└── README.md                   # 本文档
```

---

## 🚀 快速开始

### 基本使用

```bash
# 完整维护流程（推荐）
./auto_maintain_v2.sh run

# 仅健康检查，不修复
./auto_maintain_v2.sh check

# 强制修复指定项
./auto_maintain_v2.sh fix webdav
./auto_maintain_v2.sh fix gateway
./auto_maintain_v2.sh fix disk_space

# 事件驱动模式（持续监听）
./auto_maintain_v2.sh event
```

### 定时任务配置

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每2小时执行一次）
0 */2 * * * /home/ubuntu/.openclaw/workspace/scripts/auto_maintain_v2.sh run >> /home/ubuntu/.openclaw/workspace/logs/cron.log 2>&1
```

---

## 🔍 健康检查项

| 检查项 | 检测内容 | 严重级别 | 自动修复 |
|-------|---------|---------|---------|
| **Gateway** | OpenClaw Gateway 进程状态 | 🔴 严重 | ✅ 支持 |
| **WebDAV** | 123盘挂载状态和读写权限 | 🟠 警告 | ✅ 支持 |
| **API** | 模型供应商认证状态 | 🟠 警告 | ✅ 支持 |
| **VNC** | VNC 服务端口监听 | 🟡 提示 | ✅ 支持 |
| **宝塔面板** | bt 服务运行状态 | 🟡 提示 | ✅ 支持 |
| **磁盘空间** | 根分区使用率 | 🟠 警告 | ✅ 支持 |
| **Git** | 工作区状态和远程同步 | 🟡 提示 | ✅ 支持 |
| **GitHub** | SSH/HTTPS 连接性 | 🟠 警告 | ⚠️ 部分支持 |

---

## 🛠️ 修复策略

### Gateway 修复
1. 优雅停止
2. 强制杀死残留进程
3. 重新启动

### WebDAV 修复
1. 重新挂载
2. 重启 davfs2 服务
3. 检查并修复凭证

### API 修复
1. 刷新 Google-antigravity 认证
2. 切换到 Zhipu 备用供应商
3. 重启 Gateway

### 磁盘清理
1. 删除7天前的日志
2. 清理临时文件
3. 压缩30天前的日志

---

## 📊 输出文件

### 日志文件
- **主日志**: `logs/auto_maintain_v2.log`
- **格式**: `[时间] [级别] 消息`

### 状态文件
- **状态**: `.maintenance_state.json`
- **告警**: `.maintenance_alerts.json`

### 状态示例
```json
{
  "timestamp": "2026-02-13T16:42:45+08:00",
  "status": "fixed",
  "checks": {
    "gateway": "ok",
    "webdav": "failed",
    "api_health": "ok",
    "vnc": "ok",
    "bt_panel": "ok",
    "disk_space": "warning",
    "git_sync": "ok"
  }
}
```

---

## 🔧 扩展开发

### 添加新的健康检查

编辑 `modules/health_checks.sh`:

```bash
check_your_service() {
    # 你的检查逻辑
    if your_condition; then
        echo "✅ 你的服务: 正常"
        return 0
    else
        echo "❌ 你的服务: 异常"
        return 1
    fi
}

# 导出函数
export -f check_your_service
```

### 添加新的修复策略

编辑 `modules/fix_strategies.sh`:

```bash
fix_your_service() {
    log "INFO" "开始修复你的服务..."
    
    # 策略1
    if try_fix_1; then
        log "SUCCESS" "✅ 修复成功"
        return 0
    fi
    
    # 策略2
    if try_fix_2; then
        log "SUCCESS" "✅ 修复成功"
        return 0
    fi
    
    log "ERROR" "❌ 修复失败"
    return 1
}

# 导出函数
export -f fix_your_service
```

### 集成到主脚本

编辑 `auto_maintain_v2.sh`:

```bash
# 在健康检查部分添加
if ! check_your_service > /dev/null 2>&1; then
    failed_checks+=("your_service")
    checks_result=$(echo "$checks_result" | jq '.your_service = "failed"')
else
    checks_result=$(echo "$checks_result" | jq '.your_service = "ok"')
fi

# 在 progressive_fix 函数中添加
your_service)
    check_your_service
    ;;
```

---

## 🐛 故障排除

### 问题：脚本无执行权限

```bash
chmod +x /home/ubuntu/.openclaw/workspace/scripts/auto_maintain_v2.sh
chmod +x /home/ubuntu/.openclaw/workspace/scripts/modules/*.sh
```

### 问题：jq 命令未找到

```bash
# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

### 问题：WebDAV 一直修复失败

这是已知的凭证问题，需要人工介入：

```bash
# 检查凭证文件
cat ~/.davfs2/secrets

# 重新配置凭证（需要密码，见 PASSWORDS.md）
```

---

## 📈 性能优化

### 当前性能
- **检查耗时**: ~3-5秒
- **修复耗时**: ~10-30秒
- **内存占用**: < 50MB

### 优化建议
1. 并行执行健康检查（使用 `&` 和 `wait`）
2. 缓存不需要频繁检查的项目
3. 使用更快的 JSON 解析器

---

## 🔄 与旧版本的差异

| 特性 | v1.0 (auto_maintain.sh) | v2.0 (auto_maintain_v2.sh) |
|-----|-------------------------|---------------------------|
| 健康检查 | 3项 | 8项 |
| 修复策略 | 单一（重启） | 渐进式（多策略） |
| 模块化 | 无 | 高 |
| 日志 | 简单 | 结构化 |
| 状态管理 | 无 | JSON |
| 告警 | 无 | 支持 |
| 扩展性 | 低 | 高 |

---

## 📝 维护者

**开发者**: GLM-4.7 (贾维斯)
**项目**: 自主编程项目-第二轮
**位置**: `PARA/Projects/自主编程项目-第二轮/`

---

## 📄 许可

本脚本作为贾维斯自动化系统的一部分，仅供内部使用。

---

**最后更新**: 2026-02-13
**版本**: 2.0
