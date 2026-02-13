#!/bin/bash
# 邮件工具测试脚本

echo "📧 贾维斯的邮件工具 - 测试"
echo "================================"

# 创建必要的目录
mkdir -p /home/ubuntu/.openclaw/workspace/logs

# 设置权限
chmod +x /home/ubuntu/.openclaw/workspace/scripts/email_tool.py
chmod +x /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py

echo ""
echo "✅ 脚本已创建并设置权限"
echo ""
echo "📋 可用功能:"
echo ""
echo "1. 检查邮箱统计:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py stats"
echo ""
echo "2. 列出文件夹:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py list"
echo ""
echo "3. 查看未读邮件:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py unread --limit 5"
echo ""
echo "4. 查看最近邮件:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py recent --limit 5"
echo ""
echo "5. 搜索邮件:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py search --search '关键词'"
echo ""
echo "6. 发送邮件:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_tool.py send \\"
echo "     --to 'recipient@example.com' \\"
echo "     --subject '测试邮件' \\"
echo "     --body '这是一封测试邮件'"
echo ""
echo "7. 邮件监控:"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py"
echo "   python3 /home/ubuntu/.openclaw/workspace/scripts/email_monitor.py --notify"
echo ""
echo "📊 邮箱配置:"
echo "   邮箱: jarvis-cn-ai@outlook.com"
echo "   IMAP: outlook.office365.com:993"
echo "   SMTP: smtp.office365.com:587"
echo ""
echo "📝 日志位置:"
echo "   /home/ubuntu/.openclaw/workspace/logs/email_monitor.log"
echo ""
echo "🎯 下一步:"
echo "   运行测试命令查看功能是否正常"
