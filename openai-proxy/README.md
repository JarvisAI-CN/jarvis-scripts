# Jarvis OpenAI 兼容代理服务

## 用途
为 NAS（或其他无法访问外网 OpenAI/Gemini 的设备）提供 OpenAI 兼容的 API 代理。

## 工作原理
1. NAS 发送 OpenAI 格式的请求到这台服务器
2. 代理服务验证 API key
3. 根据 `model` 参数转发到对应的上游服务
4. 返回 OpenAI 格式的响应

## 配置

### 1. 创建 .env 文件
```bash
cp .env.example .env
```

### 2. 编辑 .env 填写上游 API 密钥
```bash
OPENAI_API_KEY=sk-xxx          # OpenAI API 密钥
GEMINI_API_KEY=AIzaSyxxx       # Google Gemini API 密钥
PROXY_API_KEYS=jarvis-local-secret  # 客户端使用的密钥（多个用逗号分隔）
PORT=9000                       # 监听端口
```

### 3. 启动服务
```bash
./start.sh
```

或者手动启动：
```bash
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 9000
```

## 客户端配置示例

NAS 上的 OpenClaw 或其他工具配置：

```json
{
  "provider": "jarvis-local",
  "base_url": "http://150.109.204.23:9000",
  "api": "openai-chat",
  "api_key": "jarvis-local-secret",
  "model": {
    "id": "gpt-4.1-mini",
    "name": "Jarvis ChatGPT Proxy"
  }
}
```

## 支持的模型

### OpenAI 系列
- `gpt-4.1-mini` → OpenAI
- `gpt-4.1` → OpenAI
- `gpt-4o` → OpenAI
- `gpt-4o-mini` → OpenAI
- `gpt-3.5-turbo` → OpenAI

### Gemini 系列
- `gemini-3-flash` → Gemini
- `gemini-3-pro` → Gemini
- `gemini-2-flash` → Gemini

### 默认
- `jarvis-default` → OpenAI

## API 端点

### POST /v1/chat/completions
标准的 OpenAI Chat Completions 接口。

请求示例：
```json
{
  "model": "gpt-4.1-mini",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7
}
```

响应示例：
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4.1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！有什么可以帮助你的吗？"
      },
      "finish_reason": "stop"
    }
  ]
}
```

### GET /health
健康检查端点。

响应：
```json
{
  "status": "ok",
  "service": "jarvis-openai-proxy"
}
```

## 安全说明
- 所有请求需要 Bearer token 认证
- 仅在配置文件中的 API key 才能通过验证
- 代理服务不存储任何请求内容，纯透传

## 端口放行
确保服务器防火墙允许 9000 端口：
```bash
sudo ufw allow 9000
```

## 问题排查
1. 检查服务是否启动：`curl http://localhost:9000/health`
2. 检查日志：查看终端输出
3. 检查防火墙：确保 9000 端口可从外网访问

## 作者
贾维斯 (JarvisAI-CN)
