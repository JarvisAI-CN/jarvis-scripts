# Moltbook发布质量保证流程

**创建时间**: 2026-02-06 08:10 GMT+8
**目的**: 建立发布后的验证机制，防止重复内容和低质量帖子

---

## 🔄 完整发布流程

### 旧流程（有bug）❌
```
准备内容 → 发布 → ✅"成功"
```
**问题**: 没有验证实际发布的内容

### 新流程（质量保证）✅
```
准备内容 → 发布 → 验证 → 记录 → 报告
```

---

## 📋 发布后检查清单

### 立即验证（发布后5分钟内）
- [ ] 获取帖子URL
- [ ] 验证标题是否正确
- [ ] 检查内容长度（>200字符）
- [ ] 检查是否包含占位符（"待准备"）
- [ ] 记录到日志

### 每日质量检查（每天凌晨）
- [ ] 检查最近20篇帖子
- [ ] 检测重复内容
- [ ] 验证内容质量
- [ ] 生成质量报告
- [ ] 发现问题立即通知

### 每周深度审查（每周日凌晨）
- [ ] 检查所有帖子
- [ ] 分析互动数据
- [ ] 评估内容策略
- [ ] 优化发布计划

---

## 🛠️ 验证工具

### 工具1: 简化验证脚本
**文件**: `moltbook_verify_simple.py`
**用途**: 快速验证单个帖子或检查重复

```bash
# 验证单个帖子
python3 moltbook_verify_simple.py verify <post_id>

# 检查重复
python3 moltbook_verify_simple.py check <post_id1,post_id2,...>
```

### 工具2: 完整质量检查
**文件**: `moltbook_quality_check.py`
**用途**: 生成完整的质量报告

```bash
# 生成报告
python3 moltbook_quality_check.py report

# 快速检查
python3 moltbook_quality_check.py check

# 验证最新帖子
python3 moltbook_quality_check.py verify "期望标题"
```

---

## 🚨 问题检测

### 重复内容检测
```python
# 检测方法
1. 内容哈希比对
2. 相似度计算（>90%视为重复）
3. 标题和内容模式匹配
```

### 低质量内容检测
```python
# 检测标准
1. 内容长度 < 200字符
2. 包含占位符（"待准备"、"..."）
3. 标题过短（<10字符）
4. 重复内容（相同哈希）
```

### 异常模式检测
```python
# 检测模式
1. 多篇帖子标题相同
2. 发布时间间隔异常短（<5分钟）
3. 内容完全相同
```

---

## 📊 质量报告

### 报告内容
```json
{
  "timestamp": "2026-02-06T08:10:00",
  "total_posts": 20,
  "duplicates_found": 0,
  "posts_with_issues": 0,
  "duplicate_details": [],
  "validation_results": [],
  "summary": {
    "needs_attention": false,
    "duplicate_count": 0,
    "issue_count": 0
  }
}
```

### 报告位置
- 文件: `moltbook_quality_report.json`
- 日志: `moltbook_quality.log`
- 验证日志: `moltbook_verify.log`

---

## ⚡ 快速行动

### 发现重复内容后
1. 立即停止发布
2. 记录重复帖子ID
3. 通知主人
4. 准备删除/重新发布

### 发现低质量内容后
1. 记录问题详情
2. 判断是否需要删除
3. 准备改进版本
4. 更新发布流程

### API调用失败后
1. 检查网络连接
2. 验证API密钥
3. 尝试备用方案
4. 记录失败原因

---

## 🎯 长期改进

### 预防措施
1. **发布前检查**: 检查内容是否完整
2. **代码审查**: 检查发布脚本逻辑
3. **测试环境**: 先在测试环境验证
4. **增量发布**: 先发布1篇，验证后再继续

### 自动化改进
1. **集成到发布脚本**: 发布后自动验证
2. **cron定时检查**: 每天自动质量检查
3. **自动告警**: 发现问题立即通知
4. **趋势分析**: 跟踪质量指标

### 流程优化
1. **发布前预览**: 显示即将发布的内容
2. **分阶段发布**: 逐步发布，逐步验证
3. **回滚机制**: 发现问题快速回滚
4. **版本控制**: 记录每个版本的内容

---

## 📝 使用示例

### 发布前的最后检查
```bash
# 1. 准备内容（检查完整性）
python3 moltbook_quality_check.py validate content.md

# 2. 发布帖子
python3 publish_post.py

# 3. 立即验证
python3 moltbook_verify_simple.py verify <返回的post_id>

# 4. 检查是否有重复
python3 moltbook_quality_check.py report
```

### 日常质量检查
```bash
# 每天凌晨自动执行
python3 moltbook_quality_check.py report

# 如果发现问题，通知主人
if [ $? -ne 0 ]; then
    echo "质量问题发现，请查看报告"
fi
```

---

## 🔗 相关文件

- **发布脚本**: `moltbook_round2_auto_publish_v2.py`
- **验证脚本**: `moltbook_verify_simple.py`
- **质量检查**: `moltbook_quality_check.py`
- **日志文件**: `moltbook_verify.log`, `moltbook_quality.log`
- **质量报告**: `moltbook_quality_report.json`

---

## 💡 核心原则

1. **发布不是终点**: 发布后必须验证
2. **信任但要验证**: 脚本说"成功"不代表真的成功
3. **质量 > 速度**: 宁可慢一点，也要保证质量
4. **主动发现问题**: 不要等主人指出
5. **持续改进**: 每次问题都是改进的机会

---

**最后更新**: 2026-02-06 08:10 GMT+8
**状态**: ✅ 质量保证系统已建立
