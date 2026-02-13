#!/bin/bash
# 网址导航网站 - 每日链接检查 Cron 任务
# 每天凌晨 02:00 执行

cd /home/ubuntu/.openclaw/workspace/PARA/Projects/网址导航网站维护项目/这个项目的文件/脚本/
python3 website_maintenance_monitor.py >> /home/ubuntu/.openclaw/workspace/PARA/Projects/网址导航网站维护项目/这个项目的文件/日志/maintenance_cron.log 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 链接检查任务完成" >> /home/ubuntu/.openclaw/workspace/PARA/Projects/网址导航网站维护项目/这个项目的文件/日志/maintenance_cron.log
