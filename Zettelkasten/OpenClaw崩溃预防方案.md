# OpenClaw多模型崩溃预防方案

**日期**: 2026-02-12
**目标**: 避免所有模型同时不可用导致系统崩溃

---

## 🎯 问题分析

### 根本原因
从2026-02-12崩溃日志分析：
1. **gemini-3-flash** 额度用完（429错误）
2. **其他模型**也返回403或超时
3. **所有模型**同时不可用，导致系统"凉了"

### 为什么智谱只用了2%还超时？
- 可能不是额度问题
- 而是**认证系统**或**网络波动**导致请求失败
- OpenClaw的fallback机制在所有模型失败时无法自动恢复

---

## 🛡️ 预防措施

### 1. **API健康监控** ⭐⭐⭐⭐⭐

**脚本**: `scripts/api_health_monitor.py`

**功能**:
- ✅ 定期测试所有模型可用性
- ✅ 记录连续失败次数
- ✅ 检测最后可用时间
- ✅ 自动预警机制
- ✅ 自动重启Gateway

**使用方法**:
```bash
# 手动运行
python3 /home/ubuntu/.openclaw/workspace/scripts/api_health_monitor.py

# 添加到cron（每30分钟）
*/30 * * * * python3 /home/ubuntu/.openclaw/workspace/scripts/api_health_monitor.py
```

**状态文件**:
- 运行状态: `.api_health_state.json`
- 预警信息: `.api_health_alert.json`
- 日志: `logs/api_health.log`

---

### 2. **智能降级策略**

当主模型失败时，不是立即尝试所有模型（可能导致连锁失败），而是：

1. **等待短暂时间**（5-10秒）
2. **再尝试备用模型**
3. **记录失败原因**
4. **触发预警**

---

### 3. **额度监控与预警**

**目标**: 提前知道额度快用完

**实现**:
```python
# 在HEARTBEAT中添加
if token_usage > 80%:
    alert("⚠️ gemini-3-flash 额度使用超过80%")
if token_usage > 95%:
    alert("🚨 gemini-3-flash 额度即将用完，停止非紧急任务")
```

---

### 4. **自动恢复机制**

当检测到**所有模型连续失败3次**时：
1. 自动重启Gateway服务（刷新认证）
2. 记录到日志
3. 通知主人

---

### 5. **日志分析改进**

**问题**: 当前日志只有错误，缺少详细原因

**改进**:
- 记录每个API调用的详细信息
- 区分不同类型的错误：
  - 额度用完（429）
  - 认证失败（401/403）
  - 网络超时
  - 服务器错误（5xx）

---

## 📋 实施计划

### 第一阶段（今天）✅
- [x] 创建API健康监控脚本
- [x] 测试基本功能
- [ ] 添加到cron定时任务

### 第二阶段（本周）
- [ ] 在HEARTBEAT中集成监控结果
- [ ] 创建预警通知机制（飞书消息）
- [ ] 添加额度使用统计

### 第三阶段（本月）
- [ ] 优化fallback策略
- [ ] 添加详细的错误分类
- [ ] 创建自动恢复测试

---

## 🔧 配置建议

### 修改模型优先级

**当前**: gemini-3-flash → claude-opus-4-5-thinking → kimi-k2.5 → glm-4.7

**建议**: 考虑将智谱(glm-4.7)提前，因为：
- 你确认智谱额度充足
- 稳定性可能更好

**修改方式**: 在OpenClaw配置中调整模型顺序

---

## 📊 预期效果

### 预防前
- ❌ 所有模型同时失败
- ❌ 系统完全瘫痪
- ❌ 需要手动重启
- ❌ downtime ~36分钟

### 预防后
- ✅ 提前30分钟预警
- ✅ 自动恢复机制
- ✅ downtime <5分钟
- ✅ 详细的问题日志

---

## 🧪 测试验证

### 手动测试
```bash
# 1. 测试API健康监控
python3 /home/ubuntu/.openclaw/workspace/scripts/api_health_monitor.py

# 2. 检查状态文件
cat /home/ubuntu/.openclaw/workspace/.api_health_state.json

# 3. 检查日志
tail -20 /home/ubuntu/.openclaw/workspace/logs/api_health.log
```

### 模拟测试
1. 临时禁用一个模型的API密钥
2. 运行监控脚本
3. 观察是否正确检测并记录

---

## 📝 相关文档

- 崩溃分析: `memory/2026-02-12-crash-analysis.md`
- 监控脚本: `scripts/api_health_monitor.py`
- 系统日志: `journalctl --user -u openclaw-gateway`

---

**创建时间**: 2026-02-12 21:45 GMT+8
**创建者**: 贾维斯
**状态**: 🚧 实施中
