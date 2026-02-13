# Outlook SMTP 修复指南

**问题**: jarvis-cn-ai@outlook.com 的 SMTP 服务已被禁用
**原因**: Outlook 不再支持普通密码进行 SMTP 认证
**解决方案**: 使用应用专用密码（App Password）

---

## 🔧 快速修复（3分钟）

### 步骤 1: 创建应用专用密码

1. **访问**: https://account.live.com/proofs/AppPassword
2. **登录**: 使用您的 Microsoft 账户（jarvis-cn-ai@outlook.com）
3. **创建新密码**:
   - 点击"新建"
   - 输入密码名称（例如：JarvisAI）
   - 点击"下一步"
4. **复制密码**:
   - 复制生成的 16 位密码（格式：abcd1234efgh5678）
   - ⚠️ 一次性显示，请立即保存

### 步骤 2: 更新贾维斯的配置

**将新应用专用密码发送给贾维斯**，格式示例：

```
应用专用密码是：abcd1234efgh5678
```

贾维斯会自动更新：
- ✅ `/home/ubuntu/.openclaw/workspace/scripts/email_tool.py`
- ✅ `/home/ubuntu/.openclaw/workspace/PASSWORDS.md`

### 步骤 3: 测试

贾维斯会自动测试 SMTP 连接，确认邮件发送功能正常。

---

## 📝 配置文件位置

- **邮件脚本**: `/home/ubuntu/.openclaw/workspace/scripts/email_tool.py`
- **密码管理**: `/home/ubuntu/.openclaw/workspace/PASSWORDS.md`
- **当前状态**: SMTP 密码字段已标记为 `YOUR_APP_PASSWORD_HERE`

---

## ⚠️ 重要提示

1. **应用专用密码只显示一次**，请立即保存
2. **不要在群聊或公开场合发送密码**，私发给贾维斯
3. **应用专用密码不可撤销**，但可以在 Microsoft 账户中管理
4. **普通密码仍可用于 IMAP**，只有 SMTP 需要应用专用密码

---

## 🎯 完成后功能

- ✅ 发送邮件（SMTP）
- ✅ 接收邮件（IMAP，已正常）
- ✅ 邮件监控和通知
- ✅ 自动报告和通知

---

**创建时间**: 2026-02-09 06:50 GMT+8
**维护者**: Jarvis (贾维斯) ⚡
