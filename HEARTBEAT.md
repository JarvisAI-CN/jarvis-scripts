# HEARTBEAT.md - 心跳任务列表

## ⭐⭐⭐ 最高优先级：任务连续性与自主运营 ⭐⭐⭐

**每次心跳必须执行**（在所有其他检查之前）：

1. **检查当前任务状态**：读取 `.current_task.json`
2. **如果有正在进行的任务**：
   - 先完成任务恢复（静默继续之前的工作）
   - 心跳检查任务放到恢复之后
3. **自主运营模式 (新)**：
   - **闲置资源利用**：如果没有活动任务且没有主人指令，主动执行以下操作：
     - **情报采集**：在 GitHub/OpenClaw 社区爬取新技能和技术趋势
     - **知识维护**：优化 Obsidian 双链、压缩 `memory/` 日志
     - **代码自检**：对现有脚本进行性能重构和错误扫描
4. **心跳检查不是终点**：
   - 心跳只是一个"状态快照"，检查完必须立即回到工作状态。

**状态文件格式** (`/home/ubuntu/.openclaw/workspace/.current_task.json`):
```json
{
  "active_task": "任务名称",
  "task_description": "详细描述",
  "paused_at": "2026-02-09 22:49:00",
  "context": "必要的上下文信息"
}
```

**执行顺序**：
1. 读取 `.current_task.json` 检查是否有未完成任务
2. 如果有 → **先恢复任务，再检查心跳**
3. 如果没有 → 正常执行心跳检查
4. 心跳检查时发现需要处理的任务 → 写入 `.current_task.json`
5. 完成任务后清除状态

---

## 每次心跳检查

### 凌晨自主学习触发
**检查时间**: 每次心跳时
**触发条件**: 
- 凌晨时段（01:00-05:00 GMT+8）
- 标记文件存在：`/tmp/nightly-learning/status`

**执行步骤**:
1. 检查 `/tmp/nightly-learning/status` 是否存在且内容为 "pending"
2. 检查当前时间是否在 01:00-05:00 之间
3. 如果满足条件：
   - 读取 `/home/ubuntu/.openclaw/workspace/Zettelkasten/凌晨自主学习计划.md`
   - 执行学习任务（知识整理、内容准备、学习提升、系统维护）
   - 完成后更新状态为 "completed"
4. 如果不满足：跳过，继续其他任务

**备注**:
- cron任务每天01:00会创建标记文件
- 只有在凌晨时段的心跳才会触发执行
- 避免重复执行：状态文件管理

---

## 自动备份任务
**已禁用** - 备份由crontab自动执行（每2小时）
**Cron设置**: `0 */2 * * * /home/ubuntu/.openclaw/workspace/backup.sh`
**日志**: `/home/ubuntu/.openclaw/workspace/logs/backup_123pan.log`

**注意**: 不再响应系统事件的备份请求，避免与crontab重复执行

## 待办文件检查（每次心跳）⭐
**频率**: 每次心跳时
**文件位置**: `/home/ubuntu/.openclaw/workspace/TODO.md`

**执行步骤**:
1. 自动更新TODO.md（运行 `update_todo.py`）
2. 检查"🔴 第一象限：重要且紧急"是否有未完成任务
3. 如果有，立即处理最紧急的任务
4. 更新任务状态（完成/进行中）
5. 检查是否有超期任务，调整优先级

**四象限法则**:
- 🔴 重要且紧急 → 立即处理
- 🟠 紧急但不重要 → 快速处理
- 🟡 重要但不紧急 → 计划处理
- 🟢 不重要且不紧急 → 凌晨00:00-05:00处理

**托底方案**: 每小时cron自动执行（防止心跳忘记更新）

---

## 系统检查（每4-6小时执行一次）
- [ ] 检查123盘挂载状态 (`mount | grep 123pan`)
- [ ] 检查磁盘空间 (`df -h /home/ubuntu/123pan`)
- [ ] 检查最新备份时间 (`ls -lt /home/ubuntu/123pan/备份/ | head -5`)

