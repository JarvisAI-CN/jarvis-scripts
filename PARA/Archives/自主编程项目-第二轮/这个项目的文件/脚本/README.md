# auto_maintain_v2.sh 使用文档

## 概述

`auto_maintain_v2.sh` 是自主编程系统 v2.0 的自动维护脚本,实现了对关键服务的健康检查和渐进式自动修复。

## 功能特性

### 1. 健康检查
- ✅ **WebDAV**: 检查挂载状态、读写权限
- ✅ **VNC**: 检查端口监听、进程状态
- ✅ **宝塔面板**: 检查端口、HTTP响应、进程状态
- ✅ **OpenClaw Gateway**: 检查运行状态
- ✅ **磁盘空间**: 检查使用率并自动清理

### 2. 渐进式修复
每个故障都有多级修复策略,从轻量级到重量级:
- 策略1: 最小干预(如重新挂载)
- 策略2: 服务重启
- 策略3: 深度修复(如修复配置)

### 3. 完整日志记录
- 详细的操作日志
- 告警分离记录
- 时间戳精确到秒
- 支持日志压缩

## 目录结构

```
scripts/
├── auto_maintain_v2.sh          # 主脚本
├── modules/
│   ├── health_checks.sh         # 健康检查函数库
│   └── fix_strategies.sh        # 修复策略函数库
├── config/
│   └── maintenance_config.json  # 配置文件
├── logs/                        # 日志目录
│   ├── auto_maintain_YYYYMMDD.log
│   └── alerts.log
└── README.md                    # 本文档
```

## 使用方法

### 手动执行

```bash
# 运行完整检查
./auto_maintain_v2.sh

# 查看日志
tail -f logs/auto_maintain_$(date +%Y%m%d).log

# 查看告警
cat logs/alerts.log
```

### 定时执行

```bash
# 添加到 crontab
crontab -e

# 每10分钟执行一次
*/10 * * * * /home/ubuntu/.openclaw/workspace/PARA/Projects/自主编程项目-第二轮/这个项目的文件/脚本/auto_maintain_v2.sh >> /dev/null 2>&1
```

### 配置修改

编辑 `config/maintenance_config.json`:

```json
{
  "checks": {
    "webdav": {
      "enabled": true,
      "mount_point": "/home/ubuntu/123pan"
    }
  }
}
```

## 修复策略示例

### WebDAV 挂载失败

```bash
策略1: mount -a (重新挂载)
   ↓ 失败
策略2: systemctl restart davfs2 (重启服务)
   ↓ 失败
策略3: 手动挂载并检查配置
```

### VNC 端口未监听

```bash
策略1: vncserver -kill :1 && vncserver :1 (重启VNC)
   ↓ 失败
策略2: pkill -9 -f Xvnc && vncserver :1 (强制重启)
   ↓ 失败
策略3: vncserver :2 (使用不同显示号)
```

### 磁盘空间不足

```bash
策略1: 删除7天前的日志文件
   ↓ 仍不足
策略2: 清理apt/npm/pip缓存
   ↓ 仍不足
策略3: 发送告警,建议手动扩容
```

## 日志级别

- **INFO**: 正常操作信息
- **SUCCESS**: 操作成功
- **WARNING**: 警告(可自动修复)
- **ERROR**: 错误(所有策略均失败)
- **ALERT**: 需要人工介入的严重问题

## 锁机制

- 防止同时运行多个实例
- 自动检测并清理过期锁
- 锁文件位置: `/tmp/auto_maintain_v2.lock`

## 安全性

- 使用 `set -euo pipefail` 严格模式
- 每个修复策略都有超时保护
- 失败时自动回滚
- 完整的错误日志

## 故障排查

### 脚本无法运行
```bash
# 检查权限
ls -l auto_maintain_v2.sh
# 应该有执行权限 (-rwxr-xr-x)

# 添加权限
chmod +x auto_maintain_v2.sh
```

### 检查失败但服务正常
```bash
# 查看详细日志
grep "WARNING\|ERROR" logs/auto_maintain_*.log

# 手动运行单个检查
source modules/health_checks.sh
webdav_check_mount
```

### 修复策略全部失败
```bash
# 查看修复日志
grep "策略.*失败" logs/auto_maintain_*.log

# 查看告警
cat logs/alerts.log
```

## 依赖项

```bash
# 必需命令
bash 4.0+
mount, umount
systemctl
netstat
psgrep

# 可选命令
curl (用于宝塔面板HTTP检查)
```

## 性能考虑

- 单次完整检查: ~5-10秒
- 内存占用: <10MB
- 磁盘占用: 约1MB/天(日志)

## 未来改进

- [ ] 支持 YAML/INI 配置
- [ ] Web 界面监控
- [ ] 飞书/企业微信告警集成
- [ ] 自动创建备份点
- [ ] 支持自定义检查插件

## 更新日志

### v2.0 (2026-02-13)
- ✅ 实现WebDAV、VNC、宝塔面板检查
- ✅ 渐进式修复逻辑
- ✅ 完整日志系统
- ✅ 告警分离记录
- ✅ 锁机制优化

## 作者

- GLM-4.7 (工程主管)
- 自主编程项目 v2.0

## 许可证

MIT License
