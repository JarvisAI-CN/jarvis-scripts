# Postfix SASL认证问题修复

**修复时间**: 2026-02-06 10:59 GMT+8

---

## ❌ 问题

**错误**: `fatal: no SASL authentication mechanisms`

**原因**: 
- 配置了SMTP认证：`smtpd_sasl_auth_enable = yes`
- 但SASL认证库未安装
- 导致外部邮件连接时崩溃

**日志**:
```
connect from m218-159.88.com[110.43.218.159]
fatal: no SASL authentication mechanisms
warning: process /usr/libexec/postfix/smtpd exit status 1
```

---

## ✅ 修复

### 方案：临时禁用SMTP认证
**接收邮件不需要SMTP认证**，发送邮件才需要。

**修改**:
1. 注释掉SASL认证相关配置
2. 注释掉重复的mynetworks和recipient_restrictions

**配置文件**: /etc/postfix/main.cf

**修改内容**:
```conf
# smtpd_sasl_auth_enable = yes
# smtpd_sasl_type = dovecot
# smtpd_sasl_path = private/auth

# mynetworks = 127.0.0.0/8, 10.0.0.0/8
# smtpd_recipient_restrictions = ...
```

**重启Postfix**: `systemctl restart postfix`

---

## 🎯 预期结果

修复后：
- ✅ 外部邮件可以连接到端口25
- ✅ 邮件可以正常接收
- ✅ 不再出现SASL错误

---

## 📧 后续优化

如果需要SMTP认证（用于发送邮件）：
1. 安装cyrus-sasl
2. 配置SASL认证
3. 重新启用认证

但对于接收邮件，不需要认证。

---

**主人，正在修复中...**
