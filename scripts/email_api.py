#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的邮件API wrapper for OpenClaw
让贾维斯可以轻松调用邮件功能
"""

import subprocess
import json
import os

class EmailAPI:
    """邮件API封装"""

    def __init__(self):
        self.script_dir = "/home/ubuntu/.openclaw/workspace/scripts"
        self.email_tool = os.path.join(self.script_dir, "email_tool.py")
        self.monitor_tool = os.path.join(self.script_dir, "email_monitor.py")

    def check_new_emails(self):
        """检查新邮件"""
        result = subprocess.run(
            ['python3', self.monitor_tool],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    def get_stats(self):
        """获取邮箱统计"""
        result = subprocess.run(
            ['python3', self.email_tool, 'stats'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    def get_unread(self, limit=5):
        """获取未读邮件"""
        result = subprocess.run(
            ['python3', self.email_tool, 'unread', '--limit', str(limit)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    def get_recent(self, limit=10):
        """获取最近邮件"""
        result = subprocess.run(
            ['python3', self.email_tool, 'recent', '--limit', str(limit)],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    def send_email(self, to_addr, subject, body, html=False):
        """发送邮件"""
        cmd = [
            'python3', self.email_tool, 'send',
            '--to', to_addr,
            '--subject', subject,
            '--body', body
        ]
        if html:
            cmd.append('--html')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }

    def search(self, keyword):
        """搜索邮件"""
        result = subprocess.run(
            ['python3', self.email_tool, 'search', '--search', keyword],
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.stderr else None
        }


# 便捷函数
def quick_check():
    """快速检查新邮件"""
    api = EmailAPI()
    result = api.check_new_emails()
    if result["success"]:
        print(result["output"])
        return True
    else:
        print(f"❌ 错误: {result['error']}")
        return False

def quick_stats():
    """快速查看统计"""
    api = EmailAPI()
    result = api.get_stats()
    if result["success"]:
        print(result["output"])
        return True
    else:
        print(f"❌ 错误: {result['error']}")
        return False

def quick_send(to_addr, subject, body):
    """快速发送邮件"""
    api = EmailAPI()
    result = api.send_email(to_addr, subject, body)
    if result["success"]:
        print(result["output"])
        return True
    else:
        print(f"❌ 错误: {result['error']}")
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python email_api.py [check|stats|unread|recent|send]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'check':
        quick_check()
    elif command == 'stats':
        quick_stats()
    elif command == 'unread':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        api = EmailAPI()
        result = api.get_unread(limit)
        if result["success"]:
            print(result["output"])
        else:
            print(f"❌ 错误: {result['error']}")
    elif command == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        api = EmailAPI()
        result = api.get_recent(limit)
        if result["success"]:
            print(result["output"])
        else:
            print(f"❌ 错误: {result['error']}")
    elif command == 'send':
        if len(sys.argv) < 5:
            print("用法: python email_api.py send <to> <subject> <body>")
            sys.exit(1)
        to_addr = sys.argv[2]
        subject = sys.argv[3]
        body = sys.argv[4]
        quick_send(to_addr, subject, body)
    else:
        print(f"❌ 未知命令: {command}")
        sys.exit(1)
