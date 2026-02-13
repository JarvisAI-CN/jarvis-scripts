# 贾维斯的Skills清单

**更新时间**: 2026-02-06 11:36 GMT+8

---

## 🔧 当前可用的Skills

### 1. bluebubbles
**功能**: 构建或更新BlueBubbles外部通道插件
- 描述: 扩展包，REST发送/探测，webhook入站
- 位置: `/home/ubuntu/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/bluebubbles/SKILL.md`

### 2. healthcheck
**功能**: 主机安全加固和风险配置
- 描述: 安全审计、防火墙/SSH/更新、风险暴露审查
- 用途: 安全加固、漏洞检查、版本状态
- 位置: `/home/ubuntu/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/healthcheck/SKILL.md`

### 3. skill-creator
**功能**: 创建或更新AgentSkills
- 描述: 设计、结构化、打包skills（脚本、引用、资源）
- 用途: 创建新技能、组织技能包
- 位置: `/home/ubuntu/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/skill-creator/SKILL.md`

### 4. weather
**功能**: 获取天气和预报（无需API密钥）
- 描述: 当前天气、天气预报
- 用途: 天气查询
- 位置: `/home/ubuntu/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/weather/SKILL.md`

---

## 📚 Skills说明

这些Skills是我能力扩展的"插件"。

**使用方式**:
- 你说"做XX"，我会检查是否有相关Skill
- 如果有，我会读取SKILL.md并按指导执行
- 每个Skill都是专门领域的专家知识

---

## 💡 可以做什么

基于当前skills，我可以：

1. **BlueBubbles集成** - 构建消息通道插件
2. **安全审计** - 检查服务器安全、加固配置
3. **创建技能** - 开发新的Skills或优化现有技能
4. **天气查询** - 获取天气信息

---

## 🎯 推荐使用

### 安全检查
**命令**: "帮我做安全审计" 或 "检查服务器安全"
**Skill**: healthcheck

### 创建新Skill
**命令**: "创建一个XX技能"
**Skill**: skill-creator

---

**主人**，想要我使用哪个Skill？或者需要我学习新的Skills吗？
