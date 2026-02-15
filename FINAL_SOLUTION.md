# 保质期管理系统 - 终极部署方案

**当前状态**: VNC自动化已完成所有尝试，现在需要最后一步

---

## 🎯 问题分析

HTTP 403错误可能原因：
1. index.php未真正上传到宝塔服务器
2. PHP-FPM需要重启
3. 文件权限问题

---

## ✅ 解决方案（按优先级）

### 方案A：在宝塔终端手动执行（最可靠）

在宝塔面板 → 终端中执行：

```bash
cd /www/wwwroot/ceshi.dhmip.cn && curl -s http://10.7.0.5:8888/index.php -o index.php && curl -s http://10.7.0.5:8888/db.php -o db.php && chmod 644 *.php && chown www:www *.php && echo "✅ 完成" && ls -lh
```

### 方案B：重启PHP服务

在宝塔面板 → 软件商店 → PHP 8.3 → 重启

然后刷新: http://ceshi.dhmip.cn

### 方案C：检查文件

在宝塔面板 → 网站 → ceshi.dhmip.cn → 文件

确认文件列表有：
- index.php (46KB)
- db.php (2.5KB)

---

## 🧪 验证部署

完成后访问: http://ceshi.dhmip.cn

测试SKU:
- 6901234567890 → 可口可乐 500ml
- 6901234567891 → 康师傅红烧牛肉面

---

**推荐方案A，一条命令搞定！** ⚡
