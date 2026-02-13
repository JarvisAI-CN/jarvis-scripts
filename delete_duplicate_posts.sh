#!/bin/bash
# 查找并删除Moltbook重复帖子 - 修正版

API_KEY="moltbook_sk_Lu4wGUciU8Pdk070fin4ngm1P4J736wL"
BASE_URL="https://www.moltbook.com/api/v1"

echo "=== 查找所有帖子 ==="
curl -s "${BASE_URL}/posts?sort=new&limit=50" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" > /tmp/moltbook_posts.json

echo "=== 查找GitHub Actions相关帖子 ==="
cat /tmp/moltbook_posts.json | jq -r '.[] | select(.title | contains("GitHub Actions")) | "\(.id) - \(.title) - \(.created_at)"'

echo ""
echo "请告诉我需要删除哪些帖子ID"
