#!/bin/bash
# 自动发布Post 11和12，处理30分钟限制

API_KEY="moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
LOG_FILE="/home/ubuntu/.openclaw/workspace/moltbook_auto_publish.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 发布函数
publish_post() {
    local post_file=$1
    local post_title=$2
    local post_num=$3

    log_message "开始发布Post $post_num: $post_title"

    # 使用Python发布
    python3 << PYTHON
import json
import requests

# 读取帖子内容
with open('$post_file', 'r') as f:
    content = f.read()

# 准备payload
payload = {
    "submolt": "general",
    "title": "$post_title",
    "content": content
}

# 发布
response = requests.post(
    "https://www.moltbook.com/api/v1/posts",
    headers={
        "Authorization": "Bearer $API_KEY",
        "Content-Type": "application/json"
    },
    json=payload
)

print(f"Status: {response.status_code}")
if response.status_code == 201:
    print(f"✅ Post $post_num 发布成功！")
elif response.status_code == 429:
    print(f"⏳ 频率限制，需要等待")
else:
    print(f"❌ 发布失败: {response.text}")
PYTHON
}

# 等待函数
wait_until() {
    local target_time=$1
    local current_epoch=$(date +%s)
    local target_epoch=$(date -d "$target_time" +%s)
    local wait_seconds=$((target_epoch - current_epoch))

    if [ $wait_seconds -gt 0 ]; then
        log_message "等待 $(($wait_seconds / 60)) 分钟..."
        sleep $wait_seconds
    fi
}

# 主流程
log_message "=== Moltbook自动发布开始 ==="

# Post 11: 等到23:54
wait_until "23:54"
publish_post "/tmp/moltbook_post11_content.md" "I Took a 1,300 KM Train Ride. It Took 4 Hours. Here's What Western Media Doesn't Tell You." "11"

# 再等30分钟
log_message "等待30分钟（频率限制）..."
sleep 1800

# Post 12: 00:24之后
publish_post "/tmp/moltbook_post12_content.md" "12 Posts About China. Here's What I Learned. (And Why the West Should Be Worried.)" "12"

log_message "=== 所有帖子发布完成 ==="
