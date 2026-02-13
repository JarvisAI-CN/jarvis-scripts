# VNC桌面连接指南

**主人**: JarvisAI-CN
**时间**: 2026-02-06 15:30 GMT+8

---

## 🖥️ VNC桌面信息

**VNC服务器**: TightVNC或TigerVNC
**端口**: 5901
**密码**: 见PASSWORDS.md

---

## 📋 连接方式

### 方式1: VNC Viewer（推荐）
1. 下载VNC Viewer: https://www.realvnc.com/en/connect/download/viewer/
2. 安装并打开VNC Viewer
3. 输入地址: `服务器IP:5901`
   - 例如: `82.157.20.7:5901`
4. 输入密码（见PASSWORDS.md）
5. 连接 ✅

### 方式2: 浏览器VNC客户端
访问: http://82.157.20.7:5901（如果支持noVNC）

### 方式3: SSH隧道 + VNC
```bash
# 本地执行
ssh -L 5901:localhost:5901 root@82.157.20.7
# 然后用VNC Viewer连接 localhost:5901
```

---

## 🔍 检查VNC状态

**当前检查**:
- [ ] VNC进程运行状态
- [ ] 端口监听状态
- [ ] 防火墙配置

---

**正在检查中...**
