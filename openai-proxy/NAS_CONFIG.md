# NAS OpenClaw 配置指南

## 代理服务信息
- **服务地址**: http://150.109.204.23:9000
- **状态**: ✅ 已启动
- **客户端密钥**: jarvis-local-secret

## NAS 上的配置模板

```json
{
  "provider": "jarvis-local",
  "base_url": "http://150.109.204.23:9000",
  "api": "openai-completions",
  "api_key": "jarvis-local-secret",
  "model": {
    "id": "glm-4.7",
    "name": "Zhipu GLM-4.7"
  }
}
```

## 可用的模型

### 智谱 GLM 系列（推荐）
- `glm-4.7` - 智谱 GLM-4.7（默认）
- `glm-5` - 智谱 GLM-5

### Kimi 系列
- `kimi-k2.5` - Kimi K2.5（通过 NVIDIA API）

## 测试命令

在 NAS 上可以用 curl 测试：

```bash
curl -X POST http://150.109.204.23:9000/v1/chat/completions \
  -H "Authorization: Bearer jarvis-local-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.7",
    "messages": [
      {"role": "user", "content": "你好"}
    ]
  }'
```

## 说明

1. **默认模型**: glm-4.7（智谱）
2. **兼容性**: 完全兼容 OpenAI Chat Completions 协议
3. **鉴权**: 需要使用 Bearer token（jarvis-local-secret）
4. **路由**: 根据模型 ID 自动转发到对应的服务
5. **API类型**: openai-completions（OpenClaw 标准配置）

## 问题排查

1. 检查服务状态: curl http://150.109.204.23:9000/health
2. 查看日志: tail -f /home/ubuntu/.openclaw/workspace/openai-proxy/proxy.log
3. 测试模型: 使用上面的 curl 命令测试

