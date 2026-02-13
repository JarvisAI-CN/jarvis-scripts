#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贾维斯的邮件工具
支持Outlook邮箱的收发、搜索、分类等功能
"""

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

# 邮箱配置
EMAIL_CONFIG = {
    "imap": {
        "host": "imap.email.cn",
        "port": 993,
        "user": "jarvis.openclaw@email.cn",
        "password": "wjhwJyeGudeCRk2e"  # 应用专用密码
    },
    "smtp": {
        "host": "smtp.email.cn",
        "port": 465,
        "user": "jarvis.openclaw@email.cn",
        "password": "wjhwJyeGudeCRk2e"  # 应用专用密码
    }
}

class OutlookEmail:
    """Outlook邮箱操作类"""

    def __init__(self):
        self.imap = None
        self.smtp = None

    def connect_imap(self):
        """连接IMAP服务器"""
        try:
            self.imap = imaplib.IMAP4_SSL(EMAIL_CONFIG["imap"]["host"], EMAIL_CONFIG["imap"]["port"])
            self.imap.login(EMAIL_CONFIG["imap"]["user"], EMAIL_CONFIG["imap"]["password"])
            return True
        except Exception as e:
            print(f"❌ IMAP连接失败: {e}")
            return False

    def connect_smtp(self):
        """连接SMTP服务器"""
        try:
            # Use SSL directly for port 465
            self.smtp = smtplib.SMTP_SSL(EMAIL_CONFIG["smtp"]["host"], EMAIL_CONFIG["smtp"]["port"])
            self.smtp.login(EMAIL_CONFIG["smtp"]["user"], EMAIL_CONFIG["smtp"]["password"])
            return True
        except Exception as e:
            print(f"❌ SMTP连接失败: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
            self.imap = None
        if self.smtp:
            try:
                self.smtp.quit()
            except:
                pass
            self.smtp = None

    def decode_header(self, header):
        """解码邮件头"""
        if not header:
            return ""
        
        decoded = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                try:
                    decoded.append(part.decode(encoding or 'utf-8', errors='ignore'))
                except:
                    decoded.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded.append(str(part))
        return ''.join(decoded)

    def parse_email(self, msg_data):
        """解析邮件内容"""
        raw_email = msg_data[1]
        msg = email.message_from_bytes(raw_email)
        
        # 解析邮件头
        subject = self.decode_header(msg.get("Subject", ""))
        from_addr = self.decode_header(msg.get("From", ""))
        to_addr = self.decode_header(msg.get("To", ""))
        date = msg.get("Date", "")
        msg_id = msg.get("Message-ID", "")
        
        # 解析邮件正文
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(part.get_payload())
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        
        return {
            "subject": subject,
            "from": from_addr,
            "to": to_addr,
            "date": date,
            "message_id": msg_id,
            "body": body
        }

    def list_folders(self, stay_connected=False):
        """列出所有文件夹"""
        if not self.imap and not self.connect_imap():
            return []
        
        try:
            folders = []
            result, data = self.imap.list()
            for item in data:
                folder_str = item.decode('utf-8')
                # 提取文件夹名称
                match = re.search(r'"([^"]+)"$', folder_str)
                if match:
                    folders.append(match.group(1))
            return folders
        except Exception as e:
            print(f"❌ 列出文件夹失败: {e}")
            return []
        finally:
            if not stay_connected:
                self.disconnect()

    def get_unread_emails(self, folder="INBOX", limit=10):
        """获取未读邮件"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap.select(f'"{folder}"')
            result, data = self.imap.search(None, "UNSEEN")
            
            if result != "OK":
                return []
            
            email_ids = data[0].split()
            # 限制数量
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for eid in email_ids:
                result, data = self.imap.fetch(eid, '(RFC822)')
                if result == "OK":
                    email_data = self.parse_email(data[0])
                    email_data["id"] = eid.decode()
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"❌ 获取未读邮件失败: {e}")
            return []
        finally:
            self.disconnect()

    def get_recent_emails(self, folder="INBOX", limit=10):
        """获取最近的邮件"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap.select(f'"{folder}"')
            result, data = self.imap.search(None, "ALL")
            
            if result != "OK":
                return []
            
            email_ids = data[0].split()
            # 获取最新的几封
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for eid in reversed(email_ids):
                result, data = self.imap.fetch(eid, '(RFC822)')
                if result == "OK":
                    email_data = self.parse_email(data[0])
                    email_data["id"] = eid.decode()
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"❌ 获取最近邮件失败: {e}")
            return []
        finally:
            self.disconnect()

    def search_emails(self, criteria, folder="INBOX"):
        """搜索邮件"""
        if not self.connect_imap():
            return []
        
        try:
            self.imap.select(f'"{folder}"')
            result, data = self.imap.search(None, criteria)
            
            if result != "OK":
                return []
            
            email_ids = data[0].split()
            emails = []
            for eid in email_ids:
                result, data = self.imap.fetch(eid, '(RFC822)')
                if result == "OK":
                    email_data = self.parse_email(data[0])
                    email_data["id"] = eid.decode()
                    emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"❌ 搜索邮件失败: {e}")
            return []
        finally:
            self.disconnect()

    def send_email(self, to_addr, subject, body, html=False):
        """发送邮件"""
        if not self.connect_smtp():
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = EMAIL_CONFIG["smtp"]["user"]
            msg['To'] = to_addr
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            self.smtp.send_message(msg)
            print(f"✅ 邮件已发送到: {to_addr}")
            return True
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            return False
        finally:
            self.disconnect()

    def mark_as_read(self, email_id, folder="INBOX"):
        """标记邮件为已读"""
        if not self.connect_imap():
            return False
        
        try:
            self.imap.select(f'"{folder}"')
            self.imap.store(email_id, '+FLAGS', '\\Seen')
            return True
        except Exception as e:
            print(f"❌ 标记已读失败: {e}")
            return False
        finally:
            self.disconnect()

    def get_email_stats(self):
        """获取邮箱统计"""
        if not self.connect_imap():
            return {}
        
        try:
            stats = {}
            folders = self.list_folders(stay_connected=True)
            
            for folder in folders:
                try:
                    self.imap.select(f'"{folder}"')
                    result, data = self.imap.search(None, "ALL")
                    total = len(data[0].split())
                    
                    result, data = self.imap.search(None, "UNSEEN")
                    unread = len(data[0].split())
                    
                    stats[folder] = {
                        "total": total,
                        "unread": unread
                    }
                except Exception as e:
                    print(f"⚠️ 处理文件夹 {folder} 失败: {e}")
            
            return stats
        except Exception as e:
            print(f"❌ 获取统计失败: {e}")
            return {}
        finally:
            self.disconnect()


def main():
    """命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='贾维斯的邮件工具')
    parser.add_argument('action', choices=['list', 'unread', 'recent', 'search', 'send', 'stats'],
                       help='操作类型')
    parser.add_argument('--limit', type=int, default=10, help='邮件数量限制')
    parser.add_argument('--folder', default='INBOX', help='文件夹名称')
    parser.add_argument('--to', help='收件人地址')
    parser.add_argument('--subject', help='邮件主题')
    parser.add_argument('--body', help='邮件正文')
    parser.add_argument('--html', action='store_true', help='HTML格式')
    parser.add_argument('--search', help='搜索关键词')
    
    args = parser.parse_args()
    
    email_tool = OutlookEmail()
    
    if args.action == 'list':
        folders = email_tool.list_folders()
        print("📁 文件夹列表:")
        for folder in folders:
            print(f"  - {folder}")
    
    elif args.action == 'unread':
        emails = email_tool.get_unread_emails(args.folder, args.limit)
        print(f"📬 未读邮件 ({args.folder}):")
        for i, email_data in enumerate(emails, 1):
            print(f"\n{i}. {email_data['subject']}")
            print(f"   发件人: {email_data['from']}")
            print(f"   日期: {email_data['date']}")
            print(f"   正文预览: {email_data['body'][:100]}...")
    
    elif args.action == 'recent':
        emails = email_tool.get_recent_emails(args.folder, args.limit)
        print(f"📬 最近邮件 ({args.folder}):")
        for i, email_data in enumerate(emails, 1):
            print(f"\n{i}. {email_data['subject']}")
            print(f"   发件人: {email_data['from']}")
            print(f"   日期: {email_data['date']}")
    
    elif args.action == 'search':
        if not args.search:
            print("❌ 请提供搜索关键词 --search")
            return
        criteria = f'SUBJECT "{args.search}"'
        emails = email_tool.search_emails(criteria, args.folder)
        print(f"🔍 搜索结果 ({args.search}):")
        for i, email_data in enumerate(emails, 1):
            print(f"\n{i}. {email_data['subject']}")
            print(f"   发件人: {email_data['from']}")
            print(f"   日期: {email_data['date']}")
    
    elif args.action == 'send':
        if not args.to or not args.subject or not args.body:
            print("❌ 发送邮件需要 --to, --subject, --body 参数")
            return
        email_tool.send_email(args.to, args.subject, args.body, args.html)
    
    elif args.action == 'stats':
        stats = email_tool.get_email_stats()
        print("📊 邮箱统计:")
        for folder, data in stats.items():
            print(f"\n📁 {folder}:")
            print(f"   总计: {data['total']} 封")
            print(f"   未读: {data['unread']} 封")


if __name__ == '__main__':
    main()
