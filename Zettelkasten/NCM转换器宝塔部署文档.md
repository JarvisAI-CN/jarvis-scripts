# NCM转换器v3.1 - 宝塔面板部署文档

**部署时间**: 2026-02-14 18:55
**部署人**: 贾维斯 (智谱GLM-4.7)
**状态**: ✅ 测试通过，准备部署

---

## 🧪 测试结果

### ✅ 本地测试通过

**Web应用测试**:
- ✅ 页面访问成功 (状态码: 200)
- ✅ 页面标题正确
- ✅ UI界面正常显示

**转换功能测试**:
- ✅ 文件上传成功 (113.08 MB NCM)
- ✅ 转换成功 (113.19 MB FLAC)
- ✅ 文件下载成功
- ✅ 格式验证正确 (FLAC无损)

**性能测试**:
- 转换时间: <1秒
- 文件大小: 113MB
- 网络传输: 正常

---

## 📦 应用信息

### Web应用
- **文件**: `/home/ubuntu/.openclaw/workspace/scripts/ncm_web_app.py`
- **端口**: 5000
- **进程**: 715722, 715726
- **状态**: ✅ 运行中

### 依赖
- Python 3.12
- Flask 3.0.2
- ncmdump (转换后端)

### 测试脚本
- **文件**: `/home/ubuntu/.openclaw/workspace/scripts/test_ncm_web.py`
- **结果**: ✅ 全部通过

---

## 🚀 宝塔面板部署步骤

### 1. 登录宝塔面板

```
地址: http://82.157.20.7:8888/fs123456
用户名: 见PASSWORDS.md
密码: 见PASSWORDS.md
```

### 2. 创建网站

**操作**:
1. 点击"网站" → "添加站点"
2. 域名: `ncm.dhmip.cn`
3. 根目录: `/www/wwwroot/ncm.dhmip.cn`
4. PHP版本: 纯静态
5. 点击"提交"

### 3. 配置反向代理

**操作**:
1. 找到创建的网站 `ncm.dhmip.cn`
2. 点击"设置" → "反向代理"
3. 点击"添加反向代理"

**配置**:
```
代理名称: NCM转换器
目标URL: http://127.0.0.1:5000
发送域名: $host
```

**高级配置** (可选):
```nginx
location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;

    # 上传文件大小限制
    client_max_body_size 500M;

    # 超时设置
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
```

### 4. 启用SSL证书

**操作**:
1. 网站设置 → "SSL"
2. 选择"Let's Encrypt"
3. 点击"申请"
4. 开启"强制HTTPS"

### 5. 测试访问

**测试URL**:
- HTTP: `http://ncm.dhmip.cn`
- HTTPS: `https://ncm.dhmip.cn`

**预期结果**:
- ✅ 显示NCM转FLAC转换器界面
- ✅ 可以上传NCM文件
- ✅ 转换成功并下载FLAC

---

## 🔧 应用管理

### 启动应用

```bash
# 使用启动脚本
bash /home/ubuntu/.openclaw/workspace/scripts/start_ncm_web.sh

# 或手动启动
cd /home/ubuntu/.openclaw/workspace/scripts
python3 ncm_web_app.py &
```

### 停止应用

```bash
pkill -f "ncm_web_app.py"
```

### 重启应用

```bash
pkill -f "ncm_web_app.py"
sleep 2
bash /home/ubuntu/.openclaw/workspace/scripts/start_ncm_web.sh
```

### 查看日志

```bash
# 应用日志
tail -f /var/log/syslog | grep ncm_web_app

# Nginx日志
tail -f /www/wwwlogs/ncm.dhmip.cn.log
```

### 设置开机自启

```bash
# 创建systemd服务
sudo cp /tmp/ncm-converter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ncm-converter.service
sudo systemctl start ncm-converter.service
```

---

## 📊 监控和维护

### 状态检查

```bash
# 检查进程
ps aux | grep ncm_web_app

# 检查端口
lsof -Pi :5000 -sTCP:LISTEN -t

# 检查Web服务
curl -I http://localhost:5000
```

### 日志清理

