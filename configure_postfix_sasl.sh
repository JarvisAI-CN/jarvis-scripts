#!/bin/bash
# Postfix SMTP认证配置

# 读取当前配置
CONFIG_FILE="/etc/postfix/main.cf"

# 备份
cp $CONFIG_FILE ${CONFIG_FILE}.backup_sasl

# 移除旧的SASL配置（如果有）
sed -i '/^smtpd_sasl_auth_enable/d' $CONFIG_FILE
sed -i '/^smtpd_sasl_type/d' $CONFIG_FILE
sed -i '/^smtpd_sasl_path/d' $CONFIG_FILE
sed -i '/^smtpd_sasl_security_options/d' $CONFIG_FILE
sed -i '/^smtpd_sasl_tls_security_options/d' $CONFIG_FILE

# 在适当位置添加新的SASL配置（在home_mailbox之后）
sed -i '/^home_mailbox = Maildir/a \
\
# SMTP Authentication (SASL)\
smtpd_sasl_auth_enable = yes\
smtpd_sasl_type = dovecot\
smtpd_sasl_path = private/auth\
smtpd_sasl_security_options = noanonymous, noplaintext\
smtpd_sasl_tls_security_options = noanonymous\
smtpd_recipient_restrictions = permit_sasl_authenticated, permit_mynetworks, reject_unauth_destination\
broken_sasl_auth_clients = yes' $CONFIG_FILE

echo "✅ Postfix SASL配置已完成"
