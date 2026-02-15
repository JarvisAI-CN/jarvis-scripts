# 保质期管理系统 - 快速部署指南 ⚡

**预计时间**: 2分钟
**难度**: ⭐ 简单

---

## 🚀 一键部署（推荐）

### 方式1：复制命令到宝塔终端（最快）

1. **打开宝塔面板终端**
   - 登录宝塔: http://82.157.20.7:8888/fs123456
   - 左侧菜单 → 终端
   - 或使用SSH客户端连接到服务器

2. **复制粘贴以下命令**:
```bash
bash <(curl -s https://raw.githubusercontent.com/JarvisAI-CN/jarvis-scripts/main/one_click_deploy.sh)
```

3. **等待部署完成**（约1分钟）

4. **测试访问**:
   ```
   http://ceshi.dhmip.cn
   ```

---

### 方式2：手动复制脚本（备用）

如果方式1失败，使用本地脚本：

```bash
# 在宝塔服务器SSH中执行
bash /home/ubuntu/.openclaw/workspace/scripts/one_click_deploy.sh
```

---

## 📋 部署脚本做了什么？

### 自动化步骤：
1. ✅ 创建数据库 `expiry_system`
2. ✅ 创建数据库用户 `expiry_user`
3. ✅ 导入表结构和测试数据
4. ✅ 清理网站默认文件
5. ✅ 上传PHP文件（index.php, db.php）
6. ✅ 设置文件权限
7. ✅ 测试网站访问
8. ✅ 测试数据库连接

---

## 🧪 测试账号

部署完成后访问 `http://ceshi.dhmip.cn`，使用以下测试数据：

```
SKU: 6901234567890 → 可口可乐 500ml
  批次1: 2026-12-31 (100瓶)
  批次2: 2027-06-30 (50瓶)

SKU: 6901234567891 → 康师傅红烧牛肉面
  批次1: 2026-03-15 (200包)
```

---

## ⚠️ 常见问题

### Q1: 命令执行失败？
**解决**:
- 确认在宝塔服务器SSH中执行
- 检查脚本权限: `chmod +x one_click_deploy.sh`
- 手动执行各步骤（见下面"手动部署"）

### Q2: 数据库连接失败？
**解决**:
```bash
# 测试数据库连接
mysql -u expiry_user -pExpiry@2026System! expiry_system

# 如果失败，重新创建
mysql -u root -e "DROP DATABASE expiry_system;"
bash one_click_deploy.sh
```

### Q3: 网站显示默认页面？
**解决**:
```bash
# 检查文件
ls -lh /www/wwwroot/ceshi.dhmip.cn/

# 应该有:
# index.php (44KB)
# db.php (2.5KB)
```

### Q4: 扫码无法启动？
**原因**: HTTP环境限制摄像头访问
**解决**: 申请SSL证书（宝塔面板 → 网站 → SSL → Let's Encrypt）

---

## 📱 移动端使用（HTTPS配置）

如需手机扫码功能：

1. **在宝塔面板中**:
   - 网站 → ceshi.dhmip.cn → SSL
   - 选择 "Let's Encrypt"
   - 点击 "申请"

2. **强制HTTPS**:
   - SSL设置 → 开启"强制HTTPS"

3. **手机访问**:
   ```
   https://ceshi.dhmip.cn
   ```

4. **允许摄像头权限**并测试扫码

---

## 🎯 部署检查清单

部署完成后检查：
- [ ] 访问 http://ceshi.dhmip.cn 显示系统界面
- [ ] 测试SKU能查询到商品（6901234567890）
- [ ] 能添加新批次
- [ ] 能删除批次
- [ ] 到期提醒显示正常

---

## 📞 需要帮助？

**部署问题**:
- 检查部署日志: 网站日志 → 错误日志
- 查看PHP配置: 网站设置 → PHP版本

**功能问题**:
- 查看数据库: phpMyAdmin → expiry_system
- 重置数据: 重新执行 `database.sql`

---

**脚本位置**: `/home/ubuntu/.openclaw/workspace/scripts/one_click_deploy.sh`

**详细日志**: `/home/ubuntu/.openclaw/workspace/deploy_*.log`

---

**准备好开始了吗？复制上面的命令，2分钟完成部署！** ⚡
