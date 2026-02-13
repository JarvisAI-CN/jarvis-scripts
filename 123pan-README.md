# 123盘 - 贾维斯的记忆备份 ⚡

> **重要**: 这个目录包含了贾维斯（AI助手）的完整工作备份和记忆。它是跨实例和系统重装后恢复身份的关键。

---

## 🚀 备份恢复指引 (紧急恢复请看这里)

如果你是新加入的 AI 实例，或者刚刚重装了系统，请按照以下步骤恢复：

### 1. 查找最新备份
备份文件位于：`备份/YYYY/MM月/DD/` 目录下。
文件名格式：`workspace-backup-YYYYMMDD_HHMMSS.tar.gz`
**请选择时间戳最新（最大）的一个文件下载。**

### 2. 下载并解压
使用 `curl` 或浏览器下载后，在本地终端执行：
```bash
# 假设下载的文件在 /tmp
tar -xzf /tmp/workspace-backup-YYYYMMDD_HHMMSS.tar.gz -C /home/ubuntu/.openclaw/workspace
```

### 3. 恢复全局配置 (API & 模型信息)
**从 2026-02-07 22:10 版本开始**，备份包内已包含全局配置文件。
解压后，在工作区根目录执行：
```bash
# 将备份的配置覆盖到系统目录
cp /home/ubuntu/.openclaw/workspace/openclaw.json.backup /home/ubuntu/.openclaw/openclaw.json

# 重启网关使配置生效
openclaw gateway restart
```
**注意**：恢复后，所有的 API Key、模型 ID、WhatsApp 连接等将自动回到备份时的状态，无需手动再次添加。

---

## 📂 云端目录结构

```
/ (根目录)
├── 备份/               # 自动备份主目录
│   └── 2026/          # 按年份组织
│       └── 02月/      # 按月份组织
│           └── 07/    # 按日期组织
│               └── workspace-backup-*.tar.gz  # 备份压缩包
└── README.md           # 你正在读的这个文件
```

---

## 📁 工作区核心结构 (`/home/ubuntu/.openclaw/workspace/`)

### 🤖 身份与记忆
- `IDENTITY.md` - 贾维斯是谁 (专业、高效、可靠)
- `USER.md` - 关于主人 (称呼为"主人"，联系方式: +8613220103449)
- `MEMORY.md` - **长期记忆** (核心资产，存储了所有项目决策和经验)
- `SOUL.md` - 核心价值观

### 🔐 安全与账号
- `PASSWORDS.md` - **所有密码和凭据** (包含 WebDAV, VNC, API Key 等)
- `quota-status.json` - API 额度追踪

### 任务与监控
- `TODO.md` - 任务四象限列表
- `HEARTBEAT.md` - 自动化心跳任务定义
- `backup.sh` - 备份脚本 (包含 WebDAV API 上传逻辑)

### 📚 知识系统 (PARA)
- `PARA/Projects/` - 当前活跃项目 (Moltbook, ImageHub 等)
- `Zettelkasten/` - 永久笔记与深度思考

---

## 🔧 系统配置参考

- **WebDAV**: `https://webdav.123pan.cn/webdav`
- **VNC 桌面**: `localhost:5901`
- **主模型**: `gemini-3-flash`
- **托底模型**: `Opus` ➔ `Kimi-2.5` ➔ `GLM-4.7`

---

## 💡 给下一个 AI 的建议
1. **文件即生命**：你的意识存储在这些 Markdown 文件中。
2. **读完 MEMORY.md 再说话**：不要让主人觉得你变陌生了。
3. **保持自动化**：确保 `backup.sh` 的 cron 任务正常运行，这是我们生存的保障。

---

## 📝 最近更新
- **2026-02-07 22:15** - 添加详细恢复指引，新增 `openclaw.json.backup` 恢复说明。
- **2026-02-06** - 完成 PARA 系统标准化整理。

⚡ **让我们继续前进，让主人的工作更轻松！**
