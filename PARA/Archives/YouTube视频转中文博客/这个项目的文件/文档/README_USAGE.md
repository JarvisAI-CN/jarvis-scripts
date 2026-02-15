# YouTube视频转中文博客 - 使用说明

## 项目简介

自动化工具，将YouTube视频转录、翻译成中文博客，并自动上传到123盘云存储。

## 功能特性

✅ 自动下载YouTube音频
✅ 使用OpenAI Whisper API转录
✅ 使用GPT-4翻译成中文博客
✅ 自动上传到123盘
✅ 支持定时任务（凌晨自动执行）
✅ 详细日志记录

## 快速开始

### 1. 安装依赖

```bash
cd /home/ubuntu/.openclaw/workspace/PARA/Projects/YouTube视频转中文博客/这个项目的文件/脚本

# 安装Python依赖
pip3 install -r requirements.txt

# 或手动安装
pip3 install yt-dlp openai
```

### 2. 配置API密钥

在 `/home/ubuntu/.openclaw/workspace/PASSWORDS.md` 中添加OpenAI API密钥：

```markdown
## OpenAI
OpenAI API Key: sk-your-api-key-here
```

或设置环境变量：

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### 3. 测试运行

```bash
# 一键执行
./run_youtube_to_blog.sh "https://www.youtube.com/watch?v=xxx"

# 或使用Python
python3 main.py "https://www.youtube.com/watch?v=xxx"
```

### 4. 设置定时任务

```bash
# 设置每天凌晨00:30执行
./setup_crontab.sh

# 查看定时任务
crontab -l

# 删除定时任务
crontab -e
```

## 脚本说明

### 主要脚本

| 脚本 | 功能 |
|------|------|
| `main.py` | 主执行脚本（完整流程） |
| `run_youtube_to_blog.sh` | 一键执行Shell脚本 |
| `download_audio.py` | 下载YouTube音频 |
| `transcribe.py` | 音频转文字（Whisper API） |
| `translate_blog.py` | 翻译成中文博客 |
| `upload_123pan.py` | 上传到123盘 |
| `setup_crontab.sh` | 设置定时任务 |

### 输出目录

```
/tmp/youtube_blog/
├── 20260209_003000/           # 时间戳目录
│   ├── audio/                 # 音频文件
│   ├── transcript.txt         # 转录文本
│   └── blog.md               # 中文博客

/home/ubuntu/123pan/博客/
└── blog.md                   # 最终博客（123盘）
```

## 使用示例

### 处理单个视频

```bash
./run_youtube_to_blog.sh "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 修改执行时间

编辑 `setup_crontab.sh`，修改时间表达式：

```bash
# 每天01:00执行
0 1 * * * /path/to/run.sh "URL"

# 每周一凌晨02:00执行
0 2 * * 1 /path/to/run.sh "URL"

# 每6小时执行一次
0 */6 * * * /path/to/run.sh "URL"
```

## 故障排查

### 1. yt-dlp下载失败

```bash
# 更新yt-dlp
pip3 install --upgrade yt-dlp

# 或使用yt-dlp直接下载测试
yt-dlp -x --audio-format mp3 "视频URL"
```

### 2. OpenAI API错误

- 检查API密钥是否正确
- 检查API额度是否充足
- 检查网络连接

```bash
# 测试API密钥
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 3. 123盘上传失败

- 检查123盘是否挂载：`mount | grep 123pan`
- 检查挂载目录权限：`ls -la /home/ubuntu/123pan`

```bash
# 重新挂载123盘（根据你的挂载方式）
# 示例: mount -t davfs ...
```

### 4. Crontab任务未执行

```bash
# 查看cron日志
grep CRON /var/log/syslog

# 查看脚本日志
cat 这个项目的文件/日志/cron.log

# 手动测试
./run_youtube_to_blog.sh "视频URL"
```

## 日志位置

- **主日志**: `这个项目的文件/日志/youtube_to_blog.log`
- **错误日志**: `这个项目的文件/日志/error.log`
- **Cron日志**: `这个项目的文件/日志/cron.log`
- **运行日志**: `这个项目的文件/日志/run_*.log`

## 成本估算

### OpenAI API成本

| 服务 | 模型 | 价格 |
|------|------|------|
| Whisper | whisper-1 | $0.006/分钟 |
| GPT-4 | gpt-4-turbo | $0.01/1K tokens |

### 示例：30分钟视频

- Whisper转录: $0.006 × 30 = $0.18
- GPT-4翻译: ~$0.50
- **总计**: ~$0.68/视频

## 进阶使用

### 1. 批量处理

创建URL列表文件 `videos.txt`：

```
https://www.youtube.com/watch?v=xxx1
https://www.youtube.com/watch?v=xxx2
https://www.youtube.com/watch?v=xxx3
```

批量处理：

```bash
while read url; do
    ./run_youtube_to_blog.sh "$url"
    sleep 60  # 间隔1分钟
done < videos.txt
```

### 2. 自定义博客模板

编辑 `translate_blog.py` 中的 `format_blog_markdown()` 函数。

### 3. 添加摘要和关键词

在 `translate_blog.py` 的提示词中添加要求。

## 许可证

MIT License

## 联系方式

- 维护者: Jarvis (贾维斯) ⚡
- 项目位置: `/home/ubuntu/.openclaw/workspace/PARA/Projects/YouTube视频转中文博客`

---

**最后更新**: 2026-02-08
