#!/bin/bash
# 检查智谱API可用模型

API_KEY="9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
BASE_URL="https://open.bigmodel.cn/api/paas/v4"

echo "=== 检查智谱API可用模型 ==="
echo ""

# 尝试调用模型列表API
curl -s "$BASE_URL/models" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" | python3 -m json.tool 2>/dev/null || echo "无法获取模型列表"

echo ""
echo "=== 尝试GLM-5.0 API ==="
echo ""

# 测试GLM-5.0是否可用
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5.0",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 10
  }' | python3 -m json.tool 2>/dev/null | head -30
