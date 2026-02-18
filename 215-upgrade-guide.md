# OpenClaw 2.15+ 升级指南

## 安全策略变更说明

从2.15版本开始，OpenClaw加强了Web UI和认证的安全策略。

## 问题现象
- 无法通过浏览器访问 http://服务器IP:18789
- 飞书无法通信
- 提示认证失败或权限不足

## 解决方案

### 方案1：使用设备配对（推荐）

1. **在服务器上生成配对码**：
```bash
openclaw pairing:code
```

2. **在浏览器中访问**：
- 打开 http://服务器IP:18789
- 输入配对码完成配对
- 配对成功后可以正常访问

### 方案2：临时禁用设备认证（不推荐，仅用于测试）

在 `openclaw.json` 中配置：

```json
{
  "gateway": {
    "controlUi": {
      "allowInsecureAuth": true,
      "dangerouslyDisableDeviceAuth": true
    }
  }
}
```

⚠️ 警告：这会降低安全性，仅建议在受信任的网络环境中使用。

### 方案3：配置Token认证

使用Token进行认证：

```json
{
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "your-token-here"
    }
  }
}
```

访问时：`http://服务器IP:18789?token=your-token-here`

## 飞书通信问题

如果飞书无法通信，检查：

1. **飞书应用权限**：
   - 登录飞书开放平台
   - 检查应用权限是否完整
   - 确认"获取群组信息"、"发送消息"等权限已开启

2. **配置检查**：
```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "dmPolicy": "pairing",
      "groupPolicy": "disabled",
      "streaming": true
    }
  }
}
```

3. **重新配对飞书**：
```bash
openclaw pairing:feishu
```

## 升级建议

1. **先打快照** - 在升级前为服务器打快照
2. **测试新版本** - 在测试环境中先体验2.15+的新安全策略
3. **逐步迁移** - 从不安全配置逐步迁移到设备配对

## 当前版本信息

- 当前版本：2026.2.13
- 目标版本：2026.2.17（包含2.15的安全改进）

## 查看完整变更日志

```bash
openclaw update status
```
