#!/bin/bash
echo "=== 测试通过域名的POST请求 ==="
curl -X POST http://yinyue.dhmip.cn/convert -v 2>&1 | head -40

echo ""
echo "=== 测试直接Flask的POST请求 ==="
curl -X POST http://127.0.0.1:5001/convert -v 2>&1 | head -40

echo ""
echo "=== 检查是否有其他Nginx配置文件 ==="
grep -r "server_name.*yinyue" /etc/nginx/ 2>/dev/null
