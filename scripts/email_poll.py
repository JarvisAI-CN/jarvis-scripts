#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件轮询脚本 - 用于cron定时检查新邮件（仅转发邮件）
"""

import sys
import imaplib
import email
from email.header import decode_header as email_decode_header
import re
from datetime import datetime, timedelta

# 邮箱配置
EMAIL_CONFIG = {
    "host": "imap.email.cn",
    "port": 993,
    "user": "jarvis.openclaw@email.cn",
    "password": "wjhwJyeGudeCRk2e",
}

# 转发邮件关键词（用于识别转发邮件）
FORWARD_KEYWORDS = [
    "转发", "FW:", "Fw:", "fw:", "Fwd:", "fwd:",
    "Forward", "FORWARD",
]


def decode_header(header):
    """解码邮件头"""
    if not header:
        return ""
    decoded = []
    for part, encoding in email_decode_header(header):
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(encoding or "utf-8", errors="ignore"))
            except Exception:
                decoded.append(part.decode("utf-8", errors="ignore"))
        else:
            decoded.append(str(part))
    return "".join(decoded)


def is_forward_email(subject, body, from_addr):
    """判断是否为转发邮件"""
    subject_lower = subject.lower() if subject else ""
    body_lower = body.lower() if body else ""

    # 检查主题
    for keyword in FORWARD_KEYWORDS:
        if keyword.lower() in subject_lower:
            return True

    # 检查发件人（排除系统邮件）
    if from_addr and any(x in from_addr.lower() for x in ["noreply", "no-reply", "notification"]):
        return False

    # 检查正文中的转发标识
    if body and any(x in body for x in ["-----Original Message-----", "From:", "发件人:", " forwarded", " 转发"]):
        return True

    return False


def parse_email(msg_data):
    """解析邮件内容"""
    raw_email = msg_data[1]
    msg = email.message_from_bytes(raw_email)

    subject = decode_header(msg.get("Subject", ""))
    from_addr = decode_header(msg.get("From", ""))
    to_addr = decode_header(msg.get("To", ""))
    date = msg.get("Date", "")
    msg_id = msg.get("Message-ID", "")

    # 解析邮件正文
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                except Exception:
                    body = str(part.get_payload())
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception:
            body = str(msg.get_payload())

    return {
        "subject": subject,
        "from": from_addr,
        "to": to_addr,
        "date": date,
        "message_id": msg_id,
        "body": body,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="邮件轮询脚本")
    parser.add_argument("--limit", type=int, default=10, help="检查的邮件数量")
    args = parser.parse_args()

    try:
        # 连接IMAP服务器
        imap = imaplib.IMAP4_SSL(EMAIL_CONFIG["host"], EMAIL_CONFIG["port"])
        imap.login(EMAIL_CONFIG["user"], EMAIL_CONFIG["password"])
        imap.select('"INBOX"')

        # 搜索未读邮件
        result, data = imap.search(None, "UNSEEN")
        if result != "OK" or not data[0]:
            imap.close()
            imap.logout()
            return  # 没有新邮件，不输出

        email_ids = data[0].split()
        # 限制数量
        email_ids = email_ids[-args.limit:] if len(email_ids) > args.limit else email_ids

        forward_emails = []
        for eid in email_ids:
            result, data = imap.fetch(eid, "(RFC822)")
            if result == "OK":
                email_data = parse_email(data[0])
                # 检查是否为转发邮件
                if is_forward_email(email_data["subject"], email_data["body"], email_data["from"]):
                    forward_emails.append(email_data)

        imap.close()
        imap.logout()

        # 如果没有转发邮件，不输出
        if not forward_emails:
            return

        # 输出转发邮件信息
        for i, email_data in enumerate(forward_emails, 1):
            print(f"\n【转发邮件 #{i}】")
            print(f"📧 主题: {email_data['subject']}")
            print(f"👤 发件人: {email_data['from']}")
            print(f"📅 时间: {email_data['date']}")
            print(f"📄 正文预览:")
            # 只显示前300字符
            preview = email_data['body'][:300].strip()
            if len(email_data['body']) > 300:
                preview += "..."
            print(preview)
            print("-" * 60)

    except Exception as e:
        # 错误也输出，方便调试
        print(f"❌ 邮件检查失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