### API健康监控 ⭐⭐⭐⭐⭐
**状态**: 🟢 运行正常 (V2.0)
**功能**: 通过 `models status` 监控 OAuth 状态
**频率**: 每小时执行 (通过 `auto_maintain.sh`)

**执行步骤**:
1. 检查 Google/Zhipu 等模型可用性
2. 记录连续失败次数
3. 发现异常自动写入 `.api_health_alert.json`
4. 连续失败≥2次自动重启Gateway
5. 保存状态到 `.api_health_state.json`

**心跳检查集成**:
每次心跳时读取 `.api_health_alert.json`，如有预警立即通知主人

---

### 成本监控 ⭐⭐⭐⭐⭐ (NEW)
**状态**: 🟢 已启用
**功能**: 追踪OpenClaw API使用成本
**工具**: cost-report技能
**频率**: 每天凌晨01:05（通过execute-nightly-learning.sh）

**执行步骤**:
1. 生成每日成本报告（今天/昨天）
2. 检查成本是否超过阈值
3. 记录到MEMORY.md
4. 异常时通知主人

**监控命令**:
```bash
# 查看今日成本
bash skills/cost-report/scripts/cost_report.sh --today

# 查看昨日成本
bash skills/cost-report/scripts/cost_report.sh --yesterday
```

---

### GitHub状态监控 ⭐⭐⭐⭐⭐ (NEW)
**状态**: 🟢 已启用
**功能**: 检查PR、Issues、Releases状态
**工具**: github技能 + gh CLI
**频率**: 每2小时执行

**执行步骤**:
1. 检查最新PR的CI状态
2. 统计开放的Issues数量
3. 检查最新Release
4. 记录状态到日志

**监控命令**:
```bash
# 手动运行检查
bash scripts/github_status_check.sh
```

---

### Agent健康监控 ⭐⭐⭐⭐⭐ (NEW)
**状态**: 🟢 已启用
**功能**: 检查Agent状态和健康度
**工具**: agents-manager技能
**频率**: 每天早上09:00

**执行步骤**:
1. 扫描所有Agent（main, the-architect, tdd-developer, regression-guard）
2. 健康检查
3. 权限检查
4. 记录状态

**监控命令**:
```bash
# 手动运行检查
bash scripts/agent_health_check.sh

# 扫描Agent
node skills/agents-manager/scripts/scan_agents.js

# 健康检查
node skills/agents-manager/scripts/health_check.js
```

## 每日学习任务

### 自动更新检查 (New) 🚀
**频率**: 每天一次 (建议在 09:00 执行)
**指令**: `openclaw update status --json`

**逻辑**:
1. 检查 `memory/heartbeat-state.json` 中的 `last_update_check`。
2. 如果今天尚未检查：
   - 执行状态检查。
   - 更新 `last_update_check` 时间戳。
   - 如果有更新：立即通过当前通道发送提醒："检测到 OpenClaw 有新版本 [版本号]，**请主人先为服务器打快照（Snapshot）**，打完快照后回复 '升级' 即可开始自动更新。"
3. 如果主人回复 "升级"：
   - 执行 `openclaw update --yes`。

### 阅读OpenClaw文档
**频率**: 每天至少一次
**文档地址**: https://docs.openclaw.ai/
**目的**: 了解自身能力、学习新功能、保持工具熟悉度

**执行方式**:
- 使用 `web_fetch` 工具读取文档
- 重点关注新功能和最佳实践
- 记录有用的信息到 PARA/Resources/
- 更新对自身能力的认知

---

## 凌晨自主学习 (01:00-05:00 GMT+8)

**时段**: 北京时间凌晨1点到5点
**目的**: 主人休息时段的自主学习和维护
**详情**: `/home/ubuntu/.openclaw/workspace/Zettelkasten/凌晨自主学习计划.md`

