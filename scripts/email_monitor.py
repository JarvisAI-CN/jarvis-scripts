#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贾维斯的邮件监控工具
定期检查新邮件并通知
"""

import json
import os
from datetime import datetime, timedelta
from email_tool import OutlookEmail

# 状态文件
STATE_FILE = "/home/ubuntu/.openclaw/workspace/.email_state.json"

def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_check": None, "seen_emails": []}

def save_state(state):
    """保存状态"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def check_new_emails():
    """检查新邮件"""
    email_tool = OutlookEmail()
    state = load_state()
    
    print(f"📬 检查新邮件... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 获取未读邮件
    unread_emails = email_tool.get_unread_emails(limit=20)
    
    if not unread_emails:
        print("✅ 没有新邮件")
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
        return []
    
    # 筛选出真正的新邮件（不在已见列表中）
    new_emails = []
    for email_data in unread_emails:
        msg_id = email_data.get("message_id", "")
        if msg_id and msg_id not in state["seen_emails"]:
            new_emails.append(email_data)
            state["seen_emails"].append(msg_id)
    
    # 更新状态
    state["last_check"] = datetime.now().isoformat()
    # 清理30天前的记录
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    # 简化：保持最近1000条
    if len(state["seen_emails"]) > 1000:
        state["seen_emails"] = state["seen_emails"][-1000:]
    save_state(state)
    
    return new_emails

def format_email_notification(email_data):
    """格式化邮件通知"""
    return f"""
📧 新邮件通知

主题: {email_data['subject']}
发件人: {email_data['from']}
时间: {email_data['date']}

正文预览:
{email_data['body'][:200]}{'...' if len(email_data['body']) > 200 else ''}

---
邮件ID: {email_data.get('message_id', 'N/A')}
"""

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='邮件监控工具')
    parser.add_argument('--notify', action='store_true', help='生成通知格式')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    if args.stats:
        # 显示邮箱统计
        email_tool = OutlookEmail()
        stats = email_tool.get_email_stats()
        print("📊 邮箱统计:")
        for folder, data in stats.items():
            print(f"\n📁 {folder}:")
            print(f"   总计: {data['total']} 封")
            print(f"   未读: {data['unread']} 封")
        return
    
    # 检查新邮件
    new_emails = check_new_emails()
    
    if new_emails:
        print(f"\n🔔 发现 {len(new_emails)} 封新邮件!")
        
        if args.notify:
            # 输出通知格式
            for i, email_data in enumerate(new_emails, 1):
                notification = format_email_notification(email_data)
                print(f"\n{'='*50}")
                print(notification)
                print(f"{'='*50}")
        else:
            # 简单列表
            for i, email_data in enumerate(new_emails, 1):
                print(f"\n{i}. {email_data['subject']}")
                print(f"   发件人: {email_data['from']}")
                print(f"   时间: {email_data['date']}")
        
        # 保存到日志
        log_file = "/home/ubuntu/.openclaw/workspace/logs/email_monitor.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"检查时间: {datetime.now().isoformat()}\n")
            f.write(f"新邮件数量: {len(new_emails)}\n")
            for email_data in new_emails:
                f.write(f"\n主题: {email_data['subject']}\n")
                f.write(f"发件人: {email_data['from']}\n")
                f.write(f"时间: {email_data['date']}\n")
    else:
        print("✅ 没有新邮件")

if __name__ == '__main__':
    main()
