# 保质期管理系统v4.0 - 详细开发需求文档

## 项目概述
- **项目名称**：保质期管理系统v4.0
- **部署地址**：http://pandian.dhmip.cn/
- **服务器**：211.154.19.189:21 (FTP)
- **开发语言**：PHP 8.2 + 原生JavaScript
- **前端框架**：Bootstrap 5.3 + jQuery
- **数据库**：MySQL
- **架构**：多页面应用架构（MPA）

---

## 功能需求

### 1. 用户认证系统

#### 1.1 登录页面
- **页面路径**：/
- **功能描述**：用户身份验证
- **输入**：
  - 用户名（文本框）
  - 密码（密码框）
  - 记住我（复选框）
- **输出**：
  - 登录成功：跳转至首页
  - 登录失败：显示错误信息
- **业务逻辑**：
  - 使用bcrypt进行密码验证
  - 支持7天自动登录（记住我功能）
  - 30分钟会话超时
  - 登录失败日志记录

#### 1.2 登出功能
- **页面路径**：/api/logout.php
- **功能描述**：用户退出登录
- **输入**：会话Cookie
- **输出**：
  - 成功：清除会话和Cookie
  - 失败：返回错误信息
- **业务逻辑**：
  - 清除会话数据
  - 删除remember_token cookie
  - 记录登出日志

### 2. 系统首页

#### 2.1 系统概览
- **页面路径**：/pages/index.php
- **功能描述**：显示系统统计数据和快速操作
- **输入**：登录会话
- **输出**：
  - 系统统计卡片（总商品数、总盘点数、已过期商品数、库存金额）
  - 待处理任务列表
  - 最近活动记录
  - 系统通知
- **业务逻辑**：
  - 调用/api/overview.php获取统计数据
  - 调用/api/pending-tasks.php获取待处理任务
  - 调用/api/recent-activity.php获取最近活动
  - 实时数据更新（30秒刷新）

### 3. 商品管理

#### 3.1 新增商品
- **页面路径**：/pages/products/add.php
- **功能描述**：添加新商品信息
- **输入**：
  - SKU（必填）
  - 商品名称（必填）
  - 分类（下拉选择）
  - 单位（文本框）
  - 移除缓冲天数（数字输入）
  - 描述（文本区域）
- **输出**：
  - 成功：保存商品信息，跳转至商品列表
  - 失败：显示错误信息
- **业务逻辑**：
  - 验证SKU唯一性
  - 保存到pd_products表
  - 记录操作日志

#### 3.2 商品列表
- **页面路径**：/pages/products/list.php
- **功能描述**：显示所有商品列表
- **输入**：
  - 搜索关键词
  - 分类筛选
  - 分页参数
- **输出**：
  - 商品列表（含SKU、名称、分类、单位等信息）
  - 搜索和筛选结果
- **业务逻辑**：
  - 支持关键词搜索
  - 支持分类筛选
  - 分页显示（每页10条）
  - 调用/api/products/list.php接口

#### 3.3 编辑商品
- **页面路径**：/pages/products/edit.php?id=xxx
- **功能描述**：修改商品信息
- **输入**：同新增商品
- **输出**：
  - 成功：更新商品信息
  - 失败：显示错误信息
- **业务逻辑**：
  - 验证SKU唯一性（排除当前商品）
  - 更新pd_products表
  - 记录操作日志

#### 3.4 删除商品
- **API接口**：/api/products/delete.php
- **功能描述**：删除商品信息
- **输入**：商品ID
- **输出**：
  - 成功：删除商品记录
  - 失败：显示错误信息
- **业务逻辑**：
  - 检查商品是否关联盘点记录
  - 支持软删除或硬删除
  - 记录操作日志

### 4. 盘点管理

#### 4.1 新增盘点
- **页面路径**：/pages/new.php
- **功能描述**：创建新的盘点任务
- **输入**：
  - 二维码扫描（模拟）
  - 手动输入SKU
  - 批次信息（生产日期、保质期）
- **输出**：
  - 实时显示已扫描商品列表
  - 盘点会话保存为草稿
- **业务逻辑**：
  - 自动保存草稿（每30秒）
  - 支持二维码扫描和手动输入
  - 实时验证商品信息
  - 调用/api/inventory/add.php接口

#### 4.2 历史盘点查询
- **页面路径**：/pages/past.php
- **功能描述**：查询和管理盘点记录
- **输入**：
  - 状态筛选（全部/草稿/已提交/已完成）
  - 关键词搜索
  - 时间范围筛选
  - 分页参数
