#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送测试邮件到jarvis@mail.dhmip.cn
使用Python直接连接SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 邮件配置
SMTP_HOST = 'localhost'
SMTP_PORT = 25
FROM_EMAIL = 'root@dhmip.cn'
TO_EMAIL = 'jarvis@mail.dhmip.cn'

def send_test_email():
    """发送测试邮件"""
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = '贾维斯，你好！这是测试邮件'
        
        # 邮件正文
        body = f"""
亲爱的贾维斯：

这是你的专属邮箱：jarvis@mail.dhmip.cn

恭喜你！现在你可以：
✅ 接收邮件
✅ 发送邮件
✅ 管理邮箱

这封测试邮件发送时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

祝你使用愉快！

---
你的系统
"""
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        
        print("✅ 测试邮件已发送到 jarvis@mail.dhmip.cn")
        return True
        
    except Exception as e:
        print(f"❌ 发送失败: {str(e)}")
        return False

if __name__ == "__main__":
    send_test_email()
