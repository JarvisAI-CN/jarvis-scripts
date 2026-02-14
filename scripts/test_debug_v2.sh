#!/bin/bash
echo "=== 测试 1: GET 首页 ==="
curl -v http://yinyue.dhmip.cn/ 2>&1 | grep -E "HTTP/|Host:|Server:|X-Debug"

echo -e "\n=== 测试 2: POST /convert (无 body) ==="
curl -v -X POST http://yinyue.dhmip.cn/convert 2>&1 | grep -E "HTTP/|Host:|Server:|X-Debug"

echo -e "\n=== 测试 3: POST / (应该 404) ==="
curl -v -X POST http://yinyue.dhmip.cn/ 2>&1 | grep -E "HTTP/|Host:|Server:|X-Debug"

echo -e "\n=== 测试 4: GET /convert (应该 404) ==="
curl -v http://yinyue.dhmip.cn/convert 2>&1 | grep -E "HTTP/|Host:|Server:|X-Debug"

echo -e "\n=== 检查 access log ==="
sudo tail -10 /var/log/nginx/debug_access.log

echo -e "\n=== 检查 error log ==="
sudo tail -10 /var/log/nginx/debug_error.log
