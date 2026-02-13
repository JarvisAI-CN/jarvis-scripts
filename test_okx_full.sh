#!/bin/bash
# OKX完整测试脚本

API_KEY="73b8a24a-232a-4df4-82d1-77b12e8b8e37"
SECRET="BBDA511D164D3C088BDCCE96D4D4340B"
PASSPHRASE="fs123456."

echo "=== 🔍 测试1: BTC价格 ==="
curl -s "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT" | jq '.data[0] | {币种: .instId, 最新价: "$" + .last, 24h最高: "$" + .high24h, 24h最低: "$" + .low24h, 24h成交量: .vol24h}'

echo -e "\n=== 🔍 测试2: ETH价格 ==="
curl -s "https://www.okx.com/api/v5/market/ticker?instId=ETH-USDT" | jq '.data[0] | {币种: .instId, 最新价: "$" + .last, 24h最高: "$" + .high24h, 24h最低: "$" + .low24h}'

echo -e "\n=== 💰 测试3: 账户余额 ==="
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
METHOD="GET"
PATH="/api/v5/account/balance"
SIGN_STRING="${TIMESTAMP}${METHOD}${PATH}"
SIGNATURE=$(echo -n "$SIGN_STRING" | openssl dgst -sha256 -hmac "$SECRET" -binary | base64)

curl -s "https://www.okx.com${PATH}" \
  -H "OK-ACCESS-KEY: ${API_KEY}" \
  -H "OK-ACCESS-SIGN: ${SIGNATURE}" \
  -H "OK-ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "OK-ACCESS-PASSPHRASE: ${PASSPHRASE}" | jq '.data[0] | {总权益: .totalEq, 可用: .availBal, 冻结: .frozenBal}'

echo -e "\n✅ 测试完成"
