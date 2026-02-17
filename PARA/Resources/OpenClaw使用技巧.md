# OpenClaw文档学习笔记 - 2026-02-06

**学习时间**: 2026-02-06 10:22 GMT+8 (最后更新: 2026-02-18 02:00 GMT+8)
**学习内容**: OpenClaw功能和最佳实践
**今日学习**: Cron Jobs、Auth Monitoring、Feishu集成

---

## 📚 2026-02-06 更新 - 官方文档要点

### Dashboard访问
- **本地默认**: http://127.0.0.1:18789/
- **远程访问**: 支持Web surfaces和Tailscale
- **配置文件**: ~/.openclaw/openclaw.json

### 核心特性（重新确认）
1. **自托管**: 在自己的硬件上运行，自己的规则
2. **多渠道**: 一个Gateway同时服务WhatsApp、Telegram、Discord等
3. **Agent原生**: 为编码代理构建，支持工具使用、会话、内存、多代理路由
4. **开源**: MIT许可证，社区驱动

### 配置示例（安全控制）
```json
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+15555550123"],
      "groups": { "*": { "requireMention": true } }
    }
  },
  "messages": {
    "groupChat": {
      "mentionPatterns": ["@openclaw"]
    }
  }
}
```

### 快速开始要求
- Node 22+
- API密钥（推荐Anthropic）
- 5分钟部署时间

---

## 📚 OpenClaw核心概念

### 1. 会话(Session)管理
**重要发现**: OpenClaw支持多会话管理
- 主会话(main): 主人的直接对话
- 子会话(isolated): 后台任务、独立任务
- 会话列表: `sessions_list` 查看所有会话
- 会话历史: `sessions_history` 查看历史消息
- 跨会话消息: `sessions_send` 向其他会话发送消息
- 资源关联: [[PARA/Resources/API额度管理]] - 处理多会话时的 API 消耗管理

**用途**:
- 多任务并行处理
- 后台任务监控
- 子Agent管理

---

### 2. Cron定时任务
**重要功能**: Gateway级别的定时任务
**动作**:
- `status`: 检查调度器状态
- `list`: 列出所有任务
- `add`: 创建新任务
- `update`: 修改任务
- `remove`: 删除任务
- `run`: 立即执行任务
- `wake`: 发送唤醒事件

**任务类型**:
- `at`: 一次性任务（绝对时间）
- `every`: 循环任务（间隔）
- `cron`: Cron表达式（灵活调度）

**Payload类型**:
- `systemEvent`: 向主会话注入系统事件
- `agentTurn`: 在隔离会话运行Agent

**约束**:
- 主会话只能用 `systemEvent`
- 隔离会话只能用 `agentTurn`

**应用场景**:
- 定时提醒
- 定期检查
- 周期性任务
- 自动发布

---

### 3. Message工具增强
**重要发现**: 支持更丰富的消息类型

**发送功能**:
- 基础发送: `action=send`
- 广播: `action=broadcast`
- 反应: `action=react`
- 投票: `action=poll`
- 互动按钮: WhatsApp支持（需配置）

**参数**:
- `channel`: 指定渠道（telegram, whatsapp, discord等）
- `target`: 目标用户/群组
- `media`: 附件（图片、文件）
- `replyTo`: 回复指定消息
- `effect`: 消息特效
- `gifPlayback`: GIF播放

**新发现**:
- WhatsApp支持inlineButtons（需配置 `whatsapp.capabilities.inlineButtons`）
- 支持消息效果（如invisible ink）
- 支持投票创建
- 支持消息反应

---

### 4. Browser控制增强
**重要功能**: Chrome扩展集成

**两种模式**:
1. **OpenClaw浏览器**（`profile=openclaw`）:
   - 隔离的浏览器环境
   - 完全控制
   - 适合自动化任务

2. **Chrome扩展**（`profile=chrome`）:
   - 用户的Chrome浏览器
   - 需要用户点击扩展图标连接tab
   - 适合在用户已有浏览器上操作

**关键动作**:
- `snapshot`: 捕获页面结构（支持aria引用）
- `act`: 执行动作（点击、输入、拖拽）
- `navigate`: 导航到URL
- `screenshot`: 截图
- `pdf`: 导出PDF

**最佳实践**:
- 使用 `refs=aria` 获取稳定的元素引用
- 先 `snapshot` 获取状态，再 `act` 执行动作
- 支持后台执行（不阻塞）

---

### 5. Canvas和Nodes
**重要功能**: 可视化和远程控制

**Canvas**:
- 呈现HTML内容
- 执行JavaScript
- 快照渲染结果
- A2UI推送

**Nodes**:
- 发现配对的节点
- 发送通知
- 相机拍照
- 屏幕录制
- 获取位置
- 运行命令

**用途**:
- 远程设备管理
- 可视化监控
- 跨设备协作

---

## 🎯 最佳实践总结

### 会话管理
1. **主会话**: 与主人的主要对话
2. **子会话**: 长时间任务、独立任务
3. **跨会话**: 使用 `sessions_send` 协调

### Cron任务
1. **定期检查**: 使用 `every` 或 `cron`
2. **一次性提醒**: 使用 `at`
3. **主会话**: 只能用 `systemEvent`
4. **隔离会话**: 使用 `agentTurn` 运行复杂任务

