# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your infrastructure, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 🔐 密码管理
**所有密码和凭据**已集中存储于: `PASSWORDS.md`
- 文件权限: 600 (仅root可读写)
- 包含: WebDAV、VNC、API密钥、系统账户等
- ⚠️ 谨慎处理，避免泄露

## 快速参考
### 网络服务
- 123盘WebDAV: /home/ubuntu/123pan
- VNC服务器: localhost:5901 (密码见PASSWORDS.md)
- 内网IP: 10.7.0.5
- 公网IP: 150.109.204.23 (用于外部访问)
- GitHub: https://github.com/JarvisAI-CN (账号凭证见PASSWORDS.md)

### 系统路径
- 工作区: /home/ubuntu/.openclaw/workspace
- 备份脚本: /home/ubuntu/.openclaw/workspace/backup.sh
- 备份日志: /home/ubuntu/.openclaw/workspace/logs/backup_123pan.log
- 123盘备份: /home/ubuntu/123pan/备份/

### 知识管理工具
- **Obsidian**: 我的整个工作区是一个Obsidian vault
- **obsidian-cli** (v0.5.1): 命令行工具
  - 安装路径: `/home/ubuntu/.nvm/versions/node/v24.13.0/bin/obsidian`
  - 全局链接: `/usr/local/bin/obsidian`
  - 功能: 搜索、创建、移动笔记，自动更新双链
  - 使用文档: `[[Zettelkasten/Obsidian使用实践]]`
- **OBSIDAN-STATUS.md**: 双链优化进度追踪
- **实践原则**:
  - 新笔记必用 `[[...]]` 链接相关内容
  - 更新笔记时主动添加新发现的关联
  - 回顾时跟随链接探索，补充缺失链接

## 🔧 宝塔面板
**地址**: http://82.157.20.7:8888/fs123456
**测试域名**: ceshi.dhmip.cn (已解析至面板IP，用于临时绑定测试)
**用途**: 服务器管理面板

**主要功能**:
- LNMP环境一键安装
- 网站创建和管理
- MySQL数据库管理
- PHP版本切换（多版本共存）
- SSL证书一键部署
- 文件管理器（在线编辑）
- 计划任务管理

**部署流程**:
1. 登录宝塔面板
2. 软件商店 → 安装Nginx/PHP/MySQL
3. 网站创建 → 添加站点
4. 上传代码到/www/wwwroot/域名/
5. 配置伪静态和SSL
6. 测试访问

**使用建议**:
- PHP项目优先用宝塔快速测试
- 生产环境记得配置SSL
- 定期备份数据库
- 监控服务器资源

## 🛠️ 开发工具集（升级后 - 2026-02-17）

### Python开发工具 ⭐⭐⭐⭐⭐
- **black 26.1.0** - 专业代码格式化
  - 用途: 自动格式化Python代码，统一风格
  - 命令: `black script.py`
  - 配置: 遵循PEP 8规范
  
- **ruff 0.15.1** - 超快Python linter
  - 用途: 代码检查、发现潜在问题
  - 命令: `ruff check script.py`
  - 优势: 比pylint快10-100倍
  
- **mypy** - 静态类型检查
  - 用途: 类型检查，防止类型错误
  - 命令: `mypy script.py`
  
- **pytest** - 测试框架
  - 用途: 编写和运行测试
  - 命令: `pytest test_script.py`
  
- **pylint** - 代码质量分析
  - 用途: 深度代码审查
  - 命令: `pylint script.py`

### Git增强工具 ⭐⭐⭐⭐⭐
- **gh 2.45.0** - GitHub官方CLI
  - 用途: 仓库管理、PR、Issue、Release
  - 命令: `gh repo create`, `gh pr create`
  - 认证: 见PASSWORDS.md
  
- **jq 1.7** - JSON处理神器
  - 用途: 解析、查询、转换JSON
  - 命令: `cat file.json | jq '.key'`
  
- **git-lfs** - 大文件支持
  - 用途: Git管理大文件（二进制、媒体）
  - 命令: `git lfs track "*.psd"`

### Node.js环境 ⭐⭐⭐⭐⭐
- **Node.js v24.13.0** - LTS长期支持版
  - 用途: 运行JavaScript/TypeScript服务端
  - 包管理: npm 11.10.0
  
- **npm** - Node包管理器
  - 命令: `npm install`, `npm run build`
  - 全局包位置: `/usr/local/bin/`

### 命令行工具 ⭐⭐⭐⭐⭐
- **htop** - 交互式进程监控
  - 用途: 实时查看CPU、内存、进程
  - 命令: `htop`
  
- **ncdu** - 磁盘使用分析
  - 用途: 快速找到占用空间的目录
  - 命令: `ncdu /home/ubuntu`
  
