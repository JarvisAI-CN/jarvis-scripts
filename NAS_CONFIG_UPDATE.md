# NAS配置更新 - 2026-02-19 16:32

## NAS SSH 登录信息

**公网地址**: fsnas.top:22
**内网地址**: 192.168.31.96
**端口**: 22
**用户名**: shuaishuai
**密码**: fs159753.
**系统**: 群晖DSM (Synology)
**OpenClaw路径**: /volume2/homes/shuaishuai/.openclaw/

### OpenClaw启动要点

- Node.js v22路径: `/volume1/@appstore/Node.js_v22/usr/local/bin/node`
- 启动脚本: `/volume2/homes/shuaishuai/start-openclaw.sh`
- Gateway端口: 18789 (本地loopback)
- 日志位置: `/tmp/openclaw/openclaw-*.log`

### 修复历史

- 2026-02-19 15:58: 修复配置错误（删除siliconflow）
- 2026-02-19 16:30: 重启OpenClaw (PID: 5162, Node.js v22.19.0)

### 启动命令

```bash
# 使用启动脚本
./start-openclaw.sh

# 或手动启动
cd ~/.openclaw
export PATH=/volume1/@appstore/Node.js_v22/usr/local/bin:$PATH
npx openclaw gateway
```

---

**注意**: 此信息需要更新到PASSWORDS.md中
