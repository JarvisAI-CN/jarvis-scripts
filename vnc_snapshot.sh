#!/bin/bash
# 使用ffmpeg从VNC获取截图

echo "正在从VNC获取截图..."

# ffmpeg从VNC抓取一帧
ffmpeg -f x11grab -r 1 -s 1920x1080 -i :1 -frames:v 1 /tmp/vnc_snapshot.jpg -y 2>&1 | tail -5

if [ -f /tmp/vnc_snapshot.jpg ]; then
    echo "✅ 截图成功: /tmp/vnc_snapshot.jpg"
    ls -la /tmp/vnc_snapshot.jpg
else
    echo "❌ 截图失败"
fi