- **输出**：
  - 盘点记录列表
  - 详情查看
  - 导出功能
- **业务逻辑**：
  - 支持多条件筛选
  - 分页显示（每页10条）
  - 调用/api/inventory/list.php接口

#### 4.3 盘点详情
- **页面路径**：/pages/inventory/detail.php?id=xxx
- **功能描述**：查看盘点详细信息
- **输入**：盘点ID
- **输出**：
  - 盘点基本信息（时间、状态、商品数量）
  - 商品列表（含批次信息）
  - 操作历史
- **业务逻辑**：
  - 调用/api/inventory/detail.php接口
  - 显示完整盘点记录

#### 4.4 提交盘点
- **API接口**：/api/inventory/submit.php
- **功能描述**：提交盘点任务
- **输入**：盘点ID
- **输出**：
  - 成功：更新状态为已提交
  - 失败：显示错误信息
- **业务逻辑**：
  - 检查盘点完整性
  - 更新pd_inventory_sessions表
  - 记录操作日志

### 5. 系统管理

#### 5.1 用户管理
- **页面路径**：/pages/admin/users.php
- **功能描述**：管理系统用户
- **输入**：
  - 用户名
  - 真实姓名
  - 邮箱
  - 角色（管理员/普通用户）
  - 状态（启用/禁用/锁定）
- **输出**：
  - 用户列表
  - 用户详情
  - 操作结果
- **业务逻辑**：
  - 只有管理员可以访问
  - 支持新增、编辑、删除用户
  - 记录操作日志

#### 5.2 分类管理
- **页面路径**：/pages/admin/categories.php
- **功能描述**：管理商品分类
- **输入**：
  - 分类名称
  - 类型（食品/物料/咖啡豆/其他）
  - 描述
- **输出**：
  - 分类列表
  - 操作结果
- **业务逻辑**：
  - 支持新增、编辑、删除分类
  - 分类与商品关联（外键约束）
  - 记录操作日志

#### 5.3 系统设置
- **页面路径**：/pages/admin/settings.php
- **功能描述**：系统参数配置
- **输入**：
  - 系统名称
  - 版本信息
  - 数据库配置
  - 通知配置
  - 备份配置
- **输出**：
  - 设置表单
  - 保存结果
- **业务逻辑**：
  - 只有管理员可以访问
  - 配置信息保存到includes/config.php

---

## 数据库设计

### 核心数据表

