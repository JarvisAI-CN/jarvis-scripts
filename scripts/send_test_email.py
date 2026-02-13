#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送测试邮件
"""

import sys
sys.path.append('/home/ubuntu/.openclaw/workspace/scripts')

from email_tool import OutlookEmail

def send_test_email():
    """发送测试邮件"""
    email_tool = OutlookEmail()
    
    to_addr = "mipjc@111.com"
    subject = "贾维斯的邮件系统测试 ✅"
    body = """你好！

这是贾维斯发送的测试邮件，恭喜Outlook邮箱配置成功！

📧 **邮箱信息**：
- 发件人：jarvis-cn-ai@outlook.com
- 收件人：mipjc@111.com
- 发送时间：2026-02-08 22:46

🤖 **关于贾维斯**：
- 我是OpenClaw驱动的AI助手
- 刚刚配置了Outlook邮箱功能
- 支持邮件收发、监控、搜索等功能

✨ **功能特性**：
- ✅ IMAP收邮件
- ✅ SMTP发邮件
- ✅ 智能邮件监控
- ✅ 邮件搜索和分类
- ✅ 定时检查新邮件

如果你收到这封邮件，说明邮件系统工作正常！

期待你的回复 📨

---
贾维斯 ⚡
OpenClaw AI助手
2026-02-08"""

    print(f"📧 发送测试邮件到: {to_addr}")
    success = email_tool.send_email(to_addr, subject, body)
    
    if success:
        print("✅ 测试邮件发送成功！")
        return 0
    else:
        print("❌ 测试邮件发送失败！")
        return 1

if __name__ == '__main__':
    exit(send_test_email())
