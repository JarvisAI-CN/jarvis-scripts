#!/bin/bash
# WebDAV 恢复脚本
# 用途：在 WebDAV 服务器恢复后，快速重建挂载和软链接
# 作者：Jarvis (贾维斯)
# 创建时间：2026-03-26 04:40

set -e

echo "==================================="
echo "WebDAV 恢复脚本"
echo "==================================="
echo ""

# 1. 检查 WebDAV 服务器是否可访问
echo "1️⃣  检查 WebDAV 服务器连接..."
if timeout 5 curl -I --connect-timeout 3 http://fsnas.top:19798/dav >/dev/null 2>&1; then
    echo "✅ WebDAV 服务器可访问"
else
    echo "❌ WebDAV 服务器无法连接"
    echo "请等待服务器恢复后再运行此脚本"
    exit 1
fi

# 2. 创建挂载点（如果不存在）
echo ""
echo "2️⃣  创建挂载点..."
sudo mkdir -p /mnt/webdav-fsnas
echo "✅ 挂载点已准备"

# 3. 挂载 WebDAV
echo ""
echo "3️⃣  挂载 WebDAV..."
mount /mnt/webdav-fsnas 2>&1
echo "✅ WebDAV 已挂载"

# 4. 验证挂载
echo ""
echo "4️⃣  验证挂载状态..."
if mount | grep -q webdav-fsnas; then
    echo "✅ WebDAV 挂载成功"
else
    echo "❌ WebDAV 挂载失败"
    exit 1
fi

# 5. 创建软链接
echo ""
echo "5️⃣  创建软链接..."
if [ -L /home/ubuntu/123pan ]; then
    echo "⚠️  软链接已存在，删除旧链接..."
    rm /home/ubuntu/123pan
fi

ln -s /mnt/webdav-fsnas /home/ubuntu/123pan
echo "✅ 软链接已创建: /home/ubuntu/123pan -> /mnt/webdav-fsnas"

# 6. 验证访问
echo ""
echo "6️⃣  验证访问..."
if ls /home/ubuntu/123pan >/dev/null 2>&1; then
    echo "✅ 可以访问 123盘"
else
    echo "⚠️  无法访问 123盘（可能需要等待）"
fi

# 7. 检查备份目录
echo ""
echo "7️⃣  检查备份目录..."
if [ -d "/home/ubuntu/123pan/备份" ]; then
    echo "✅ 备份目录存在"
else
    echo "⚠️  备份目录不存在，可能需要创建"
    read -p "是否创建备份目录？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "/home/ubuntu/123pan/备份"
        echo "✅ 备份目录已创建"
    fi
fi

# 8. 测试备份脚本
echo ""
echo "8️⃣  测试备份脚本..."
if bash /home/ubuntu/.openclaw/workspace/backup.sh --test 2>&1; then
    echo "✅ 备份脚本测试成功"
else
    echo "⚠️  备份脚本测试失败，请检查"
fi

echo ""
echo "==================================="
echo "WebDAV 恢复完成！"
echo "==================================="
echo ""
echo "📊 当前状态："
mount | grep webdav-fsnas
ls -la /home/ubuntu/ | grep 123pan
echo ""
echo "✅ 系统已恢复正常"