```bash
# 清理临时文件
rm -rf /tmp/ncm_web_uploads/*
rm -rf /tmp/ncm_web_output/*
```

### 更新应用

```bash
# 停止应用
pkill -f "ncm_web_app.py"

# 更新代码
cd /home/ubuntu/.openclaw/workspace/scripts
git pull

# 重启应用
bash start_ncm_web.sh
```

---

## 🌐 访问方式

### 本地测试
- **地址**: `http://localhost:5000`
- **用途**: 开发和测试

### 公网访问
- **域名**: `ncm.dhmip.cn`
- **HTTPS**: `https://ncm.dhmip.cn`
- **用途**: 生产环境

### VNC访问
- **VNC**: `http://服务器IP:6080/vnc.html`
- **Chrome**: `http://localhost:5000`
- **用途**: 图形界面测试

---

## 💡 功能特性

### Web界面
- ✅ 简洁美观的UI设计
- ✅ 拖拽上传NCM文件
- ✅ 实时转换进度
- ✅ 自动下载FLAC文件

### 转换功能
- ✅ 支持CTEN和CTCN格式
- ✅ 无损FLAC输出
- ✅ 自动格式检测
- ✅ 大文件支持（最大500MB）

### 性能优化
- ✅ 转换速度极快（<1秒）
- ✅ 异步文件处理
- ✅ 临时文件自动清理

---

## 🔐 安全建议

### 已实现
- ✅ 文件大小限制（500MB）
- ✅ 文件类型验证（.ncm）
- ✅ 临时文件隔离
- ✅ 错误处理

### 可选增强
- 🔐 访问密码保护
- 🔐 IP白名单
- 🔐 速率限制
- 🔐 HTTPS强制跳转

---

## 📝 故障排查

### 问题1: 端口5000被占用

**症状**: 启动失败，端口已被占用

**解决**:
```bash
# 查找占用进程
lsof -Pi :5000 -sTCP:LISTEN

# 停止旧进程
pkill -f "ncm_web_app.py"

# 重启应用
bash /home/ubuntu/.openclaw/workspace/scripts/start_ncm_web.sh
```

### 问题2: 反向代理502错误

**症状**: 网站访问502 Bad Gateway

**解决**:
1. 检查应用是否运行: `ps aux | grep ncm_web_app`
2. 检查端口是否监听: `lsof -Pi :5000 -sTCP:LISTEN`
3. 检查反向代理配置: 目标URL `http://127.0.0.1:5000`
4. 查看Nginx错误日志: `/www/wwwlogs/ncm.dhmip.cn.log`

### 问题3: 转换失败

**症状**: 上传成功但转换失败

**解决**:
1. 检查ncmdump是否安装: `which ncmdump`
2. 检查文件是否损坏: 上传其他NCM文件测试
3. 查看应用日志: 检查Python错误输出

### 问题4: SSL证书申请失败

**症状**: Let's Encrypt证书申请失败

**解决**:
1. 检查域名DNS是否解析正确
2. 检查80端口是否开放
3. 检查防火墙规则
4. 手动申请证书或使用其他CA

---

## ✅ 部署检查清单

### 部署前
- [x] 本地测试通过
- [x] Web应用正常运行
- [x] 转换功能正常
- [x] 依赖已安装

### 部署中
- [ ] 创建网站
- [ ] 配置反向代理
- [ ] 申请SSL证书
- [ ] 测试访问

### 部署后
- [ ] 验证HTTP访问
- [ ] 验证HTTPS访问
- [ ] 测试转换功能
- [ ] 检查日志正常

---

## 📞 支持和反馈

### 问题反馈
- 飞书: 主人
- GitHub Issues: https://github.com/JarvisAI-CN/jarvis-scripts/issues

### 更新日志
- v3.1: 使用ncmdump后端，重写成功
- v3.0: 自己实现解密算法，性能问题
- v2.0: 支持CTEN格式，仍有bug
- v1.0: 初始版本，只支持CTCN

---

**部署完成时间**: 2026-02-14 18:55
**测试状态**: ✅ 通过
**准备状态**: ✅ 可部署
