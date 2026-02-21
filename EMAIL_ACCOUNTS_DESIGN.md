# 邮箱账户配置功能 - 架构设计文档

## 项目概述

为保质期管理系统添加QQ邮箱账户配置功能，支持多账户管理和智能轮换发送。

## 1. 数据库设计

### 1.1 邮箱账户表 (email_accounts)

```sql
CREATE TABLE `email_accounts` (
  `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  `qq_number` VARCHAR(20) NOT NULL UNIQUE COMMENT 'QQ号',
  `auth_code_encrypted` TEXT NOT NULL COMMENT 'AES-256加密的授权码',
  `is_active` TINYINT(1) DEFAULT 1 COMMENT '是否启用: 1=启用, 0=禁用',
  `last_used_at` DATETIME DEFAULT NULL COMMENT '最后使用时间',
  `usage_count` INT DEFAULT 0 COMMENT '使用次数统计',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX `idx_active_last_used` (`is_active`, `last_used_at`),
  INDEX `idx_qq_number` (`qq_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='邮箱账户配置表';
```

### 1.2 安全设计

**授权码加密方案**：
- 使用AES-256-CBC加密
- 密钥从config.php读取（定义EMAIL_ENCRYPTION_KEY常量）
- IV向量存储在加密数据前16字节

**加密函数**：
```php
function encryptAuthCode($authCode) {
    $key = EMAIL_ENCRYPTION_KEY; // 32字节密钥
    $iv = openssl_random_pseudo_bytes(16);
    $encrypted = openssl_encrypt($authCode, 'AES-256-CBC', $key, 0, $iv);
    return base64_encode($iv . $encrypted);
}

function decryptAuthCode($encrypted) {
    $key = EMAIL_ENCRYPTION_KEY;
    $data = base64_decode($encrypted);
    $iv = substr($data, 0, 16);
    $encrypted = substr($data, 16);
    return openssl_decrypt($encrypted, 'AES-256-CBC', $key, 0, $iv);
}
```

## 2. API接口设计

### 2.1 添加邮箱账户

**端点**: `index.php?api=add_email_account`

**方法**: POST

**请求体**:
```json
{
  "qq_number": "123456789",
  "auth_code": "授权码"
}
```

**响应**:
```json
{
  "success": true,
  "message": "邮箱账户添加成功"
}
```

### 2.2 列出所有邮箱账户

**端点**: `index.php?api=list_email_accounts`

**方法**: GET

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "qq_number": "123456789",
      "email": "123456789@qq.com",
      "is_active": 1,
      "last_used_at": "2026-02-21 14:00:00",
      "usage_count": 15,
      "created_at": "2026-02-20 10:00:00"
    }
  ]
}
```

### 2.3 删除邮箱账户

**端点**: `index.php?api=delete_email_account`

**方法**: POST

**请求体**:
```json
{
  "id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "邮箱账户删除成功"
}
```

### 2.4 切换邮箱状态

**端点**: `index.php?api=toggle_email_account`

**方法**: POST

**请求体**:
```json
{
  "id": 1,
  "is_active": 0
}
```

**响应**:
```json
{
  "success": true,
  "message": "邮箱状态已更新"
}
```

### 2.5 测试发送邮件

**端点**: `index.php?api=test_email_account`

**方法**: POST

**请求体**:
```json
{
  "id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "测试邮件发送成功"
}
```

## 3. 轮换算法设计

### 3.1 Round-Robin策略

**选择逻辑**:
1. 查询所有启用的邮箱账户 (is_active=1)
2. 按last_used_at升序排序（最久未使用的优先）
3. 如果last_used_at相同，按usage_count升序排序
4. 选择第一个账户
5. 更新该账户的last_used_at和usage_count

**SQL查询**:
```sql
SELECT id, qq_number, auth_code_encrypted
FROM email_accounts
WHERE is_active = 1
ORDER BY last_used_at ASC, usage_count ASC
LIMIT 1
```

### 3.2 实现函数

```php
function getNextEmailAccount($conn) {
    // 获取下一个可用账户
    $stmt = $conn->prepare("
        SELECT id, qq_number, auth_code_encrypted
        FROM email_accounts
        WHERE is_active = 1
        ORDER BY last_used_at ASC, usage_count ASC
        LIMIT 1
    ");
    $stmt->execute();
    $result = $stmt->get_result();

    if ($result->num_rows === 0) {
        return null; // 没有可用账户
    }

    $account = $result->fetch_assoc();

    // 更新使用记录
    $updateStmt = $conn->prepare("
        UPDATE email_accounts
        SET last_used_at = NOW(), usage_count = usage_count + 1
        WHERE id = ?
    ");
    $updateStmt->bind_param("i", $account['id']);
    $updateStmt->execute();

    // 解密授权码
    $account['auth_code'] = decryptAuthCode($account['auth_code_encrypted']);
    $account['email'] = $account['qq_number'] . '@qq.com';

    return $account;
}
```

## 4. 后台管理界面

### 4.1 admin.php添加菜单

在现有菜单中添加：
```php
<a href="#email-accounts" class="list-group-item list-group-item-action" data-page="email-accounts">
    📧 邮箱账户管理
</a>
```

### 4.2 邮箱账户管理页面

**显示内容**:
1. 邮箱列表（QQ号、完整邮箱、状态、使用次数、最后使用时间）
2. 添加账户按钮
3. 操作按钮（启用/禁用、删除、测试发送）

**界面布局**:
```
📧 邮箱账户管理
┌─────────────────────────────────────────────────────────────┐
│ [+ 添加邮箱账户]                                             │
├─────────────────────────────────────────────────────────────┤
│ QQ号          邮箱              状态    使用次数    操作      │
├─────────────────────────────────────────────────────────────┤
│ 123456789   123...@qq.com      ✅启用    15      [禁用][测试] │
│ 987654321   987...@qq.com      ❌禁用    8       [启用][删除] │
└─────────────────────────────────────────────────────────────┘
```

## 5. 文件结构

### 5.1 需要修改的文件

1. **index.php** - 添加API端点
2. **admin.php** - 添加邮箱管理页面
3. **smtp_mailer.php** - 修改发送逻辑使用轮换账户
4. **config.php** - 添加EMAIL_ENCRYPTION_KEY常量
5. **install.php** - 添加数据库表创建
6. **upgrade_to_v2.14.php** - 升级脚本

### 5.2 新增文件

1. **email_accounts_api.php** - 邮箱账户API（可选，也可以集成到index.php）

## 6. 安全考虑

### 6.1 权限控制

- 只有登录的管理员才能访问邮箱配置功能
- 所有API端点检查$_SESSION['admin']

### 6.2 授权码保护

- 授权码永远不在前端显示
- 列表API只返回qq_number，不返回auth_code
- 日志中不记录授权码明文

### 6.3 输入验证

- QQ号必须是数字，长度5-15位
- 授权码长度6-32位
- 防止SQL注入（使用预处理语句）

## 7. 实现优先级

### P0 (核心功能)
1. 数据库表创建
2. 添加/删除/列出邮箱账户API
3. 轮换算法实现
4. 修改smtp_mailer.php使用轮换账户

### P1 (管理界面)
1. admin.php添加邮箱管理页面
2. 邮箱列表展示
3. 启用/禁用功能

### P2 (增强功能)
1. 测试发送功能
2. 使用统计展示
3. 批量导入邮箱账户

## 8. 测试用例

1. 添加邮箱账户 → 验证加密存储
2. 列出邮箱账户 → 验证授权码不泄露
3. 启用/禁用账户 → 验证轮换算法跳过禁用账户
4. 发送多封邮件 → 验证轮换机制
5. 删除账户 → 验证不影响其他账户

## 9. 版本计划

- **v2.14.0** - 核心功能实现（P0）
- **v2.14.1** - 管理界面完善（P1）
- **v2.14.2** - 增强功能（P2）
