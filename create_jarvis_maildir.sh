# jarvis用户Maildir创建脚本

#!/bin/bash

# 创建Maildir结构
mkdir -p /home/jarvis/Maildir/{cur,new,tmp}

# 设置权限
chmod -R 700 /home/jarvis/Maildir
chown -R jarvis:jarvis /home/jarvis/Maildir

# 验证
ls -la /home/jarvis/Maildir/

echo "✅ Maildir创建完成"
