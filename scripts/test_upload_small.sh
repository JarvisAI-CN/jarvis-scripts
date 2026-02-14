#!/bin/bash
# 创建一个小测试文件
echo "test content" > /tmp/test_small.txt

echo "=== 测试POST上传小文件 ==="
curl -X POST -F "file=@/tmp/test_small.txt" http://yinyue.dhmip.cn/convert -v 2>&1 | head -50

echo ""
echo "=== 测试直接Flask上传小文件 ==="
curl -X POST -F "file=@/tmp/test_small.txt" http://127.0.0.1:5001/convert -v 2>&1 | head -50
