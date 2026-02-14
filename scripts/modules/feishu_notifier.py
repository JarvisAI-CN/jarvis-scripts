#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书通知模块 (Feishu Notifier)
通过 OpenClaw CLI 发送通知
"""

import subprocess
import json
import logging
import sys

# 默认配置
DEFAULT_CHANNEL = "feishu"
DEFAULT_TARGET = "ou_5f1c95e17c1b9d8f679c500e8864999f"

class FeishuNotifier:
    def __init__(self, channel=DEFAULT_CHANNEL, target=DEFAULT_TARGET):
        self.channel = channel
        self.target = target

    def send_text(self, message):
        """发送纯文本消息"""
        try:
            # 构建命令
            cmd = [
                "openclaw", "message", "send",
                "--channel", self.channel,
                "--account", "main",
                "--target", self.target,
                "--message", message
            ]
            
            # 执行命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"Feishu notification failed: {e.stderr or e.stdout}"
            print(error_msg, file=sys.stderr)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error in FeishuNotifier: {str(e)}"
            print(error_msg, file=sys.stderr)
            return False, error_msg

    def send_task_notification(self, task_id, title, status, details=None):
        """发送结构化的任务通知"""
        emoji = "🚀" if status == "START" else "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "ℹ️"
        msg = f"{emoji} [自主维护] {status}\n任务: {task_id}\n标题: {title}"
        if details:
            msg += f"\n详情: {details}"
        
        return self.send_text(msg)

if __name__ == "__main__":
    # 简单测试
    notifier = FeishuNotifier()
    if len(sys.argv) > 1:
        notifier.send_text(" ".join(sys.argv[1:]))
    else:
        notifier.send_text("🔔 飞书通知模块已上线")
