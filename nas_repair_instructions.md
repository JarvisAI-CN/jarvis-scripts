# NAS OpenClaw 配置修复说明 (shuaishuai 用户)

## 问题分析
OpenClaw 在尝试使用 SiliconFlow 模型时失败，因为在 `/var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json` 文件中找不到该提供商的API密钥配置。

## 修复方案

### 方法1：通过DSM Web界面操作（推荐）

#### 1. 登录DSM管理界面
- 访问：https://fsnas.top
- 登录用户：admin
- 密码：fs159753

#### 2. 打开终端
1. 进入 "控制面板" → "终端机和SNMP"
2. 确保 "启动SSH功能" 已启用
3. 打开 DSM 的 "终端" 应用

#### 3. 切换用户并执行修复
```bash
# 切换到 shuaishuai 用户
su - shuaishuai
# 密码：fs159753

# 创建修复脚本
cat > ~/fix_openclaw.sh << 'EOF'
#!/bin/bash

# OpenClaw 配置修复脚本
# 修复 SiliconFlow API key 未找到的问题

echo "=== 修复OpenClaw配置问题 ==="
echo "目标：将默认模型从 SiliconFlow 改为智谱4.7"

# 检查当前配置
CONFIG_PATH="/var/services/homes/shuaishuai/.openclaw/config.json"
AUTH_PATH="/var/services/homes/shuaishuai/.openclaw/agents/main/agent/auth-profiles.json"

echo ""
echo "1. 检查配置文件..."
if [ -f "$CONFIG_PATH" ]; then
    echo "  找到 config.json"
    echo "  内容："
    cat "$CONFIG_PATH"
else
    echo "  未找到 config.json，将创建新的"
fi

if [ -f "$AUTH_PATH" ]; then
    echo ""
    echo "  找到 auth-profiles.json"
    echo "  内容："
    cat "$AUTH_PATH"
else
    echo ""
    echo "  未找到 auth-profiles.json，将创建新的"
fi

echo ""
echo "2. 修改 config.json"
cat > "$CONFIG_PATH" << 'INNER_EOF'
{
  "model": {
    "default": "zhipu/glm-4.7"
  }
}
INNER_EOF

if [ $? -eq 0 ]; then
    echo "  ✅ 成功更新 config.json"
else
    echo "  ❌ 无法写入 config.json"
    exit 1
fi

echo ""
echo "3. 检查并创建认证配置"
if [ ! -f "$AUTH_PATH" ]; then
    cat > "$AUTH_PATH" << 'INNER_EOF'
{
  "providers": {
    "zhipu": {
      "apiKey": "你的智谱API密钥"
    }
  }
}
INNER_EOF
    echo "  ✅ 创建了新的 auth-profiles.json"
else
    echo "  ✅ auth-profiles.json 已存在"
fi

echo ""
echo "4. 重启 OpenClaw 服务"
pkill -f "openclaw gateway" 2>/dev/null
pkill -f "node.*openclaw" 2>/dev/null
sleep 2

npm exec openclaw gateway -- --daemon > /dev/null 2>&1 &
sleep 5

echo ""
echo "5. 验证服务状态"
if pgrep -f "openclaw gateway" > /dev/null; then
    PID=$(pgrep -f "openclaw gateway")
    echo "  ✅ OpenClaw Gateway 运行正常 (PID: $PID)"
else
    echo "  ❌ OpenClaw Gateway 未运行"
    exit 1
fi

if ss -tuln | grep -q 18789; then
    echo "  ✅ 端口 18789 正常监听"
else
    echo "  ❌ 端口 18789 未监听"
    exit 1
fi

echo ""
echo "=== 修复完成 ==="
echo "现在 OpenClaw 应该使用智谱4.7模型回复消息了"
EOF

# 赋予执行权限
chmod +x ~/fix_openclaw.sh
echo "修复脚本已创建"

# 执行修复
~/fix_openclaw.sh
```

### 方法2：通过SSH直接连接（如果密码正确）

```bash
# 连接到NAS（需要正确的密码）
ssh shuaishuai@fsnas.top
# 密码：fs159753

# 执行修复
cat > ~/fix_openclaw.sh << 'EOF'
[上述脚本内容]
EOF

chmod +x ~/fix_openclaw.sh
~/fix_openclaw.sh
```

### 方法3：检查系统状态

如果OpenClaw无法启动，可以检查系统状态：

```bash
# 检查 Node.js 版本
node -v

# 检查 npm 版本
npm -v

# 检查 OpenClaw 安装
npm list -g openclaw

# 检查进程
ps aux | grep openclaw

# 检查日志
openclaw logs --follow
```

### 常见问题排查

#### 1. 权限问题
```bash
# 确保 shuaishuai 用户对配置文件有读写权限
chown -R shuaishuai:users /var/services/homes/shuaishuai/.openclaw/
ls -laR /var/services/homes/shuaishuai/.openclaw/
```

#### 2. Node.js 版本问题
```bash
# 检查 Node.js 版本是否兼容
node -v
which node

# 如果需要重新安装
# curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
# apt-get install -y nodejs
```

#### 3. OpenClaw 安装问题
```bash
# 重新安装 OpenClaw
npm uninstall -g openclaw
npm install -g openclaw

# 验证安装
openclaw --version
```

## 验证修复

修复完成后，测试 OpenClaw 是否正常工作：

```bash
# 发送测试消息
curl -X POST http://127.0.0.1:18789/api/message -d '{"text":"hello"}'
```

## 成功标准

1. OpenClaw Gateway 进程正常运行
2. 端口 18789 正常监听
3. 发送消息能正常回复
4. 不再出现 "No API key found for provider "siliconflow"" 错误

---
**修复脚本已保存到**: `/home/ubuntu/.openclaw/workspace/nas_repair_instructions.md`
**创建时间**: 2026年2月23日
**目标用户**: shuaishuai