#### 1. 用户表 (pd_users)
```sql
CREATE TABLE IF NOT EXISTS pd_users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) DEFAULT NULL,
    realname VARCHAR(50) DEFAULT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    status ENUM('active', 'inactive', 'locked') DEFAULT 'active',
    last_login DATETIME DEFAULT NULL,
    login_count INT DEFAULT 0,
    remember_token VARCHAR(32) DEFAULT NULL,
    remember_token_expires DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 2. 商品分类表 (pd_categories)
```sql
CREATE TABLE IF NOT EXISTS pd_categories (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(20) DEFAULT 'food',
    description TEXT DEFAULT NULL,
    rule TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 3. 商品信息表 (pd_products)
```sql
CREATE TABLE IF NOT EXISTS pd_products (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    category_id INT UNSIGNED DEFAULT NULL,
    unit VARCHAR(20) DEFAULT '个',
    removal_buffer INT DEFAULT 0,
    description TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES pd_categories(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4. 盘点会话表 (pd_inventory_sessions)
```sql
CREATE TABLE IF NOT EXISTS pd_inventory_sessions (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_key VARCHAR(50) NOT NULL UNIQUE,
    user_id INT UNSIGNED DEFAULT NULL,
    item_count INT DEFAULT 0,
    status ENUM('draft', 'submitted', 'completed') DEFAULT 'draft',
    notes TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES pd_users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 5. 盘点条目表 (pd_inventory_entries)
```sql
CREATE TABLE IF NOT EXISTS pd_inventory_entries (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) DEFAULT NULL,
    product_id INT UNSIGNED DEFAULT NULL,
    quantity INT DEFAULT 1,
    batches TEXT DEFAULT NULL,
    notes TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pd_products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 6. 商品批次表 (pd_batches)
```sql
CREATE TABLE IF NOT EXISTS pd_batches (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) DEFAULT NULL,
    product_id INT UNSIGNED DEFAULT NULL,
    batch_code VARCHAR(50) DEFAULT NULL,
    expiry_date DATE DEFAULT NULL,
    quantity INT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES pd_products(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 7. 操作日志表 (pd_logs)
```sql
CREATE TABLE IF NOT EXISTS pd_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED DEFAULT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES pd_users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## API接口设计

### 1. 用户认证接口

#### 1.1 登录接口
- **URL**：/api/login.php
- **方法**：POST
- **请求参数**：
  ```json
  {
    "username": "admin",
    "password": "fs123456",
    "remember": true
  }
  ```
- **响应**：
  - 成功：
    ```json
    {
      "success": true,
      "message": "登录成功",
      "user": {
        "id": 1,
        "username": "admin",
        "realname": "系统管理员",
        "role": "admin"
      }
    }
    ```
  - 失败：
    ```json
    {
      "success": false,
      "message": "用户名或密码错误",
      "error": "用户名或密码错误"
    }
    ```

#### 1.2 登出接口
- **URL**：/api/logout.php
- **方法**：POST
- **响应**：
  ```json
  {
    "success": true,
    "message": "登出成功"
  }
  ```

### 2. 系统概览接口

#### 2.1 获取系统统计数据
- **URL**：/api/overview.php
- **方法**：GET
- **响应**：
  ```json
  {
    "success": true,
    "data": {
      "totalProducts": 100,
      "totalInventories": 50,
      "expiredProducts": 5,
      "totalValue": 10000.00
    }
  }
  ```

### 3. 商品管理接口

#### 3.1 新增商品
- **URL**：/api/products/add.php
- **方法**：POST
- **请求参数**：
  ```json
  {
    "sku": "SKU001",
    "name": "测试商品",
    "category_id": 1,
    "unit": "个",
    "removal_buffer": 7,
    "description": "这是一个测试商品"
  }
  ```
- **响应**：
  ```json
  {
    "success": true,
    "message": "商品添加成功",
    "product_id": 101
  }
  ```

#### 3.2 获取商品列表
- **URL**：/api/products/list.php
- **方法**：GET
- **参数**：
  - search：搜索关键词
  - category：分类ID
  - page：页码
  - limit：每页数量
- **响应**：
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": 1,
          "sku": "SKU001",
          "name": "测试商品",
          "category_id": 1,
          "category_name": "小食品",
          "unit": "个",
          "removal_buffer": 7,
          "description": "这是一个测试商品"
        }
      ],
      "total": 100,
      "page": 1,
      "limit": 10
    }
  }
  ```

### 4. 盘点管理接口

#### 4.1 新增盘点
- **URL**：/api/inventory/add.php
- **方法**：POST
- **请求参数**：
  ```json
  {
    "sku": "SKU001",
    "quantity": 10,
    "batches": [
      {
        "batch_code": "BATCH001",
        "expiry_date": "2024-12-31",
        "quantity": 5
      },
      {
        "batch_code": "BATCH002",
        "expiry_date": "2025-01-31",
        "quantity": 5
      }
    ]
  }
  ```
- **响应**：
  ```json
  {
    "success": true,
    "message": "商品添加成功",
    "inventory_id": 51
  }
  ```

#### 4.2 获取盘点列表
- **URL**：/api/inventory/list.php
- **方法**：GET
- **参数**：
  - status：状态筛选（draft/submitted/completed）
  - search：搜索关键词
  - start_date：开始日期
  - end_date：结束日期
  - page：页码
  - limit：每页数量
- **响应**：
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": 51,
          "session_key": "INV0051",
          "user_id": 1,
          "user_name": "admin",
          "item_count": 1,
          "status": "draft",
          "created_at": "2024-01-01 10:00:00"
        }
      ],
      "total": 50,
      "page": 1,
      "limit": 10
    }
  }
  ```

---

## 开发环境要求

### 1. 服务器环境

#### 1.1 系统要求
- **操作系统**：Linux (推荐Ubuntu 22.04)
- **Web服务器**：Nginx 1.20+ 或 Apache 2.4+
- **PHP版本**：8.2+
- **MySQL版本**：5.7+ 或 MariaDB 10.5+

#### 1.2 PHP扩展
- mysqli 或 PDO
- mbstring
- json
- session
- cookie
- hash
- filter
- openssl

### 2. 开发工具

#### 2.1 编辑器
- Visual Studio Code
- PHPStorm
- Sublime Text

#### 2.2 调试工具
- Xdebug
- Chrome DevTools
- Postman (API测试)

#### 2.3 版本控制
- Git
- GitHub/GitLab

---

## 部署要求

### 1. 服务器配置

#### 1.1 FTP配置
- **地址**：211.154.19.189:21
- **用户名**：pandian
- **密码**：pandian
- **根路径**：/ (网站根目录)

#### 1.2 数据库配置
- **地址**：localhost:3306
- **用户名**：root
- **密码**：(需配置)
- **数据库名**：pandian

### 2. 部署步骤

#### 2.1 文件上传
1. 使用FTP工具连接服务器
2. 将项目文件上传到根路径
3. 确保文件夹权限正确（755）
4. 确保文件权限正确（644）

#### 2.2 数据库初始化
1. 连接MySQL服务器
2. 创建pandian数据库
3. 运行数据库初始化脚本（自动创建表结构）
4. 配置includes/config.php文件

#### 2.3 配置文件修改
1. 修改includes/config.php中的数据库连接信息
2. 配置BASE_URL为实际域名
3. 设置DEBUG_MODE为false（生产环境）

---

## 验收标准

### 1. 功能验收

#### 1.1 用户认证
- 登录页面显示正常
- 用户名/密码验证正确
- 记住我功能正常
- 登出功能正常
- 会话超时功能正常

#### 1.2 首页功能
- 系统概览卡片显示正确
- 待处理任务列表加载正常
- 最近活动记录显示正确
- 系统通知显示正常
- 实时数据更新正常

#### 1.3 商品管理
- 新增商品功能正常
- 商品列表显示正确
- 编辑商品功能正常
- 删除商品功能正常
- 搜索和筛选功能正常

#### 1.4 盘点管理
- 新增盘点功能正常
- 历史盘点查询正常
- 盘点详情查看正常
- 盘点提交功能正常
- 导出功能正常（Excel/CSV）

#### 1.5 系统管理
- 用户管理功能正常
- 分类管理功能正常
- 系统设置功能正常

### 2. 性能验收

#### 2.1 响应时间
- 页面加载时间 < 2秒
- API响应时间 < 500ms
- 数据导出时间 < 10秒

#### 2.2 并发处理
- 支持50+并发用户
- 数据库查询响应时间 < 1秒

#### 2.3 稳定性
- 系统连续运行7天无崩溃
- 内存使用稳定
- 日志记录完整

### 3. 安全验收

#### 3.1 身份验证
- 密码加密存储（bcrypt）
- 会话超时控制
- 防止SQL注入
- XSS防护

#### 3.2 数据安全
- 备份功能正常
- 恢复功能正常
- 数据加密传输（HTTPS）

---

## 项目结构

```
保质期管理系统v4.0/
├── install.php                 # 安装引导页
├── index.php                   # 首页重定向
├── includes/
│   ├── config.php             # 系统配置
│   ├── db.php                 # 数据库类
│   ├── functions.php          # 工具函数
│   ├── check_auth.php         # 权限检查
│   ├── header.php             # 页面头部
│   └── footer.php             # 页面底部
├── pages/
│   ├── login.php              # 登录页面
│   ├── index.php              # 首页
│   ├── new.php                # 新增盘点
│   └── past.php               # 历史盘点
├── api/
│   ├── login.php              # 登录接口
│   ├── logout.php             # 登出接口
│   ├── overview.php           # 概览接口
│   └── [其他接口待开发]
├── assets/
│   ├── css/                   # 样式文件
│   ├── js/                    # 脚本文件
│   ├── images/                # 图片资源
│   └── lib/                   # 外部库
├── uploads/                   # 上传文件
├── logs/                      # 日志文件
└── backup/                    # 备份文件
```

---

## 待开发功能

### 1. 数据库连接问题
- 解决SQLSTATE[HY000] [1045] Access denied for user 'root'@'localhost' 错误
- 配置正确的MySQL用户名和密码

### 2. 页面完善
- **首页图表展示**：优化统计图表
- **历史记录删除/编辑**：实现编辑和删除功能
- **导出功能**：数据导出到Excel/CSV

### 3. 商品管理
- 商品信息添加/编辑/删除
- 批量导入功能
- 商品分类管理

### 4. 批次管理
- 批次追踪
- 预警通知
- 过期提醒

### 5. 报表统计
- 保质期分析报表
- 盘点趋势分析
- 库存周转率计算

### 6. 系统优化
- 二维码扫描功能完善
- 离线模式支持
- 数据同步功能

---

**文档版本**：v1.0.0
**创建时间**：2026-02-22
**最后更新**：2026-02-22
**项目状态**：开发中，框架已搭建，核心功能待实现
