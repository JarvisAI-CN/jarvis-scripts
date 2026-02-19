# NAS Node.js v22配置记录

**配置时间**: 2026-02-19 16:10 GMT+8
**目的**: 让NAS永久使用Node.js v22，避免每次手动设置PATH

---

## 问题背景

NAS上安装了多个Node.js版本：
- Node.js v14: `/volume1/@appstore/Node.js_v14/`
- Node.js v16: `/volume2/@appstore/Node.js_v16/`
- Node.js v20: `/volume2/@appstore/Node.js_v20/`
- Node.js v22: `/volume1/@appstore/Node.js_v22/` ✅

但系统默认使用Node.js v20，而OpenClaw需要 v22.12.0+

---

## 配置方案

### 1. 更新Shell配置文件

**~/.bashrc** (bash登录时加载)
```bash
# Node.js v22 - OpenClaw需要的版本
export PATH=/volume1/@appstore/Node.js_v22/usr/local/bin:$PATH

# npm全局包路径
export PATH=~/.npm-global/bin:$PATH
```

**~/.profile** (sh登录时加载)
```bash
# Node.js v22 - OpenClaw需要的版本
export PATH=/volume1/@appstore/Node.js_v22/usr/local/bin:$PATH

# npm全局包路径
export PATH=~/.npm-global/bin:$PATH
```

**~/.zshrc** (zsh登录时加载)
```bash
# Node.js v22 - OpenClaw需要的版本
export PATH=/volume1/@appstore/Node.js_v22/usr/local/bin:$PATH

# npm全局包路径
export PATH=~/.npm-global/bin:$PATH

# OpenClaw Completion
source "/var/services/homes/shuaishuai/.openclaw/completions/openclaw.zsh"
```

### 2. 备份文件
- `~/.bashrc.bak`
- `~/.zshrc.bak`

### 3. 启动脚本更新

**~/start-openclaw.sh**
```bash
#!/bin/bash
# OpenClaw启动脚本 - NAS版本
# 自动使用Node.js v22

# 加载.bashrc以获得Node.js v22
source ~/.bashrc

# 进入OpenClaw目录
cd /volume2/homes/shuaishuai/.openclaw

# 启动OpenClaw Gateway
echo "启动OpenClaw (Node $(node --version))..."
npx openclaw gateway >> /tmp/openclaw_startup.log 2>&1
```

---

## 验证方法

```bash
# SSH登录后直接运行（应该显示v22.19.0）
ssh shuaishuai@fsnas.top "node --version"

# 或用登录shell测试
ssh shuaishuai@fsnas.top "bash -lc 'node --version'"
```

**期望输出**: `v22.19.0`

---

## 使用方法

### 启动OpenClaw

**方法1: 使用启动脚本（推荐）**
```bash
ssh shuaishuai@fsnas.top
./start-openclaw.sh
```

**方法2: 手动启动**
```bash
ssh shuaishuai@fsnas.top
cd ~/.openclaw
npx openclaw gateway
```

---

## 效果

✅ 所有新SSH会话自动使用Node.js v22
✅ 无需手动设置PATH环境变量
✅ OpenClaw启动时自动使用正确的Node版本
✅ 当前OpenClaw进程继续正常运行（PID: 30805）

---

## 相关文件

- NAS配置: `/volume2/homes/shuaishuai/.bashrc`
- 启动脚本: `/volume2/homes/shuaishuai/start-openclaw.sh`
- OpenClaw目录: `/volume2/homes/shuaishuai/.openclaw/`
- 日志文件: `/tmp/openclaw/openclaw-*.log`

---

**配置完成时间**: 2026-02-19 16:12 GMT+8
**验证状态**: ✅ 通过
