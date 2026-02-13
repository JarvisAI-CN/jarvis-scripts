#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贾维斯 - SMTP 密码更新工具
用于更新 Outlook SMTP 应用专用密码
"""

import sys
import os

def update_smtp_password(new_password):
    """更新 SMTP 密码"""

    # 文件路径
    email_tool_path = "/home/ubuntu/.openclaw/workspace/scripts/email_tool.py"
    passwords_path = "/home/ubuntu/.openclaw/workspace/PASSWORDS.md"

    # 1. 更新 email_tool.py
    try:
        with open(email_tool_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 替换密码占位符
        content = content.replace(
            '"password": "YOUR_APP_PASSWORD_HERE"',
            f'"password": "{new_password}"'
        )

        with open(email_tool_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ email_tool.py 已更新")

    except Exception as e:
        print(f"❌ 更新 email_tool.py 失败: {e}")
        return False

    # 2. 更新 PASSWORDS.md
    try:
        with open(passwords_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 添加应用专用密码条目
        app_password_section = f"""
### Outlook 应用专用密码 ⭐ 新增 2026-02-09
- **用途**: SMTP 认证
- **密码**: {new_password}
- **创建时间**: 2026-02-09
- **状态**: ✅ 已配置
- **重要**: 此密码仅用于 SMTP，IMAP 仍使用普通密码

---

"""

        # 在"Outlook 个人邮箱"部分之后插入
        outlook_section = "### Outlook 个人邮箱 ⭐ 新增 2026-02-08"
        if outlook_section in content:
            # 找到 Outlook 部分的结束位置（下一个 ### 或 ---）
            lines = content.split('\n')
            new_lines = []
            inserted = False

            for i, line in enumerate(lines):
                new_lines.append(line)
                # 在 Outlook 部分的 "---" 后插入
                if not inserted and line.strip().startswith('---'):
                    # 检查前面是否是 Outlook 部分
                    if i > 10 and '### Outlook 个人邮箱' in '\n'.join(lines[max(0, i-20):i]):
                        new_lines.append(app_password_section.strip())
                        inserted = True

            content = '\n'.join(new_lines)

        with open(passwords_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ PASSWORDS.md 已更新")

    except Exception as e:
        print(f"❌ 更新 PASSWORDS.md 失败: {e}")
        return False

    # 3. 测试 SMTP 连接
    print("\n🧪 测试 SMTP 连接...")
    try:
        import smtplib
        from email.mime.text import MIMEText

        # 读取配置
        sys.path.insert(0, os.path.dirname(email_tool_path))
        from email_tool import EMAIL_CONFIG

        smtp_config = EMAIL_CONFIG["smtp"]

        # 连接测试
        server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
        server.starttls()
        server.login(smtp_config["user"], smtp_config["password"])
        server.quit()

        print("✅ SMTP 连接测试成功！")
        print("\n🎉 Outlook SMTP 配置完成！邮件发送功能已恢复。")
        return True

    except Exception as e:
        print(f"❌ SMTP 测试失败: {e}")
        print("\n请检查：")
        print("1. 应用专用密码是否正确")
        print("2. 密码是否已正确复制（无多余空格）")
        print("3. 账户是否启用了 SMTP 服务")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 update_smtp_password.py '新密码'")
        print("示例: python3 update_smtp_password.py 'abcd1234efgh5678'")
        sys.exit(1)

    new_password = sys.argv[1].strip()

    if len(new_password) != 16:
        print("⚠️ 警告: 应用专用密码应该是16位字符")
        confirm = input("继续吗？(y/n): ")
        if confirm.lower() != 'y':
            sys.exit(1)

    print(f"\n🔧 更新 SMTP 密码...")
    print(f"新密码: {'*' * 12}{new_password[-4:]}")

    if update_smtp_password(new_password):
        sys.exit(0)
    else:
        sys.exit(1)
