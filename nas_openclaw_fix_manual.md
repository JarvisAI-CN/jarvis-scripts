# NAS OpenClaw 配置修复说明

## 问题分析
NAS上的OpenClaw正在尝试使用 SiliconFlow 模型，但 `auth-profiles.json` 文件中缺少对应的API密钥。需要将默认模型改为已配置的智谱4.7。

## 修复步骤（在NAS上操作）

### 1. 登录NAS
- 地址：https://fsnas.top
- 用户名：admin
- 密码：fs159753

### 2. 打开DSM系统
登录后，进入 DSM 桌面。

### 3. 打开终端
1. 进入 "控制面板" → "终端机和SNMP"
2. 确保 "启动SSH功能" 已启用
3. 打开 DSM 的 "Web Station" 或 "终端" 应用

### 4. 切换到 shuaishuai 用户
```bash
su - shuaishuai
密码：fs159753
```

### 5. 检查当前配置
```bash
# 检查 OpenClaw 主目录
ls -la /var/services/homes/shuaishuai/.openclaw/

# 检查当前配置文件
cat /var/services/homes/shuaishuai/.openclaw/config.json
cat /var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json
```

### 6. 修改默认模型为智谱4.7
#### 方法1：使用命令行修改 config.json
```bash
cat > /var/services/homes/shuaishuai/.openclaw/config.json << 'EOF'
{
  "model": {
    "default": "zhipu/glm-4.7"
  }
}
EOF
```

#### 方法2：使用编辑器修改（如果有vi/vim）
```bash
vi /var/services/homes/shuaishuai/.openclaw/config.json
```

修改内容为：
```json
{
  "model": {
    "default": "zhipu/glm-4.7"
  }
}
```

### 7. 检查并更新认证配置
确保 `auth-profiles.json` 包含智谱API密钥：
```bash
cat /var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json
```

如果没有，创建或更新：
```bash
cat > /var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json << 'EOF'
{
  "providers": {
    "zhipu": {
      "apiKey": "你的智谱API密钥"
    }
  }
}
EOF
```

### 8. 重启 OpenClaw 服务
```bash
# 停止当前进程
pkill -f "openclaw gateway" 2>/dev/null
pkill -f "node.*openclaw" 2>/dev/null

# 等待进程结束
sleep 2

# 启动 OpenClaw Gateway
npm exec openclaw gateway -- --daemon > /dev/null 2>&1 &

# 等待启动
sleep 5
```

### 9. 验证服务状态
```bash
# 检查进程是否在运行
pgrep -f "openclaw gateway"
ss -tuln | grep 18789
```

### 10. 测试 OpenClaw 功能
在 DSM 终端中，尝试发送测试消息：
```bash
curl -X POST http://127.0.0.1:18789/api/message -d '{"text":"hello"}'
```

## 替代方案：使用 OpenClaw 管理界面
如果有 Web 管理界面：
1. 访问：http://localhost:18789
2. 登录（如果需要）
3. 进入 "设置" → "模型"
4. 将默认模型改为 "zhipu/glm-4.7"
5. 保存设置

## 常见问题排查

### 1. OpenClaw 无法启动
```bash
# 检查 Node.js 版本
node -v

# 检查 npm 版本
npm -v

# 检查 OpenClaw 版本
npm exec openclaw -- --version
```

### 2. 权限问题
```bash
# 检查文件权限
ls -laR /var/services/homes/shuaishuai/.openclaw/

# 确保 shuaishuai 用户有读写权限
chown -R shuaishuai:users /var/services/homes/shuaishuai/.openclaw/
```

### 3. 智谱API密钥无效
```bash
# 检查 API 密钥是否正确
curl -X POST "https://open.bigmodel.cn/api/paas/v4/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的智谱API密钥" \
  -d '{
    "model": "glm-4",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

## 成功标准
- OpenClaw Gateway 进程正常运行
- 端口 18789 正常监听
- 发送测试消息能正常回复
- 不再出现 "No API key found for provider \"siliconflow\"" 错误

---
**最后修改时间**: 2026年2月23日
**修改原因**: 修正NAS地址和密码
