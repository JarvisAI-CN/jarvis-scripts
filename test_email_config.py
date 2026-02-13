#!/usr/bin/env python3
import imaplib
import smtplib

# 测试配置
configs = [
    {
        "name": "应用专用密码",
        "password": "cqgsgyomulsfjmfs"
    },
    {
        "name": "账户密码",
        "password": "Jarvis@2026AI#Helper"
    }
]

host = "outlook.office365.com"
user = "jarvis-cn-ai@outlook.com"

print("🧪 测试Outlook邮箱连接...\n")

for config in configs:
    print(f"📋 测试: {config['name']}")
    pwd = config['password']

    # 测试IMAP
    try:
        imap = imaplib.IMAP4_SSL(host, 993)
        imap.login(user, pwd)
        imap.select('INBOX')
        status, messages = imap.search(None, 'UNSEEN')
        print(f"  ✅ IMAP连接成功！未读邮件: {len(messages[0].split()) if messages[0] else 0} 封")
        imap.close()
        imap.logout()
    except Exception as e:
        print(f"  ❌ IMAP连接失败: {e}")

    # 测试SMTP
    try:
        smtp = smtplib.SMTP(host, 587)
        smtp.starttls()
        smtp.login(user, pwd)
        print(f"  ✅ SMTP连接成功！")
        smtp.quit()
    except Exception as e:
        print(f"  ❌ SMTP连接失败: {e}")

    print()
