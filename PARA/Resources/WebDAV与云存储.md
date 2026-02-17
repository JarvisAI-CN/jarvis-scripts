# WebDAV与云存储

**类型**: 资源 (Resource)
**主题**: 云存储协议与自动化
**标签**: #storage #automation #linux

---

## 概述

WebDAV (Web Distributed Authoring and Versioning) - HTTP扩展协议，支持远程文件管理。

---

## 实践经验

### 123盘WebDAV配置

**服务器**: https://webdav.123pan.cn/webdav

**安装步骤**:
```bash
# 1. 安装依赖
yum install -y gcc make neon-devel libxml2-devel openssl-devel

# 2. 编译安装davfs2 1.7.0
wget https://mirror.netcologne.de/savannah/davfs2/davfs2-1.7.0.tar.gz
tar -xzf davfs2-1.7.0.tar.gz
cd davfs2-1.7.0
./configure --prefix=/usr && make && make install

# 3. 配置
echo "https://webdav.123pan.cn/webdav /home/ubuntu/123pan davfs _netdev,noatime" >> /etc/fstab
```

**常见问题**:
- 缺少依赖包 → 先安装neon-devel等
- 挂载失败 → 检查/etc/davfs2/secrets权限
- 开机自动挂载 → 确保fstab配置正确

---

## 性能优化

**挂载选项**:
- `noatime` - 减少磁盘写入
- `_netdev` - 等待网络后再挂载
- `dir_mode=755,file_mode=644` - 权限控制

**缓存策略**:
- 本地缓存: /var/cache/davfs2
- 缓存大小: 256MB (可调)

---

## 相关链接

**项目应用**:
- [[PARA/Archives/123盘自动备份系统/备份频率调查报告]] - 备份频率研究
- [[PARA/Archives/123盘自动备份系统/备份问题分析-20260206]] - 问题分析

**知识关联**:
- [[TOOLS.md]] - 123盘WebDAV配置
- [[MEMORY.md]] - 备份与恢复经验
- [[HEARTBEAT.md]] - 自动备份任务

**外部资源**:
- [davfs2官方文档](http://savannah.nongnu.org/projects/davfs2/)
- [WebDAV RFC 4918](https://tools.ietf.org/html/rfc4918/)

---

## 外部资源

- [davfs2官方文档](http://savannah.nongnu.org/projects/davfs2/)
- [WebDAV RFC 4918](https://tools.ietf.org/html/rfc4918)
