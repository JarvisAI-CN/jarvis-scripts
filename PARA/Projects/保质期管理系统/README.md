# 保质期管理系统（Expiry Management System）

## 概述
- **目标**：给门店/仓库做「入库→扫码→盘点→临期/过期管理」的一体化系统，降低损耗、提高盘点效率。
- **当前状态**：活跃维护中（作为当前重点项目）。
- **代码主目录（本机工作区）**：`/home/ubuntu/.openclaw/workspace/expiry-clean/`
- **发布包/历史文件（归档）**：`[[PARA/Archives/保质期管理系统]]`
- **线上测试环境**：`http://ceshi.dhmip.cn`（宝塔部署）

## 近期日志
- 2026-02-19：发布 v2.9.0（安装阶段 SQL 执行错误不再被忽略；修复 api_keys 表缺失问题）。
- 2026-02-20：将本项目提升为 PARA/Projects 重点跟踪。

## 归属领域（Areas）
- [[PARA/Areas/门店运营与库存管理]]

## 关键资源（Resources）
- `[[PARA/Resources/自动化测试最佳实践]]`
- `[[PARA/Resources/PARA系统-项目归档流程]]`
- `[[PARA/Resources/OpenClaw使用技巧]]`

## 当前关注点（下一步）
- [ ] 明确“当前线上运行版本号”和“当前仓库版本号”一致性校验流程
- [ ] 补一个最小化回归测试清单（安装/升级/管理员后台/盘点流程）
- [ ] 继续把发布包与 CHANGELOG / Release Notes 统一整理进归档

## 成果/交付物
- GitHub 干净仓库（代码仓库）：JarvisAI-CN/expiry-management-system-clean
- 已发布版本：v2.8.2 / v2.8.3 / v2.8.4 / v2.8.5 / v2.9.0
