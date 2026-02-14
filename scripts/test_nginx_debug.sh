#!/bin/bash
echo "=== 测试域名访问 ==="
curl -v http://yinyue.dhmip.cn/ 2>&1 | head -30

echo ""
echo "=== 测试域名 /convert 路由 ==="
curl -v http://yinyue.dhmip.cn/convert 2>&1 | head -30

echo ""
echo "=== 检查Nginx配置是否加载 ==="
grep -r "yinyue.dhmip.cn" /etc/nginx/

echo ""
echo "=== 检查配置语法 ==="
sudo nginx -t 2>&1
