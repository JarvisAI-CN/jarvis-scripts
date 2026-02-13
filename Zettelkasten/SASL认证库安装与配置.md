# SASL认证库安装与配置

**安装时间**: 2026-02-06 11:05 GMT+8
**目的**: 彻底解决Postfix SMTP认证问题

---

## 🔧 安装步骤

### 1. 安装SASL库
```bash
yum install cyrus-sasl cyrus-sasl-plain cyrus-sasl-md5 -y
```

### 2. 启动saslauthd服务
```bash
systemctl enable saslauthd
systemctl start saslauthd
```

### 3. 配置Postfix使用SASL
**文件**: /etc/postfix/main.cf

**配置**:
```conf
# SMTP认证
smtpd_sasl_auth_enable = yes
smtpd_sasl_type = dovecot
smtpd_sasl_path = private/auth
smtpd_sasl_security_options = noanonymous, noplaintext
smtpd_sasl_tls_security_options = noanonymous
```

### 4. 配置Dovecot SASL
**文件**: /etc/dovecot/conf.d/10-master.conf

**配置**:
```
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}
```

---

**开始安装...**
