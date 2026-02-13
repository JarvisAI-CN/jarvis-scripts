# Dovecot SASL配置

**配置文件**: /etc/dovecot/conf.d/10-master.conf

---

## 🔍 需要配置的部分

查找 `service auth` 部分，添加unix_listener配置：

```
service auth {
  unix_listener /var/spool/postfix/private/auth {
    mode = 0666
    user = postfix
    group = postfix
  }
}
```

**目的**: 让Postfix可以通过Dovecot的socket进行SMTP认证
