# VNC连接方法大全

**主人**: JarvisAI-CN
**时间**: 2026-02-06 15:47 GMT+8

---

## 🔗 方法1: noVNC（浏览器）⭐ 推荐

### 访问地址
```
http://82.157.20.7:6080/vnc.html
```

### 优点
- ✅ 无需安装客户端
- ✅ 浏览器直接访问
- ✅ 跨平台（Windows/Mac/Linux/手机）
- ✅ 支持现代浏览器

### 使用方法
1. 打开浏览器（Chrome/Firefox/Edge/Safari）
2. 访问: `http://82.157.20.7:6080/vnc.html`
3. 输入密码: `123456`
4. 连接 ✅

---

## 🔗 方法2: Remmina（Linux）

### 安装
```bash
dnf install -y remmina remmina-plugins-vnc
```

### 使用
1. 打开Remmina
2. 新建VNC连接
3. 服务器: `82.157.20.7:5901`
4. 密码: `123456`

---

## 🔗 方法3: VNC Viewer（官方）

### Windows/Mac/Linux
- 下载: https://www.realvnc.com/en/connect/download/viewer/
- 连接: `82.157.20.7:5901`

---

## 🔗 方法4: SSH隧道 + VNC（更安全）

### 步骤
```bash
# 在您的本地电脑执行
ssh -L 5901:localhost:5901 root@82.157.20.7

# 然后用VNC Viewer连接
localhost:5901
```

### 优点
- ✅ 加密传输
- ✅ 更安全
- ✅ 绕过防火墙

---

## 🔗 方法5: Chrome Remote Desktop（第三方）

### 使用Chrome浏览器扩展
1. 安装Chrome Remote Desktop扩展
2. 需要在VNC桌面内安装Chrome
3. 设置远程访问

---

## 🔗 方法6: 手机APP

### Android
- **VNC Viewer**: RealVNC官方
- **BVNC**: 开源免费
- **aVNC**: 轻量级

### iOS
- **VNC Viewer**: RealVNC官方
- **Mocha VNC**: 付费

---

## 📊 推荐方案

### 🏆 最方便: noVNC（浏览器）
**直接用浏览器访问，无需安装任何软件**

### 🔒 最安全: SSH隧道 + VNC Viewer
**加密传输，适合长期使用**

### 📱 移动端: VNC Viewer手机APP
**随时随地连接**

---

## ✅ 当前状态

**noVNC**: ✅ 已安装并启动
**访问地址**: http://82.157.20.7:6080/vnc.html

**VNC服务器**: ✅ 运行中
**端口**: 5901
**密码**: 123456

---

**主人，最方便的是直接用浏览器访问 http://82.157.20.7:6080/vnc.html !**
