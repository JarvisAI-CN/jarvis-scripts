# 保质期管理系统 v4.0.0 - 专业的商品保质期管理解决方案

## 📋 项目概述

保质期管理系统是一个专业的商品保质期管理解决方案，采用**多页面架构设计**，每个功能模块独立运行，确保系统的高可用性和稳定性。

### 🎯 核心特点

- **多页面架构**：每个功能模块是独立的页面，互不影响
- **故障隔离**：单个页面代码错误不会影响其他功能
- **模块化设计**：易于扩展和维护
- **安全可靠**：完善的权限管理和数据保护机制
- **响应式设计**：完美适配桌面、平板和手机

---

## 🏗️ 系统架构

### 技术栈

**后端**：
- PHP 8.x
- MySQL 8.x
- PDO 数据库操作层

**前端**：
- HTML5/CSS3
- 原生JavaScript
- Bootstrap 5.3
- HTML5 QR Code 扫描器

### 目录结构

```
/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0/
├── api/                      # 后端API接口
│   ├── login.php            # 登录接口
│   ├── logout.php           # 登出接口
│   └── ...                  # 其他API接口
├── includes/                # 共享代码和配置
│   ├── config.php           # 系统配置
│   ├── db.php               # 数据库连接
│   ├── functions.php        # 工具函数
│   ├── check_auth.php       # 权限检查
│   ├── header.php           # 页面头部
│   └── footer.php           # 页面底部
├── pages/                   # 页面文件
│   ├── login.php            # 登录页面
│   ├── index.php            # 首页
│   ├── new.php              # 新增盘点
│   ├── past.php             # 历史盘点
│   └── settings.php         # 系统设置（管理员）
├── assets/                  # 静态资源
│   ├── css/                 # 样式文件
│   ├── js/                  # JavaScript文件
│   └── images/              # 图片资源
├── logs/                    # 日志文件
├── backup/                  # 数据备份
├── install.php              # 安装程序
└── README.md                # 项目文档
```

---

## 🚀 快速开始

### 1. 系统要求

- PHP 8.0 或更高版本
- MySQL 8.0 或更高版本
- Nginx/Apache Web服务器
- 支持PDO扩展

### 2. 安装步骤

#### 方式一：自动安装（推荐）

```bash
# 1. 上传文件到服务器
cd /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统v4.0/

# 2. 运行安装程序
php install.php

# 3. 删除安装文件
rm install.php
```

#### 方式二：手动安装

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE pandian CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pandian;
SOURCE /path/to/schema.sql;

# 2. 配置系统
编辑 includes/config.php，修改数据库连接信息

