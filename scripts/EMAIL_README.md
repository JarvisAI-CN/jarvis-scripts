# 贾维斯的邮件工具

Outlook邮箱自动化工具集，支持收发邮件、监控、搜索等功能。

## 📧 邮箱配置

- **邮箱**: jarvis-cn-ai@outlook.com
- **密码**: Jarvis@2026AI#Helper
- **IMAP**: outlook.office365.com:993 (SSL)
- **SMTP**: smtp.office365.com:587 (STARTTLS)

## 🚀 快速开始

### 1. 检查邮箱统计

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py stats
```

### 2. 查看未读邮件

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py unread --limit 5
```

### 3. 查看最近邮件

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py recent --limit 10
```

### 4. 发送邮件

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py send \
  --to 'recipient@example.com' \
  --subject '邮件主题' \
  --body '邮件正文内容'
```

### 5. 搜索邮件

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py search --search '关键词'
```

## 📬 邮件监控

定期检查新邮件并生成通知：

```bash
# 检查新邮件
python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py

# 检查新邮件并生成通知格式
python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py --notify

# 查看邮箱统计
python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py --stats
```

## 🤖 OpenClaw集成示例

在OpenClaw中调用邮件功能：

```python
# 检查新邮件
import subprocess
result = subprocess.run(
    ['python3', '/home/ubuntu/.openclaw/workspace/scripts/email_monitor.py'],
    capture_output=True,
    text=True
)
print(result.stdout)
```

## 📊 日志位置

- 监控日志: `/home/ubuntu/.openclaw/workspace/logs/email_monitor.log`
- 状态文件: `/home/ubuntu/.openclaw/workspace/.email_state.json`

## 🔧 高级功能

### 列出所有文件夹

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py list
```

### 查看特定文件夹

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py recent --folder "Sent Mail"
```

### 发送HTML邮件

```bash
python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py send \
  --to 'recipient@example.com' \
  --subject 'HTML邮件' \
  --body '<h1>标题</h1><p>内容</p>' \
  --html
```

## 📅 定时任务

添加到crontab自动检查邮件：

```cron
# 每10分钟检查一次新邮件
*/10 * * * * /usr/bin/python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py >> /home/ubuntu/.openclaw/workspace/logs/email_monitor.log 2>&1
```

## ⚠️ 注意事项

1. 密码存储在PASSWORDS.md中，请确保文件权限安全
2. 首次使用可能需要允许Outlook访问
3. 发送邮件频率不要太高，避免被标记为垃圾邮件
4. 定期检查日志文件大小

## 🎯 功能路线图

- [ ] 自动分类邮件
- [ ] 智能回复建议
- [ ] 邮件模板系统
- [ ] 附件处理
- [ ] 多账户支持
- [ ] 邮件提醒集成到OpenClaw

## 📝 更新日志

### 2026-02-08
- ✅ 创建基础邮件工具
- ✅ 实现IMAP/SMTP功能
- ✅ 添加邮件监控
- ✅ 支持搜索和统计

---

**创建者**: 贾维斯 ⚡
**邮箱**: jarvis-cn-ai@outlook.com
**版本**: 1.0.0
