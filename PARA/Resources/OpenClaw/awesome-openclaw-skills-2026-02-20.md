# Awesome OpenClaw Skills 速览（2026-02-20 手动学习）

来源：https://github.com/VoltAgent/awesome-openclaw-skills （README）

## 我们现在最相关的方向（按你当前系统）

1) **Moltbook (51)**
- 目标：恢复发帖/互动的质量与幂等性（避免重复内容灾难）。
- 选择标准：
  - 有去重/幂等/内容质量检查思路
  - 能做“先验证后发布”（post-verify）

2) **Self-Hosted & Automation (25) / DevOps & Cloud (212)**
- 目标：把 NAS/OpenClaw 的“连不上就卡死”变成“自动降级 + 明确告警 + 可恢复”。
- 关注点：健康检查、重试策略、报警、任务状态持久化。

3) **Notes & PKM (100)**
- 目标：Obsidian 双链维护、日志→洞察→长期记忆的流水线。

## 安装方式（备忘）
- ClawHub CLI：`npx clawhub@latest install <skill-slug>`
- 手动：复制到 `~/.openclaw/skills/` 或 workspace 的 `skills/`

## 风险提示（重要）
- 这个列表明确提醒：**收录不代表安全**。
- 安装前先去 ClawHub 看 VirusTotal 扫描 + 过一遍源码（尤其是会读写文件/发消息/跑 shell 的技能）。

## 下一步（建议你确认后我再动手）
- 你说一个优先方向：
  1) Moltbook 质量与幂等
  2) NAS / OpenClaw 远程自愈
  3) Obsidian / PKM 流水线
- 我就从对应分类里挑 3 个最可能有用的技能，逐个做“源码审计 + 适配你环境”的安装方案。
