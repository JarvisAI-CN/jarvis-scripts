# 123盘 WebDAV 服务器

## 📁 目录结构

```
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
```

## 🔄 自动备份

- **备份脚本**: `/home/ubuntu/.openclaw/workspace/backup.sh`
- **备份日志**: `/home/ubuntu/.openclaw/workspace/logs/backup_123pan.log`
- **备份频率**: 每日凌晨 3:00
- **备份内容**: 工作区、配置文件、重要数据

## 🛠️ 维护命令

### 检查挂载状态
```bash
mount | grep 123pan
```

### 重新挂载WebDAV
```bash
sudo umount /mnt/123pan-webdav
sudo mount -t davfs https://webdav.123pan.cn/webdav /mnt/123pan-webdav
```

### 查看备份日志
```bash
tail -f /home/ubuntu/.openclaw/workspace/logs/backup_123pan.log
```

### 手动备份
```bash
bash /home/ubuntu/.openclaw/workspace/backup.sh
```

## 📊 系统信息

- **服务器**: Ubuntu 22.04 LTS
- **WebDAV服务**: 123盘 (https://www.123pan.com)
- **WebDAV URL**: https://webdav.123pan.cn/webdav
- **本地路径**: `/mnt/123pan-webdav`
- **最后更新**: 2026-03-31 08:00:00

## ⚠️ 注意事项

1. **不要删除**: `备份/` 目录中的文件是系统恢复的关键
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
*更新时间: 2026-03-31 08:00:00*
