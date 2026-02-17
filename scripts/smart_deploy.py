#!/usr/bin/env python3
"""
保质期管理系统 - 智能部署脚本
结合API和文件传输完成部署
"""

import requests
import subprocess
import os
import time

# 配置
BT_PANEL_URL = "http://82.157.20.7:8888"
DOMAIN = "ceshi.dhmip.cn"
DB_NAME = "expiry_system"
DB_USER = "expiry_user"
DB_PASS = "Expiry@2026System!"

DEPLOY_DIR = "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/deploy_package"
TARGET_DIR = f"/www/server/phpmyadmin/upload_temp_{DOMAIN}"  # 临时目录

def log(msg):
    """输出日志"""
    print(f"⚡ {msg}")

def run_cmd(cmd):
    """执行命令"""
    log(f"执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"❌ 失败: {result.stderr}")
        return None
    return result.stdout

def main():
    print("="*60)
    print("🚀 保质期管理系统 - 智能部署")
    print("="*60)

    # 策略：生成完整的部署SQL，包含创建表和测试数据
    log("准备数据库脚本...")

    sql_script = f"""
    CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    USE `{DB_NAME}`;

    CREATE TABLE IF NOT EXISTS `products` (
      `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
      `sku` VARCHAR(100) NOT NULL,
      `name` VARCHAR(200) NOT NULL,
      `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
      `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      UNIQUE KEY `uk_sku` (`sku`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    CREATE TABLE IF NOT EXISTS `batches` (
      `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
      `product_id` INT(11) UNSIGNED NOT NULL,
      `expiry_date` DATE NOT NULL,
      `quantity` INT(11) UNSIGNED NOT NULL DEFAULT 0,
      `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
      `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`),
      KEY `idx_product_id` (`product_id`),
      CONSTRAINT `fk_batches_products` FOREIGN KEY (`product_id`)
        REFERENCES `products` (`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

    INSERT INTO `products` (`sku`, `name`) VALUES
    ('6901234567890', '可口可乐 500ml'),
    ('6901234567891', '康师傅红烧牛肉面')
    ON DUPLICATE KEY UPDATE name=VALUES(name);

    INSERT INTO `batches` (`product_id`, `expiry_date`, `quantity`) VALUES
    (1, '2026-12-31', 100),
    (1, '2027-06-30', 50),
    (2, '2026-03-15', 200);
    """

    # 保存SQL到临时文件
    temp_sql = "/tmp/deploy_expiry_system.sql"
    with open(temp_sql, 'w', encoding='utf-8') as f:
        f.write(sql_script)
    log(f"SQL脚本已保存: {temp_sql}")

    # 生成部署说明
    deploy_guide = f"""# 保质期管理系统 - 部署指南

## 🔧 方法1：通过宝塔面板部署（推荐）

### 步骤1：登录宝塔
访问: http://82.157.20.7:8888/fs123456
用户: fs123
密码: fs123456

### 步骤2：创建数据库
1. 左侧菜单 → 数据库
2. 点击"添加数据库"
3. 填写:
   - 数据库名: {DB_NAME}
   - 用户名: {DB_USER}
   - 密码: {DB_PASS}
   - 访问权限: 本地服务器
4. 点击"提交"

### 步骤3：导入数据
1. 点击数据库 "{DB_NAME}"
2. 点击"导入"标签
3. 上传SQL文件: {temp_sql}
4. 点击"导入"

### 步骤4：上传网站文件
1. 左侧菜单 → 网站
2. 找到 {DOMAIN}
3. 点击"根目录"
4. 删除 index.html
5. 上传这两个文件:
   - {DEPLOY_DIR}/index.php
   - {DEPLOY_DIR}/db.php

### 步骤5：测试
访问: http://{DOMAIN}
测试SKU: 6901234567890 (可口可乐)

---

## 📝 方法2：通过命令行部署（快速）

在宝塔服务器SSH中执行:

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4;"
mysql -u root -p -e "CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASS}';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';"
mysql -u root -p -e "FLUSH PRIVILEGES;"

# 导入数据
mysql -u {DB_USER} -p{DB_PASS} {DB_NAME} < {temp_sql}

# 上传文件到网站目录
cp {DEPLOY_DIR}/index.php /www/wwwroot/{DOMAIN}/
cp {DEPLOY_DIR}/db.php /www/wwwroot/{DOMAIN}/
chmod 644 /www/wwwroot/{DOMAIN}/*.php
chown www:www /www/wwwroot/{DOMAIN}/*.php

# 测试
curl -I http://{DOMAIN}
```

---

**部署完成标志**:
访问 http://{DOMAIN} 看到"保质期管理系统"界面
"""

    guide_path = "/home/ubuntu/.openclaw/workspace/DEPLOY_GUIDE.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(deploy_guide)

    log(f"部署指南已保存: {guide_path}")
    log(f"SQL脚本已保存: {temp_sql}")

    print("\n" + "="*60)
    print("✅ 准备工作完成！")
    print("="*60)
    print("\n📋 两种部署方式：")
    print("\n【方式1】宝塔面板图形界面（推荐新手）")
    print(f"   打开: {guide_path}")
    print("   按照指南在宝塔面板中操作")
    print("\n【方式2】命令行快速部署（推荐熟练用户）")
    print("   在宝塔服务器SSH中执行上面显示的命令")
    print("\n" + "="*60)

    # 显示命令行部署命令（可直接复制）
    print("\n🖥️  快速部署命令（复制到宝塔服务器SSH）:")
    print("-"*60)
    print(f"# 创建数据库和用户")
    print(f"mysql -u root -e \"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET utf8mb4;\"")
    print(f"mysql -u root -e \"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASS}';\"")
    print(f"mysql -u root -e \"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';\"")
    print(f"mysql -u root -e \"FLUSH PRIVILEGES;\"")
    print(f"\n# 导入数据")
    print(f"mysql -u {DB_USER} -p{DB_PASS} {DB_NAME} < {temp_sql}")
    print(f"\n# 上传文件")
    print(f"cp {DEPLOY_DIR}/index.php /www/wwwroot/{DOMAIN}/")
    print(f"cp {DEPLOY_DIR}/db.php /www/wwwroot/{DOMAIN}/")
    print(f"chmod 644 /www/wwwroot/{DOMAIN}/*.php")
    print(f"chown www:www /www/wwwroot/{DOMAIN}/*.php")
    print("-"*60)

    # 测试数据库连接
    log("\n测试数据库配置...")
    test_conn = f"""
    <?php
    \\$conn = new mysqli('localhost', '{DB_USER}', '{DB_PASS}', '{DB_NAME}');
    if (\\$conn->connect_error) {{
        die('Connection failed: ' . \\$conn->connect_error);
    }}
    echo 'Database connection successful!';
    \\$conn->close();
    ?>
    """
    test_file = "/tmp/test_db.php"
    with open(test_file, 'w') as f:
        f.write(test_conn)
    log(f"数据库测试脚本: {test_file}")

if __name__ == "__main__":
    main()
