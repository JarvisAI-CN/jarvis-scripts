# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 🔐 密码管理
**所有密码和凭据**已集中存储于: `PASSWORDS.md`
- 文件权限: 600 (仅root可读写)
- 包含: WebDAV、VNC、API密钥、系统账户等
- ⚠️ 谨慎处理，避免泄露

## 快速参考
### 网络服务
- 123盘WebDAV: /home/ubuntu/123pan
- VNC服务器: localhost:5901 (密码见PASSWORDS.md)
- 内网IP: 10.7.0.5
- GitHub: https://github.com/JarvisAI-CN (账号凭证见PASSWORDS.md)

### 系统路径
- 工作区: /home/ubuntu/.openclaw/workspace
- 备份脚本: /home/ubuntu/.openclaw/workspace/backup.sh
- 备份日志: /home/ubuntu/.openclaw/workspace/logs/backup_123pan.log
- 123盘备份: /home/ubuntu/123pan/备份/

### 知识管理工具
- **Obsidian**: 我的整个工作区是一个Obsidian vault
- **obsidian-cli** (v0.5.1): 命令行工具
  - 安装路径: `/home/ubuntu/.nvm/versions/node/v24.13.0/bin/obsidian`
  - 全局链接: `/usr/local/bin/obsidian`
  - 功能: 搜索、创建、移动笔记，自动更新双链
  - 使用文档: `[[Zettelkasten/Obsidian使用实践]]`
- **OBSIDAN-STATUS.md**: 双链优化进度追踪
- **实践原则**:
  - 新笔记必用 `[[...]]` 链接相关内容
  - 更新笔记时主动添加新发现的关联
  - 回顾时跟随链接探索，补充缺失链接

## 🔧 宝塔面板
**地址**: http://82.157.20.7:8888/fs123456
**用途**: 服务器管理面板

**主要功能**:
- LNMP环境一键安装
- 网站创建和管理
- MySQL数据库管理
- PHP版本切换（多版本共存）
- SSL证书一键部署
- 文件管理器（在线编辑）
- 计划任务管理

**部署流程**:
1. 登录宝塔面板
2. 软件商店 → 安装Nginx/PHP/MySQL
3. 网站创建 → 添加站点
4. 上传代码到/www/wwwroot/域名/
5. 配置伪静态和SSL
6. 测试访问

**使用建议**:
- PHP项目优先用宝塔快速测试
- 生产环境记得配置SSL
- 定期备份数据库
- 监控服务器资源

---
