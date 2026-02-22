#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# 读取当前文件
with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到并修复API接口处理块的结构问题
# 登录接口的if语句没有正确地闭合
fixed_content = re.sub(
    r'''
    if \(\$action === 'login'\) \{
        \$data = json_decode\(file_get_contents\('php://input'\), true\);
        \$stmt = \$conn->prepare\("SELECT id, username, password FROM users WHERE username = \?"\);
        \$stmt->bind_param\("s", \$data\['username'\]\); \$stmt->execute\(\);
        \$row = \$stmt->get_result\(\)->fetch_assoc\(\);
        if \(\$row && password_verify\(\$data\['password'\], \$row\['password'\]\)\) \{
            \$_SESSION\['user_id'\] = \$row\['id'\]; \$_SESSION\['username'\] = \$row\['username'\];
            echo json_encode\(\['success'=>true\]\); exit;
    # AI分析API接口
    if \(\$action === 'analyze_inventory'\) \{
    ''',
    r'''
    if ($action === 'login') {
        $data = json_decode(file_get_contents('php://input'), true);
        $stmt = $conn->prepare("SELECT id, username, password FROM users WHERE username = ?");
        $stmt->bind_param("s", $data['username']); $stmt->execute();
        $row = $stmt->get_result()->fetch_assoc();
        if ($row && password_verify($data['password'], $row['password'])) {
            $_SESSION['user_id'] = $row['id']; $_SESSION['username'] = $row['username'];
            echo json_encode(['success'=>true]); exit;
        }
        echo json_encode(['success'=>false, 'message'=>'账号或密码错误']); exit;
    }
    # AI分析API接口
    if ($action === 'analyze_inventory') {
    ''',
    content,
    flags=re.DOTALL | re.VERBOSE
)

# 保存修改后的文件
with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ API接口处理块结构问题已修复")
