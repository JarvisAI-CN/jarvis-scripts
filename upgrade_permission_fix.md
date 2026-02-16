# 升级后权限问题诊断报告

## 问题总结

升级 OpenClaw 后出现两个权限问题：

1. **WebChat 错误**: "Error: missing scope: operator.read"
2. **Feishu 错误**: "OpenClaw: access not configured."

## 问题分析

### 1. WebChat - operator.read 缺失

**根本原因**：
升级后，OpenClaw 引入了新的权限系统。当前已配对的设备只有以下 scopes：
- `operator.admin`
- `operator.approvals`
- `operator.pairing`

但是缺少 `operator.read` scope，这导致某些操作（如读取配置、查看状态）失败。

**当前设备状态**：
```
Paired (2)
Device ID: 9c3a5730a2e0ce4d7114d74908c19ae42fd9067ffa
Roles: operator
Scopes: operator.admin, operator.approvals, operator.pairing
```

### 2. Feishu - 配对过期

**根本原因**：
- Feishu 配置为 `dmPolicy: "pairing"` 模式
- 配对代码有效期只有 1 小时
- 用户提供的配对代码 `3YNLQFDF` 已过期
- 运行 `openclaw pairing list feishu` 显示没有待处理的配对请求

**解决方案**：用户需要在飞书中重新发送消息，获取新的配对代码。

## 解决方案

### 修复 WebChat operator.read 缺失

**方案 1：通过 Control UI 修复（推荐）**

1. 打开 Control UI: http://10.7.0.5:18789/
2. 进入 **Devices** 面板
3. 找到对应的设备，编辑其 scopes
4. 添加 `operator.read` 到 scopes 列表

**方案 2：通过 CLI 修复**

删除旧设备并重新配对：

```bash
# 1. 删除现有设备配对
openclaw devices revoke --device <device-id> --role operator

# 2. 从 WebChat 重新连接（会触发新的配对请求）

# 3. 批准新配对请求
openclaw devices list
openclaw devices approve <request-id>
```

**方案 3：直接修改配置文件（临时方案）**

编辑 `~/.openclaw/devices/paired.json`，在设备的 scopes 中添加 `operator.read`：

```json
{
  "9c3a5730a2e0ce4d7114d74908c19ae42fd9067ffa": {
    "roles": ["operator"],
    "scopes": ["operator.admin", "operator.approvals", "operator.pairing", "operator.read"]
  }
}
```

然后重启 Gateway：
```bash
openclaw gateway restart
```

### 修复 Feishu 配对

**步骤**：

1. 在飞书中找到你的机器人
2. 发送任意消息（例如："hello"）
3. 机器人会返回新的配对代码
4. 在终端运行批准命令：

```bash
# 查看待处理的配对请求
openclaw pairing list feishu

# 批准配对（使用新的配对代码）
openclaw pairing approve feishu <NEW_CODE>
```

## 安全建议

根据 `openclaw status` 的安全审计报告，建议修复以下问题：

### 1. 禁用不安全的 HTTP 认证

当前配置：
```json5
{
  gateway: {
    controlUi: {
      allowInsecureAuth: true,
      dangerouslyDisableDeviceAuth: true
    }
  }
}
```

建议修复：
```bash
# 通过 Control UI 或直接编辑配置
openclaw config set gateway.controlUi.allowInsecureAuth false
openclaw config set gateway.controlUi.dangerouslyDisableDeviceAuth false
```

### 2. 修复 Feishu groupPolicy

当前配置：
```json5
{
  channels: {
    feishu: {
      groupPolicy: "open"  // 危险！允许任何群组成员触发
    }
  }
}
```

建议修复：
```bash
openclaw config set channels.feishu.groupPolicy "allowlist"
```

### 3. 增强网关令牌

当前令牌：`claw-123456`（太短）

建议修复：
```bash
# 生成新的随机令牌
openclaw config set gateway.auth.token "$(openssl rand -hex 16)"
```

### 4. 添加认证速率限制

```bash
openclaw config set gateway.auth.rateLimit.maxAttempts 10
openclaw config set gateway.auth.rateLimit.windowMs 60000
openclaw config set gateway.auth.rateLimit.lockoutMs 300000
```

## 快速修复命令

```bash
# 1. 修复 operator.read（方案 3 - 最快）
cat ~/.openclaw/devices/paired.json | \
  jq 'to_entries | .[].value.scopes += ["operator.read"] | from_entries' > /tmp/paired-new.json
mv /tmp/paired-new.json ~/.openclaw/devices/paired.json
openclaw gateway restart

# 2. 修复安全配置
openclaw config set gateway.controlUi.allowInsecureAuth false
openclaw config set gateway.controlUi.dangerouslyDisableDeviceAuth false
openclaw config set channels.feishu.groupPolicy "allowlist"
openclaw config set gateway.auth.token "$(openssl rand -hex 16)"
openclaw gateway restart
```

## 验证修复

修复后，运行以下命令验证：

```bash
# 检查设备状态
openclaw devices list

# 检查安全状态
openclaw security audit

# 测试 WebChat 连接
# 在浏览器中打开: http://10.7.0.5:18789/

# 测试 Feishu 连接
# 在飞书中发送消息，应该正常回复
```

## 总结

- **WebChat 问题**: 缺少 `operator.read` scope，需要添加到设备配对中
- **Feishu 问题**: 配对代码已过期，需要重新配对
- **安全问题**: 多个严重的安全配置问题，建议修复

---

**生成时间**: 2026-02-16 16:37 GMT+8
**OpenClaw 版本**: 2026.2.13
