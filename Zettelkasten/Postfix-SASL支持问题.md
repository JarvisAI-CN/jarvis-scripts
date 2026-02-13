# Postfix SASL支持问题

**问题**: `fatal: no SASL authentication mechanisms`
**原因**: Postfix需要cyrus-sasl库支持

---

## 🔍 诊断

### 1. 检查Postfix支持的SASL类型
```bash
postconf -a
```

### 2. 检查Postfix是否链接了SASL库
```bash
ldd /usr/libexec/postfix/smtpd | grep sasl
```

### 3. 安装的包
```bash
rpm -qa | grep -E "postfix|sasl"
```

---

## 💡 可能的解决方案

### 方案1：禁用SASL认证（临时）
对于**接收邮件**，不需要SMTP认证。

### 方案2：完全禁用smtpd_sasl
接收邮件不需要认证，可以直接禁用。

---

**正在检查Postfix SASL支持...**