# 3. 设置文件权限
chmod 755 api/ includes/ pages/
chmod 644 api/*.php includes/*.php pages/*.php
```

### 3. 访问系统

打开浏览器，访问：
```
http://pandian.dhmip.cn/
```

默认登录凭据：
- 用户名：`admin`
- 密码：`fs123456`

⚠️ **安全提示**：首次登录后请立即修改默认密码！

---

## 📍 功能模块

### 1. 用户认证系统

**登录页面**：`/pages/login.php`
- 用户名/密码验证
- 自动记住我功能
- 防止暴力破解
- 会话超时保护

**API接口**：
- `/api/login.php` - 登录
- `/api/logout.php` - 登出

### 2. 首页/门户

**页面路径**：`/pages/index.php`
- 系统概览统计
- 快速操作入口
- 待处理任务提醒
- 最近活动记录

### 3. 新增盘点

**页面路径**：`/pages/new.php`
- 二维码扫描录入
- 手动输入SKU
- 草稿保存功能
- 实时数据验证

**核心功能**：
- 📷 **二维码扫描**：支持多种二维码格式
- 📝 **手动输入**：支持SKU粘贴和商品搜索
- 💾 **草稿管理**：自动保存盘点进度
- ✅ **数据验证**：实时检查商品信息和保质期

### 4. 历史盘点

**页面路径**：`/pages/past.php`
- 盘点记录查看
- 多条件筛选搜索
- 详细信息展示
- 数据导出功能

**统计概览**：
- 总盘点数
- 商品总数
- 已过期商品
- 本周盘点数

### 5. 系统设置（管理员）

**页面路径**：`/pages/settings.php`
- 用户管理
- 分类管理
- 系统参数配置
- 数据备份恢复

---

## 🔒 安全特性

### 1. 数据安全

- ✅ **密码加密**：使用bcrypt加密存储
- ✅ **SQL注入防护**：使用PDO预处理语句
- ✅ **XSS防护**：所有用户输入进行转义
- ✅ **CSRF保护**：Token验证机制

### 2. 会话管理

- ✅ **会话过期**：30分钟无活动自动登出
- ✅ **IP绑定**：防止会话劫持
- ✅ **单点登录**：支持记住我功能

### 3. 权限控制

- ✅ **角色权限**：admin / user 角色分离
- ✅ **页面保护**：未登录自动跳转
- ✅ **API鉴权**：接口权限验证

---

## 📊 数据库设计

### 核心表结构

1. **users** - 用户表
2. **categories** - 商品分类表
3. **products** - 商品信息表
4. **inventory_sessions** - 盘点会话表
5. **inventory_entries** - 盘点条目表
6. **batches** - 批次信息表
7. **logs** - 操作日志表

### 关系说明

```
users (1) ----< (N) inventory_sessions
categories (1) ----< (N) products
products (1) ----< (N) inventory_entries
inventory_sessions (1) ----< (N) inventory_entries
products (1) ----< (N) batches
```

---

## 🛠️ 开发指南

### API接口开发

所有API接口位于 `/api/` 目录，遵循以下规范：

```php
<?php
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 设置响应头
header('Content-Type: application/json; charset=utf-8');

// 业务逻辑处理
// ...

// 返回JSON响应
echo json_encode($response, JSON_UNESCAPED_UNICODE);
exit;
?>
```

### 页面开发

所有页面位于 `/pages/` 目录，必须包含：

```php
<?php
define('APP_NAME', '保质期管理系统');
session_start();

require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/functions.php';
require_once __DIR__ . '/../includes/check_auth.php';

// 权限检查
if (!checkAuth()) {
    header('Location: /');
    exit;
}

// 页面内容
// ...
?>
```

---

## 📱 部署说明

### 生产环境部署

1. **准备服务器环境**
```bash
# 安装PHP和MySQL
apt-get install php8.0 mysql-server

# 安装PHP扩展
apt-get install php8.0-mysql php8.0-pdo php8.0-mbstring
```

2. **配置Nginx**
```nginx
server {
    listen 80;
    server_name pandian.dhmip.cn;
    root /var/www/html;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.0-fpm.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }
}
```

3. **运行安装程序**
```bash
php install.php
rm install.php
```

4. **设置文件权限**
```bash
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html
```

### 性能优化建议

1. **启用OPcache**：加速PHP执行
2. **使用CDN**：加速静态资源加载
3. **数据库优化**：添加适当索引
4. **启用Gzip压缩**：减少传输数据量

---

## 🐛 故障排除

### 常见问题

**1. 数据库连接失败**
```
检查 includes/config.php 中的数据库配置
确保MySQL服务正在运行
验证用户权限
```

**2. 页面显示空白**
```
检查PHP错误日志
确认文件权限正确
验证数据库连接
```

**3. 登录失败**
```
确认用户名和密码正确
检查users表中用户状态
验证session配置
```

**4. 二维码扫描不工作**
```
确保HTTPS访问（摄像头权限）
检查浏览器兼容性
验证HTML5 QR Code库加载
```

---

## 📝 更新日志

### v4.0.0 (2026-02-22)

**重大更新**：
- ✅ 全新的多页面架构设计
- ✅ 完全重构的代码库
- ✅ 增强的安全机制
- ✅ 改进的用户体验
- ✅ 模块化功能设计

**新增功能**：
- 📷 二维码扫描录入
- 💾 草稿自动保存
- 📊 实时统计概览
- 🔍 高级筛选搜索
- 📤 数据导出功能

**修复问题**：
- 🐛 修复登录页面乱码
- 🐛 修复API路由问题
- 🐛 修复权限检查bug
- 🐛 优化数据库查询性能

---

## 👥 团队和贡献

**开发团队**：
- 架构设计：贾维斯 AI
- 代码开发：OpenClaw AI
- 测试验证：自动化测试

**贡献指南**：
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📞 技术支持

**项目地址**：https://github.com/JarvisAI-CN/保质期管理系统
**问题反馈**：https://github.com/JarvisAI-CN/保质期管理系统/issues
**邮箱联系**：jarvis.openclaw@email.cn

---

## 🙏 鸣谢

感谢所有为本项目做出贡献的开发者和用户！

特别感谢：
- Bootstrap 团队
- HTML5 QR Code 项目
- OpenClaw 社区

---

**版本**：v4.0.0  
**最后更新**：2026-02-22  
**维护者**：贾维斯 AI

---

*让保质期管理变得简单高效！* 🚀