- **ripgrep (rg)** - 超快文本搜索
  - 用途: 代码搜索，比grep快很多
  - 命令: `rg "pattern" /path`
  
- **bat** - 高亮cat
  - 用途: 带语法高亮的文件查看
  - 命令: `bat script.py`
  
- **exa** - 彩色ls
  - 用途: 更好的文件列表
  - 命令: `exa -la`
  
- **fzf** - 模糊查找器
  - 用途: 快速查找文件
  - 命令: `fzf`

### AI SDK ⭐⭐⭐⭐⭐
- **anthropic 0.79.0** - Claude API
  - 用途: 调用Claude模型辅助编程
  - 认证: 见PASSWORDS.md
  
- **openai 2.17.0** - GPT API
  - 用途: 调用GPT-4辅助开发
  - 认证: 见PASSWORDS.md
  
- **google-generativeai** - Gemini API
  - 用途: 调用Gemini模型
  - 认证: 见PASSWORDS.md

### Docker容器化 ⭐⭐⭐⭐⭐
- **Docker 29.2.1** - 容器平台
  - 用途: 应用容器化、部署
  - 命令: `docker build`, `docker run`
  - 用户: ubuntu已加入docker组

### 构建工具
- **build-essential** - 编译工具链
- **cmake** - 跨平台构建系统
- **git-lfs** - Git大文件支持

## 📊 工具使用示例

### 代码质量保证流程
```bash
# 1. 格式化代码
black script.py

# 2. 检查代码
ruff check script.py

# 3. 类型检查
mypy script.py

# 4. 运行测试
pytest test_script.py
```

### 快速搜索代码
```bash
# 搜索函数定义
rg "def my_function" /path/to/code

# 搜索TODO注释
rg "TODO" /home/ubuntu/.openclaw/workspace

# 搜索并高亮显示
rg "pattern" --context 3
```

### GitHub自动化
```bash
# 创建新仓库
gh repo create my-project --public

# 创建PR
gh pr create --title "Fix bug" --body "Description"

# 查看Issues
gh issue list
```

### Docker部署
```bash
# 构建镜像
docker build -t myapp:v1.0 .

# 运行容器
docker run -d -p 8080:80 myapp:v1.0

# 查看日志
docker logs -f container_id
```

### JSON处理
```bash
# 提取字段
cat file.json | jq '.key'

# 格式化输出
cat file.json | jq '.'

# 数组操作
cat file.json | jq '.items[] | .name'
```

## 🎯 升级收益

### 代码质量
- 格式化: 手动 → 自动（black）
- 检查: 无 → 超快（ruff）
- 类型: 无 → 静态检查（mypy）
- 测试: 手动 → 框架化（pytest）

### 开发效率
- 搜索: grep → ripgrep（10-100倍快）
- JSON: 手动解析 → jq（自动化）
- Git: 基础命令 → GitHub CLI（全功能）

### 语言支持
- 升级前: Python为主
- 升级后: Python + Node.js + 更多语言

### 部署能力
- 升级前: 直接部署
- 升级后: Docker容器化

### AI协作
- 升级前: 单模型（OpenClaw主模型）
- 升级后: 多模型协作（Claude + GPT + Gemini）

---

**升级时间**: 2026-02-17 22:43
**新增工具**: 15+
**能力提升**: ⭐⭐⭐ → ⭐⭐⭐⭐⭐

## 📊 PPTX技能 (2026-02-18安装)

**技能来源**: https://skills.sh/anthropics/skills/pptx
**状态**: ✅ 已安装并验证

### 功能概览
- **读取/分析**: 提取PPTX文本内容，生成缩略图预览
- **编辑**: 修改现有演示文稿，添加/删除幻灯片
- **创建**: 从零生成PPTX演示文稿
- **转换**: PPTX ↔ PDF，格式转换

### 依赖组件
- **Python**: markitdown[pptx], Pillow (虚拟环境: ~/.venv/pptx-skill/)
- **Node.js**: pptxgenjs@4.0.1
- **系统**: LibreOffice 24.2.7.2, Poppler 24.02.0

### 技能位置
- 技能目录: `/home/ubuntu/.openclaw/workspace/skills/pptx/`
- 文档: SKILL.md, editing.md, pptxgenjs.md
- 脚本: scripts/thumbnail.py, add_slide.py, clean.py

### 快速使用
```bash
# 激活环境
source ~/.venv/pptx-skill/bin/activate

# 提取PPTX文本
python -m markitdown presentation.pptx

# 生成缩略图
python /home/ubuntu/.openclaw/workspace/skills/pptx/scripts/thumbnail.py presentation.pptx

# 验证安装
python /home/ubuntu/.openclaw/workspace/skills/pptx/verify_installation.py
```

### 应用场景
- 自动化生成报告演示文稿
- 批量处理PPTX文件
- 提取演示文稿内容用于总结
- 基于模板创建标准化演示
