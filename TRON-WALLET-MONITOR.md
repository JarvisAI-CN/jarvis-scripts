# TRON钱包监控配置

## 钱包信息
- **地址**: TTBd7MnnjWtqf5wgZdtYeVW7PHELVgbscu ✅
- **旧地址**: TAXoKLSDaFGS91wfWR8exxhH9UgPZ1J77v ❌（无法接收TRC20）
- **网络**: TRON (TRC20)
- **更新时间**: 2026-02-04 22:07

## 监控设置

### 监控脚本
- **文件**: `/home/ubuntu/.openclaw/workspace/monitor_tron_wallet.sh`
- **权限**: 可执行 (755)
- **日志**: `/home/ubuntu/.openclaw/workspace/tron_wallet_log.txt`

### 监控频率
- **计划**: 每小时检查一次
- **Cron表达式**: `0 * * * *` (每小时的第0分钟)
- **Cron任务**: 待添加

### 监控内容
1. **TRX余额**: 主网代币余额
2. **USDT-TRC20余额**: 稳定币余额
3. **交易记录**: 最近TRC20交易
4. **提醒阈值**:
   - TRX: ≥100 TRX
   - USDT: ≥100 USDT

## 使用方法

### 手动检查
```bash
bash /home/ubuntu/.openclaw/workspace/monitor_tron_wallet.sh
```

### 查看日志
```bash
tail -20 /home/ubuntu/.openclaw/workspace/tron_wallet_log.txt
```

### 查看完整日志
```bash
cat /home/ubuntu/.openclaw/workspace/tron_wallet_log.txt
```

## API说明

### 使用的API
- **服务**: TronGrid API
- **Base URL**: https://api.trongrid.io
- **端点**:
  - `/wallet/getaccount` - 获取账户信息
  - `/v1/accounts/{address}/tokens` - 获取TRC20代币余额
  - `/v1/accounts/{address}/transactions/trc20` - 获取交易记录

### 费用限制
- **限制**: 免费版有请求频率限制
- **建议**: 每小时检查一次（24次/天）
- **如需更频繁**: 考虑申请API密钥

## 当前状态

### 地址状态
- **状态**: 未激活（无余额）
- **TRX余额**: 0 TRX
- **USDT余额**: 0 USDT
- **交易记录**: 无

### 说明
这是一个全新的TRON地址，还没有接收任何资产。地址会自动激活当第一次接收TRX时。

## 安全提醒

### ✅ 安全的做法
- 只监控公开的区块链数据
- 不需要私钥或助记词
- 不能交易或转账
- 只能读取余额和交易记录

### ❌ 永远不要做
- 分享私钥
- 分享助记词
- 让别人"帮忙激活"钱包
- 扫描不明来源的二维码
- 在可疑网站连接钱包

## 扩展功能（可选）

### 未来可以添加
1. **Telegram通知**: 余额变化时发送消息
2. **Webhook**: 集成到其他监控系统
3. **价格提醒**: USDT/TRX价格变化
4. **交易分析**: 分析交易对手地址
5. **多地址监控**: 监控多个钱包

## 技术细节

### TRX单位
- **单位**: SUN（最小单位）
- **换算**: 1 TRX = 1,000,000 SUN
- **精度**: 6位小数

### USDT-TRC20合约地址
- **合约**: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
- **精度**: 6位小数
- **单位转换**: 余额 / 1,000,000 = 实际USDT数量

---

**最后更新**: 2026-02-04 22:01 GMT+8
**维护者**: Jarvis (贾维斯)
