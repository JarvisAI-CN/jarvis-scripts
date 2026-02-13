#!/bin/bash
# OKX API测试脚本

API_KEY="73b8a24a-232a-4df4-82d1-77b12e8b8e37"
SECRET="BBDA511D164D3C088BDCCE96D4D4340B"
PASSPHRASE="fs123456."

# 测试1: 获取BTC价格
echo "=== 测试1: 获取BTC价格 ==="
curl -s "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT" | jq '.data[0] | {instId: .instId, last: .last, high24h: .high24h, low24h: .low24h, vol24h: .vol24h, volCcy24h: .volCcy24h}'

echo -e "\n=== 测试2: 获取账户余额 ==="
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")
METHOD="GET"
PATH="/api/v5/account/balance"
SIGN_STRING="${TIMESTAMP}${METHOD}${PATH}"
SIGNATURE=$(echo -n "$SIGN_STRING" | openssl dgst -sha256 -hmac "$SECRET" -binary | base64)

curl -s "https://www.okx.com${PATH}" \
  -H "OK-ACCESS-KEY: ${API_KEY}" \
  -H "OK-ACCESS-SIGN: ${SIGNATURE}" \
  -H "OK-ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "OK-ACCESS-PASSPHRASE: ${PASSPHRASE}" | jq '.data[0]'
