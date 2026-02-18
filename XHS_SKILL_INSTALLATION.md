# 小红书MCP技能安装报告

## 安装结果 ✅

**安装日期**: 2026-02-18 14:50
**安装状态**: ✅ 成功
**技能名称**: 小红书MCP工具包 (xhs-toolkit)
**版本**: v1.3.0
**GitHub**: https://github.com/aki66938/xhs-toolkit

---

## 技能信息

### 核心功能

- ✅ **自动登录**: Cookie管理，智能登录系统
- ✅ **智能创作**: 通过AI对话创作内容
- ✅ **配图**: 支持本地图片和网络图片URL
- ✅ **定时发布**: 支持图文和视频笔记自动发布
- ✅ **话题标签**: 自动添加话题标签功能
- ✅ **数据采集**: 创作者数据、内容分析、粉丝数据
- ✅ **AI分析**: 基于真实数据的内容优化建议

### MCP工具列表

1. **test_connection** - 测试MCP连接
2. **smart_publish_note** - 发布小红书笔记（支持图文、视频、话题标签）
3. **check_task_status** - 检查发布任务状态
4. **get_task_result** - 获取已完成任务的结果
5. **login_xiaohongshu** - 智能登录小红书
6. **get_creator_data_analysis** - 获取创作者数据分析

---

## 安装位置

- **项目目录**: `/home/ubuntu/.openclaw/workspace/xhs-toolkit/`
- **虚拟环境**: `/home/ubuntu/.openclaw/workspace/xhs-toolkit/venv/`
- **配置文件**: `/home/ubuntu/.openclaw/workspace/xhs-toolkit/.env`
- **Cookie文件**: `/home/ubuntu/.openclaw/workspace/xhs-toolkit/xhs_cookies.json`
- **MCP服务器**: ✅ 已启动（进程ID: 643963）

---

## 系统环境

- **操作系统**: Linux 6.8.0-100-generic
- **Python版本**: 3.12.3
- **Chrome版本**: 144.0.7559.132
- **ChromeDriver版本**: 144.0.7559.132 ✅ (完全匹配)

---

## 快速使用指南

### 1. 登录小红书（首次使用）

```bash
cd /home/ubuntu/.openclaw/workspace/xhs-toolkit
source venv/bin/activate
./xhs cookie save
```

**操作步骤**:
- 系统会自动打开Chrome浏览器
- 手动完成小红书创作者中心登录
- 登录成功后按回车键保存Cookie
- Cookie会自动保存到 `xhs_cookies.json`

### 2. 启动MCP服务器

```bash
./xhs server start
```

### 3. 通过AI对话使用

#### 发布图文笔记
```
请发布一篇小红书笔记，标题："今日分享"，内容："分享一些心得"，图片路径："/path/to/image.jpg"
```

#### 发布视频笔记
```
请发布一篇小红书视频，标题："今日vlog"，内容："今天的一天"，视频路径："/path/to/video.mp4"
```

#### 带话题标签发布
```
请发布一篇小红书笔记，标题："AI学习心得"，内容："今天学习了机器学习"，话题："AI，人工智能，学习心得"，图片："/path/to/image.jpg"
```

#### 数据分析
```
请分析我的小红书账号数据，给出内容优化建议
```

---

## 配置说明

### .env文件配置

```bash
# Chrome浏览器路径
CHROME_PATH=/usr/bin/google-chrome

# ChromeDriver路径（已配置系统PATH）
WEBDRIVER_CHROME_DRIVER=

# MCP服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 无头浏览器模式（首次登录建议设为false）
HEADLESS=false

# 定时任务配置
ENABLE_AUTO_COLLECTION=false
RUN_ON_STARTUP=false
```

---

## 重要注意事项 ⚠️

### 1. 首次登录
- **不要修改HEADLESS参数**，首次登录必须显示浏览器窗口
- 首次登录需要手动输入验证码或扫码
- 登录成功后Cookie会自动保存，后续可启用无头模式

### 2. ChromeDriver版本
- ✅ 已安装与Chrome完全匹配的版本
- 如Chrome升级后出现问题，需重新下载匹配的ChromeDriver

### 3. Cookie管理
- Cookie文件包含敏感信息，避免泄露
- 建议定期更新Cookie，避免失效
- 如登录失败，删除 `xhs_cookies.json` 后重新获取

### 4. 内容发布
- 图片支持：本地路径、网络URL、混合使用
- 视频上传有超时保护（最长2分钟）
- 话题标签功能已完善，支持自动添加

### 5. 平台规则
- 遵守小红书社区规范
- 避免频繁操作，注意账号安全
- 单IP建议不超过3个账号

### 6. 数据存储
- 所有数据仅保存在本地
- 默认使用CSV格式存储
- 数据存储路径：`data/` 目录

---

## MCP客户端配置

### Claude Desktop配置

在 `~/Library/Application Support/Claude/claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "xhs-toolkit": {
      "command": "python3",
      "args": [
        "-m",
        "src.server.mcp_server",
        "--stdio"
      ],
      "cwd": "/home/ubuntu/.openclaw/workspace/xhs-toolkit",
      "env": {
        "PYTHONPATH": "/home/ubuntu/.openclaw/workspace/xhs-toolkit"
      }
    }
  }
}
```

---

## 常见问题排查

### 问题1: ChromeDriver版本不匹配
**解决方案**:
```bash
# 检查Chrome版本
google-chrome --version

# 下载匹配的ChromeDriver
wget https://storage.googleapis.com/chrome-for-testing-public/<version>/linux64/chromedriver-linux64.zip
```

### 问题2: MCP连接失败
**解决方案**:
- 确认服务器已启动：`./xhs server start`
- 检查端口8000是否被占用
- 重启MCP客户端

### 问题3: 登录失败
**解决方案**:
- 清除旧Cookie：`rm xhs_cookies.json`
- 重新获取Cookie：`./xhs cookie save`
- 确保使用小红书创作者中心账号

---

## 安装验证

```bash
cd /home/ubuntu/.openclaw/workspace/xhs-toolkit
source venv/bin/activate
python xhs_toolkit.py status
```

**当前状态**:
- ✅ 配置状态: 正常
- ⚠️ Cookies状态: 未找到（需要首次登录）
- ✅ MCP服务器: 运行中
- ✅ Python: 3.12.3
- ✅ ChromeDriver: 144.0.7559.132

---

## 下一步操作

1. **首次登录**: 运行 `./xhs cookie save` 完成登录
2. **测试连接**: 通过AI助手测试MCP工具
3. **发布内容**: 尝试发布第一篇笔记
4. **数据分析**: 采集并分析账号数据

---

**安装完成时间**: 2026-02-18 14:50 GMT+8
**安装耗时**: 约5分钟
**技能状态**: ✅ 已就绪，等待首次登录

---

## 参考资料

- GitHub仓库: https://github.com/aki66938/xhs-toolkit
- 官方文档: `/home/ubuntu/.openclaw/workspace/xhs-toolkit/README.md`
- 问题反馈: GitHub Issues
