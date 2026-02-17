#!/bin/bash
# 测试GLM-5可用性

API_KEY="9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
BASE_URL="https://open.bigmodel.cn/api/paas/v4"

echo "=== 测试不同的GLM-5模型ID ==="
echo ""

for model in "glm-5" "glm-5.0" "glm-5-turbo" "glm-5-plus"; do
    echo "测试模型: $model"
    curl -s "$BASE_URL/chat/completions" \
      -H "Authorization: Bearer $API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"model\": \"$model\",
        \"messages\": [{\"role\": \"user\", \"content\": \"测试\"}],
        \"max_tokens\": 5
      }" | python3 -c "import sys, json; d=json.load(sys.stdin); print('✅ 可用' if 'error' not in d else f\"❌ {d.get('error', {}).get('message', 'Unknown error')}\")" 2>/dev/null
    echo ""
done

echo "=== 对比GLM-4.7 ==="
echo "测试模型: glm-4.7"
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7",
    "messages": [{"role": "user", "content": "测试"}],
    "max_tokens": 5
  }' | python3 -c "import sys, json; d=json.load(sys.stdin); print('✅ 可用' if 'error' not in d and 'choices' in d else f\"❌ {d.get('error', {}).get('message', 'Unknown error')}\")" 2>/dev/null