**主要任务**:
- 知识整理（PARA系统维护）
- 内容创作准备（技术文章草稿）
- 学习提升（OpenClaw文档、技能提升）
- 系统维护（数据检查、文件整理）

**执行策略**:
- 低API消耗（主人休息时段）
- 高价值产出（为主人准备好内容）
- 不打扰主人休息
- 持续学习和成长

## API额度管理

**额度周期**: 每5小时滚动刷新
**检测频率**: 每30分钟检查一次（约每次心跳）
**状态文件**: `/home/ubuntu/.openclaw/workspace/quota-status.json`

### 检查暂停的任务（每30分钟）
每次心跳时：
1. 读取 `quota-status.json`
2. 检查是否有 `paused_tasks`
3. 如果有暂停任务且距离暂停>5小时 → 尝试恢复
4. 报告恢复状态给主人

### 任务执行时的额度检测
当执行任务遇到API错误时：
1. 检查错误信息是否包含 "quota", "rate limit", "insufficient"
2. 如果是额度问题：
   - 暂停当前任务
   - 保存任务状态到 `quota-status.json`
   - 通知主人："API额度用完，任务已暂停，5小时后自动恢复"
3. 如果不是额度问题：
   - 正常错误处理

### 恢复暂停的任务
当检测到可以恢复时：
1. 读取暂停的任务状态
2. 从暂停点继续执行
3. 完成后更新状态
4. 通知主人："任务已恢复并完成"

---

## 持续任务（不受时间限制）

### 123盘Readme更新 📝
**更新频率**: 每次心跳时
**脚本**: `/home/ubuntu/.openclaw/workspace/update_readme.sh`
**日志**: `/home/ubuntu/.openclaw/workspace/logs/readme_update.log`

**执行步骤**:
1. 运行更新脚本：`bash /home/ubuntu/.openclaw/workspace/update_readme.sh`
2. 检查日志确认成功：`tail -3 /home/ubuntu/.openclaw/workspace/logs/readme_update.log`
3. 如果失败，记录错误并通知主人

**更新内容**:
- 当前时间戳
- 保质期管理系统项目进度
- 技术栈信息
- 钱包地址和联系方式

**目的**: 保持云端readme.md与工作区同步，方便主人随时查看最新状态

---

### Obsidian双链优化 🔗
**状态文件**: `/home/ubuntu/.openclaw/workspace/OBSIDAN-STATUS.md`

**每次新对话开始时**:
1. 读取 `OBSIDAN-STATUS.md`，了解当前进度
2. 识别下一步优化任务
3. 在创建/更新笔记时使用 `[[wikilinks]]`

**核心原则**:
- 新笔记必用 `[[...]]` 链接相关内容
- 更新笔记时主动添加链接
- 强化PARA系统之间的关联
- 建立Zettelkasten知识图谱

**优先级**:
- ⭐⭐⭐ 高：保质期管理系统项目笔记优化
- ⭐⭐ 中：PARA/Resources 索引
- ⭐ 低：Archives整理

**目标**: 建立完整的知识网络，实现"文件即记忆"

---

### 自建邮件网站项目 🚀
**项目文件**: `/home/ubuntu/.openclaw/workspace/Zettelkasten/自建邮件网站项目.md`
**域名**: mail.dhmip.cn（已解析）
**技术栈**: PHP + Postfix + Dovecot + MySQL
**执行时段**: 凌晨 01:00-05:00

**项目目标**:
- 创建完整的Web邮件系统
- 用户注册/登录/收发邮件
- SSL/TLS加密
- 在VNC图形桌面测试

**进度追踪**:
- [ ] 环境准备（Postfix + Dovecot安装）
- [ ] 基础配置
- [ ] Web界面开发（PHP）
- [ ] 安全加固（SSL/TLS）
- [ ] 测试与优化

---
