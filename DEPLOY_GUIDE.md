# 保质期管理系统 - 部署指南

## 🔧 方法1：通过宝塔面板部署（推荐）

### 步骤1：登录宝塔
访问: http://82.157.20.7:8888/fs123456
用户: fs123
密码: fs123456

### 步骤2：创建数据库
1. 左侧菜单 → 数据库
2. 点击"添加数据库"
3. 填写:
   - 数据库名: expiry_system
   - 用户名: expiry_user
   - 密码: Expiry@2026System!
   - 访问权限: 本地服务器
4. 点击"提交"

### 步骤3：导入数据
1. 点击数据库 "expiry_system"
2. 点击"导入"标签
3. 上传SQL文件: /tmp/deploy_expiry_system.sql
4. 点击"导入"

### 步骤4：上传网站文件
1. 左侧菜单 → 网站
2. 找到 ceshi.dhmip.cn
3. 点击"根目录"
4. 删除 index.html
5. 上传这两个文件:
   - /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/index.php
   - /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/db.php

### 步骤5：测试
访问: http://ceshi.dhmip.cn
测试SKU: 6901234567890 (可口可乐)

---

## 📝 方法2：通过命令行部署（快速）

在宝塔服务器SSH中执行:

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS expiry_system DEFAULT CHARACTER SET utf8mb4;"
mysql -u root -p -e "CREATE USER IF NOT EXISTS 'expiry_user'@'localhost' IDENTIFIED BY 'Expiry@2026System!';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON expiry_system.* TO 'expiry_user'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"

# 导入数据
mysql -u expiry_user -pExpiry@2026System! expiry_system < /tmp/deploy_expiry_system.sql

# 上传文件到网站目录
cp /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/index.php /www/wwwroot/ceshi.dhmip.cn/
cp /home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package/db.php /www/wwwroot/ceshi.dhmip.cn/
chmod 644 /www/wwwroot/ceshi.dhmip.cn/*.php
chown www:www /www/wwwroot/ceshi.dhmip.cn/*.php

# 测试
curl -I http://ceshi.dhmip.cn
```

---

**部署完成标志**:
访问 http://ceshi.dhmip.cn 看到"保质期管理系统"界面