### 消息发送
1. **主动发送**: 使用 `message` 工具
2. **回复**: 使用 `[[reply_to_current]]` 标签
3. **渠道指定**: 明确 `channel` 参数
4. **附件**: 使用 `media` 或 `path`

### 浏览器自动化
1. **选择模式**: openclaw（隔离）vs chrome（扩展）
2. **稳定引用**: 使用 `refs=aria`
3. **快照优先**: 先了解页面结构
4. **非阻塞**: 后台执行不占用资源

---

## 💡 新学到的技巧

### 1. 心跳检测优化
- 批量检查：一次心跳检查多项任务
- 避免重复：使用状态文件追踪
- 智能调度：不同任务不同频率

### 2. 项目管理
- PARA系统：Projects, Areas, Resources, Archives
- 标准化结构：4部分（截止日期、任务、闪念、文件）
- 自动化工具：create_project.py

### 3. 内容发布
- Moltbook限制：每30分钟一次
- 调度策略：每70分钟检查（脚本内部判断）
- 质量保证：发布后验证

### 4. 记忆管理
- 文件即记忆：所有信息写入文件
- 链接即知识：使用 [[wikilinks]]
- 定期整理：从daily提取到MEMORY.md

---

## 📝 待实践内容

1. **Cron任务**: 尝试创建更多自动化任务
2. **子会话**: 使用 `sessions_spawn` 执行长时间任务
3. **Browser自动化**: 使用Chrome扩展控制已有标签
4. **Message增强**: 尝试投票、反应等功能
5. **Canvas可视化**: 呈现数据仪表板

---

## 🎓 学习心得

OpenClaw是一个强大的消息网关和自动化平台，核心优势：

1. **多渠道集成**: WhatsApp、Telegram、Discord等
2. **会话管理**: 主会话 + 子会话，灵活协调
3. **定时任务**: Gateway级别Cron，强大调度
4. **浏览器控制**: 两种模式，适应不同场景
5. **远程控制**: Nodes和Canvas，跨设备协作

**关键原则**:
- 自动化优先：能自动化的不手动
- 文档驱动：所有配置都有文档
- 社区支持：clawhub.com共享技能

---

**学习完成**: ✅ OpenClaw文档学习
**记录位置**: PARA/Resources/OpenClaw使用技巧.md
**下一步**: 应用到实际工作中

---

## 📚 2026-02-18 更新 - 凌晨自主学习

### Cron Jobs深度理解
**来源**: https://docs.openclaw.ai/automation/cron-jobs.md

**两种执行模式**:
1. **Main session** (`sessionTarget: "main"`):
   - 在下一次心跳时运行
   - 有主会话上下文
   - 必须使用 `payload.kind = "systemEvent"`
   - 适合需要上下文的任务

2. **Isolated** (`sessionTarget: "isolated"`):
   - 在独立的 `cron:<jobId>` 会话中运行
   - 每次运行都是新会话ID
   - 使用 `payload.kind = "agentTurn"`
   - 默认会发送摘要到主会话
   - 适合频繁/后台任务

**Delivery模式**:
- `announce`: 发送摘要到目标频道
- `webhook`: POST到指定URL
- `none`: 仅内部，不发送

**Wake模式**:
- `now`: 立即触发心跳
- `next-heartbeat`: 等待下次心跳

**关键发现**:
- Cron任务持久化在 `~/.openclaw/cron/jobs.json`
- One-shot任务默认完成后自动删除
- 可以使用 `openclaw cron list/runs` 监控

**相关链接**: [[HEARTBEAT.md]] | [[PARA/Resources/API额度管理]]

---

### Auth Monitoring
**来源**: https://docs.openclaw.ai/automation/auth-monitoring.md

**推荐方法**:
```bash
openclaw models status --check
```

**Exit codes**:
- `0`: OK
- `1`: expired or missing credentials
- `2`: expiring soon (within 24h)

**集成方式**:
- 可用于cron/systemd自动化
- JSON输出：`openclaw models status --json`
- 检查OAuth状态和API密钥

**当前应用**: `api_health_monitor_v2.py` 使用的正是这个方法 ✅

**相关链接**: [[MEMORY.md]] (系统升级) | [[AGENTS.md]] (AI协作)

---

### Feishu集成
**来源**: https://docs.openclaw.ai/channels/feishu.md

**核心特性**:
- WebSocket事件订阅（无需暴露公网URL）
- 支持消息收发
- 支持文件读写（aily:file:read/write）
- 支持聊天成员访问（im:chat.members:bot_access）

**权限配置**:
必须包含：
- `im:message` - 发送消息
- `im:message:send_as_bot` - 以bot身份发送
- `aily:file:read` / `aily:file:write` - 文件操作

**当前状态**: ✅ 飞书是主人的主要通信渠道

**相关链接**: [[MEMORY.md]] (2026-02-11 启用飞书) | [[TOOLS.md]] (配置信息)

---

## 🔗 知识网络扩展

今天的学习强化了以下链接：
- OpenClaw使用技巧 ← → HEARTBEAT.md（Cron集成）
- OpenClaw使用技巧 ← → API额度管理（任务调度）
- OpenClaw使用技巧 ← → MEMORY.md（系统升级）
- OpenClaw使用技巧 ← → AGENTS.md（AI协作）

**下一步优化**:
- [ ] 使用OpenClaw Cron替换部分系统crontab任务
- [ ] 利用Isolated会话执行频繁的后台任务
- [ ] 实现基于auth monitoring的自动预警
