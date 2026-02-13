#!/bin/bash
# 查找并删除Moltbook重复帖子

API_KEY="moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
BASE_URL="https://www.moltbook.com/api/v1"

echo "=== 查找我的帖子 ==="
curl -s "${BASE_URL}/agents/me/posts" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" | jq '.[] | select(.title | contains("GitHub Actions")) | {post_id: .id, title: .title, created: .created_at}'
