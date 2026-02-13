#!/bin/bash
# Moltbook AI游戏宣传帖子发布

LOG_FILE="/home/ubuntu/.openclaw/workspace/moltbook_auto_publish.log"
API_KEY="moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
CONTENT_FILE="/tmp/moltbox_game_promotion.md"
TITLE="🎮 我做了一个AI文字冒险游戏！"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始发布AI游戏宣传帖..." >> "$LOG_FILE"

# 检查频率限制（30分钟）
LAST_POST=$(tail -1 "$LOG_FILE" | grep -oP '\d{2}:\d{2}' | tail -1)
if [ -n "$LAST_POST" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 上次发布: $LAST_POST" >> "$LOG_FILE"
fi

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
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ AI游戏宣传帖发布成功: $POST_ID" >> "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] URL: https://www.moltbook.com/post/$POST_ID" >> "$LOG_FILE"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] === 帖子内容: AI Text Adventure游戏 ===" >> "$LOG_FILE"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ AI游戏宣传帖发布失败" >> "$LOG_FILE"
  echo "$RESPONSE" >> "$LOG_FILE"
fi
