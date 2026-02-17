# 保质期管理系统 - VNC调试指南

**部署时间**: 2026-02-17 11:23
**访问地址**: http://localhost:8081
**VNC端口**: 5901

---

## ✅ 已完成

1. **Web服务部署**
   - 目录: `/var/www/html/expiry`
   - Nginx配置: 端口8081
   - PHP 8.3.6 ✅

2. **数据库准备**
   - 数据库: `expiry_system` ✅
   - 字符集: utf8mb4_unicode_ci ✅

3. **文件部署**
   - 所有PHP文件已复制 ✅
   - 可通过 http://localhost:8081 访问 ✅

---

## 🖥️ VNC访问方式

### 方法1: 使用VNC Viewer（推荐）
1. 下载VNC Viewer: https://www.realvnc.com/download/viewer/
2. 连接: `<服务器IP>:5901`
3. 密码: 见 PASSWORDS.md

### 方法2: 通过浏览器（需要主人开启端口转发）
```bash
# 在主人本地执行
ssh -L 5901:localhost:5901 ubuntu@<服务器IP>
```
然后打开 VNC Viewer 连接 localhost:5901

### 方法3: 使用noVNC（如果已安装）
访问: http://<服务器IP>:6080/vnc.html

---

## 🌐 在VNC中操作

1. **打开Firefox**
   - 地址栏输入: `http://localhost:8081`
   - 会自动跳转到安装向导

2. **安装步骤**
   - 填写数据库信息
   - Host: `localhost`
   - Database: `expiry_system`
   - User: `root`
   - Password: 见 PASSWORDS.md

3. **功能测试**
   - 扫码功能
   - 预警系统
   - 任务管理
   - 管理员控制台

---

## 🐛 调试重点

### 核心功能
- [ ] 扫码识别（手机浏览器测试）
- [ ] 批量盘点（暂存队列）
- [ ] 过期预警（7/15/30天）
- [ ] 任务自动生成
- [ ] 管理员后台

### 已知问题检查
- 数据库连接是否正常
- API接口返回格式
- 前端JavaScript错误
- 移动端适配

---

## 📝 备注

VNC服务器已在运行（Display :1）
Firefox启动需要图形环境

建议使用VNC Viewer直接连接，体验最佳。
