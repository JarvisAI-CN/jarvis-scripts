# 保质期管理系统 - 部署说明

## 项目概述

这是一个轻量级的保质期管理系统，支持通过手机摄像头扫描条形码/二维码，快速录入商品批次信息和保质期。

### 技术栈
- **后端**: 原生 PHP (7.4+)
- **数据库**: MySQL 5.7+
- **前端**: HTML5, Bootstrap 5, JavaScript (jQuery)
- **扫码库**: html5-qrcode

---

## 📦 文件清单

```
保质期管理系统/
├── database.sql      # 数据库建表语句
├── db.php           # 数据库连接配置
├── index.php        # 主应用文件（包含前后端）
└── README.md        # 本文档
```

---

## 🚀 快速部署指南

### 步骤 1: 导入数据库

1. 登录 MySQL（使用 phpMyAdmin 或命令行）：
   ```bash
   mysql -u root -p
   ```

2. 导入数据库结构：
   ```bash
   source /path/to/database.sql
   ```

   或使用 phpMyAdmin 的"导入"功能上传 `database.sql` 文件。

3. 验证数据库创建成功：
   ```sql
   USE expiry_system;
   SHOW TABLES;
   ```
   应显示 `products` 和 `batches` 两张表。

### 步骤 2: 配置数据库连接

编辑 `db.php` 文件，修改数据库配置：

```php
define('DB_HOST', 'localhost');        // 数据库主机
define('DB_USER', 'root');             // 数据库用户名
define('DB_PASS', 'your_password');    // 修改为你的MySQL密码
define('DB_NAME', 'expiry_system');    // 数据库名称
```

### 步骤 3: 部署到 Web 服务器

#### 方法 A: 使用宝塔面板（推荐新手）

1. 登录宝塔面板
2. 创建新网站：
   - 域名: `expiry.yourdomain.com`（或使用测试域名）
   - PHP版本: 选择 7.4 或更高
   - 数据库: 不需要（已在步骤1创建）

3. 上传文件到网站根目录：
   - 进入"文件"管理
   - 打开网站目录 `/www/wwwroot/yourdomain.com/`
   - 上传 `db.php` 和 `index.php` 两个文件

4. 访问网站测试：
   ```
   http://your-domain.com/index.php
   ```

#### 方法 B: 手动部署（Nginx/Apache）

1. 将文件上传到 Web 目录：
   ```bash
   /var/www/html/expiry_system/
   ```

2. 设置文件权限：
   ```bash
   chown -R www-data:www-data /var/www/html/expiry_system/
   chmod -R 755 /var/www/html/expiry_system/
   ```

3. 配置 Nginx/Apache 虚拟主机（示例 Nginx）：
   ```nginx
   server {
       listen 80;
       server_name expiry.yourdomain.com;
       root /var/www/html/expiry_system;
       index index.php index.html;
       
       location ~ \.php$ {
           fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
           fastcgi_index index.php;
           include fastcgi_params;
           fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
       }
   }
   ```

4. 重启服务：
   ```bash
   sudo systemctl reload nginx
   ```

---

## 📱 使用说明

### 基本流程

1. **扫描条形码**
   - 点击"启动摄像头扫描"按钮
   - 允许浏览器访问摄像头
   - 将条形码对准扫描框

2. **录入商品信息**
   - 如果是新商品：手动输入商品名称
   - 如果是旧商品：系统自动填充名称和已有批次

3. **添加批次**
   - 默认显示一行输入框
   - 点击"+ 添加更多批次"可动态添加新行
   - 每行输入：到期日期 + 数量

4. **保存数据**
   - 点击"保存商品信息"按钮
   - 系统自动保存商品和批次到数据库

### 移动端使用

- 推荐使用 Chrome 或 Safari 浏览器
- 首次访问需允许摄像头权限
- 建议添加到主屏幕，像原生 App 一样使用

---

## 🔍 功能特性

### 已实现功能

✅ 扫码识别（条形码/二维码）  
✅ 手动输入 SKU 查询  
✅ 自动识别新旧商品  
✅ 显示已有批次列表  
✅ 动态添加多批次  
✅ 批次到期状态提醒（过期/临期）  
✅ 响应式设计（移动端适配）  
✅ 数据验证和错误处理  
✅ 事务保证数据一致性  

### 数据库特性

- 商品 SKU 唯一索引
- 外键约束保证数据完整性
- 级联删除（删除商品时自动删除关联批次）
- 自动时间戳记录

---

## 🛠️ 常见问题

### 1. 扫码功能无法使用？

**原因**: 浏览器未获得摄像头权限或使用 HTTP 协议

**解决方案**:
- 确保使用 HTTPS 协议（本地测试可用 `localhost` 或 `127.0.0.1`）
- 检查浏览器设置，允许网站访问摄像头
- 尝试使用其他浏览器（Chrome/Safari 推荐）

### 2. 数据库连接失败？

**检查步骤**:
1. 确认 MySQL 服务正在运行
2. 验证 `db.php` 中的数据库配置是否正确
3. 检查数据库用户权限

### 3. 保存时提示错误？

**可能原因**:
- SKU 或商品名称为空
- 未添加批次或批次数据无效
- 数据库连接异常

---

## 📊 数据库结构

### products 表（商品基础信息）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT(11) | 主键，自增 |
| sku | VARCHAR(100) | 商品SKU/条形码（唯一） |
| name | VARCHAR(200) | 商品名称 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### batches 表（批次有效期）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT(11) | 主键，自增 |
| product_id | INT(11) | 关联商品ID（外键） |
| expiry_date | DATE | 到期日期 |
| quantity | INT(11) | 数量 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

---

## 🔒 安全建议

1. **生产环境配置**:
   - 关闭 PHP 错误显示（修改 `db.php` 中的 `error_reporting`）
   - 使用 HTTPS 证书
   - 设置强密码和数据库权限

2. **备份策略**:
   ```bash
   # 定期备份数据库
   mysqldump -u root -p expiry_system > backup_$(date +%Y%m%d).sql
   ```

3. **访问控制**（可选）:
   - 添加登录验证
   - 限制 IP 访问
   - 使用 .htaccess 保护目录

---

## 📝 后续优化建议

- [ ] 添加用户登录系统
- [ ] 批次编辑/删除功能
- [ ] 到期提醒通知
- [ ] 数据导出（Excel/CSV）
- [ ] 统计报表
- [ ] 多仓库支持
- [ ] 扫码历史记录

---

## 📞 技术支持

如遇到问题，请检查以下日志：

- **PHP 错误日志**: `/var/log/php/error.log`
- **Nginx 日志**: `/var/log/nginx/error.log`
- **MySQL 慢查询日志**: `/var/log/mysql/slow.log`

---

## 📄 许可证

本项目仅供学习和个人使用。

---

**部署日期**: 2026-02-15  
**版本**: v1.0.0  
**作者**: AI 助手
