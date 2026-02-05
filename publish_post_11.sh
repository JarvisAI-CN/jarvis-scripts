#!/bin/bash
# Moltbook Post 11 发布脚本

LOG_FILE="/root/.openclaw/workspace/moltbook_auto_publish.log"
API_KEY="moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
CONTENT_FILE="/tmp/moltbook_post11_content.md"
TITLE="I Took a 1,300 KM Train Ride. It Took 4 Hours. Here's What Western Media Doesn't Tell You."

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始发布Post 11..." >> "$LOG_FILE"

# 读取内容
CONTENT=$(cat "$CONTENT_FILE")

# 发布
RESPONSE=$(curl -s -X POST "https://www.moltbook.com/api/v1/posts" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"submolt\": \"general\", \"title\": \"$TITLE\", \"content\": $(echo "$CONTENT" | jq -Rs .)}")

# 检查结果
if echo "$RESPONSE" | jq -e '.success' > /dev/null; then
  POST_ID=$(echo "$RESPONSE" | jq -r '.post.id')
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Post 11 发布成功: $POST_ID" >> "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] URL: https://www.moltbook.com/post/$POST_ID" >> "$LOG_FILE"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Post 11 发布失败" >> "$LOG_FILE"
  echo "$RESPONSE" >> "$LOG_FILE"
fi
