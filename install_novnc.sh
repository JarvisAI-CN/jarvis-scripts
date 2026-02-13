#!/bin/bash
# noVNC安装脚本
# 通过浏览器访问VNC桌面

echo "=== 安装noVNC ==="

# 安装依赖
dnf install -y git novnc websockify

# 或从GitHub安装最新版
cd /opt
git clone https://github.com/novnc/noVNC.git
cd noVNC
git clone https://github.com/novnc/websockify websockify

# 启动noVNC
# ./utils/novnc_proxy --vnc localhost:5901 --listen 6080

echo "=== noVNC安装完成 ==="
echo "访问: http://82.157.20.7:6080/vnc.html"
echo "需要启动: /opt/noVNC/utils/novnc_proxy --vnc localhost:5901 --listen 6080"
