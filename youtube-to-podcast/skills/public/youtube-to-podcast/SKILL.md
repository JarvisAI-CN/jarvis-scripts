---
name: youtube-to-podcast
description: Convert YouTube videos to Chinese podcast transcripts using Whisper API and GPT-4. Automatically downloads audio, transcribes to English, translates to natural spoken Chinese with podcast-style formatting, and uploads to cloud storage. Use when user asks to: (1) Convert YouTube video to Chinese podcast, (2) Transcribe and translate YouTube content, (3) Create podcast scripts from videos, (4) Download and process YouTube audio for translation.
---

# YouTube to Chinese Podcast

Automatically convert YouTube videos into natural, conversational Chinese podcast transcripts.

## Quick Start

Convert a YouTube video to podcast:

```bash
cd skills/public/youtube-to-podcast
./scripts/run_youtube_to_podcast.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Workflow

The complete pipeline:

1. **Download audio** from YouTube (using yt-dlp)
2. **Transcribe** to English text (using Whisper API)
3. **Translate** to Chinese podcast script (using GPT-4)
4. **Upload** to cloud storage (WebDAV/123 Pan)

All steps are automated in the main script.

## Scripts

### `main.py`
Main execution script that orchestrates the entire pipeline.

**Usage:**
```bash
python3 main.py "<YouTube_URL>"
```

### `run_youtube_to_podcast.sh`
One-click shell script with dependency checking and logging.

**Usage:**
```bash
./run_youtube_to_podcast.sh "<YouTube_URL>"
```

### `download_audio.py`
Download YouTube audio only (best quality, MP3 format).

**Usage:**
```bash
python3 download_audio.py "<YouTube_URL>" [output_dir]
```

### `transcribe.py`
Transcribe audio to English text using OpenAI Whisper API.

**Usage:**
```bash
python3 transcribe.py <audio_file> [output_transcript_file]
```

Requires `OPENAI_API_KEY` in PASSWORDS.md or environment variable.

### `translate_podcast.py`
Translate English transcript to natural spoken Chinese podcast script.

**Usage:**
```bash
python3 translate_podcast.py <transcript_file> <YouTube_URL> [output_podcast_file]
```

**Podcast Style Features:**
- Conversational, natural spoken Chinese
- Preserves speaker's tone and personality
- Adds voice cues: [pause], [laughter], [emphasis]
- Includes intro/outro in podcast style
- Natural transitions between topics

### `upload_123pan.py`
Upload generated podcast to cloud storage (WebDAV).

**Usage:**
```bash
python3 upload_123pan.py <podcast_file> [target_directory]
```

Default target: `/home/ubuntu/123pan/播客/`

## Configuration

### API Keys

Add OpenAI API key to `/home/ubuntu/.openclaw/workspace/PASSWORDS.md`:

```markdown
## OpenAI
OpenAI API Key: sk-your-api-key-here
```

Or set environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Cloud Storage

Edit `upload_123pan.py` to configure WebDAV mount point:

```python
WEBDAV_MOUNT = "/home/ubuntu/123pan"
PODCAST_DIR = os.path.join(WEBDAV_MOUNT, "播客")
```

## Output Format

Generated podcast scripts include:

- **YAML frontmatter** with metadata (title, date, source, duration)
- **Intro** in conversational podcast style
- **Body** with natural spoken Chinese and voice cues
- **Outro** with summary
- **Metadata** about translation tools and credits

Example structure:

```markdown
---
title: Video Title
type: podcast
date: 2026-02-09
source: https://youtube.com/watch?v=xxx
---

# Video Title

> 本播客文稿由AI自动翻译自YouTube视频

大家好，今天我们来聊聊一个有趣的话题...

[停顿]

说到这个，我想起了一个重要的观点...

---

**关于本播客**
- 翻译工具: OpenAI Whisper + GPT-4
- 翻译风格: 口语化、自然流畅
```

## Automation

Set up automated processing with crontab:

```bash
./scripts/setup_crontab.sh
```

This schedules daily execution at 00:30 (configurable).

## Cost Estimation

For a 30-minute video:
- Whisper transcription: ~$0.18
- GPT-4 translation: ~$0.50
- **Total**: ~$0.68 per video

## Troubleshooting

See `references/TROUBLESHOOTING.md` for common issues and solutions.

## Advanced Usage

### Batch Processing

Process multiple videos from a list:

```bash
while read url; do
    ./scripts/run_youtube_to_podcast.sh "$url"
    sleep 60
done < videos.txt
```

### Custom Prompt Templates

Edit `translate_podcast.py` to customize translation style:

```python
prompt = f"""
将以下英文演讲翻译成中文播客文稿...
[Your custom instructions]
"""
```

## File Organization

```
youtube-to-podcast/
├── SKILL.md                          # This file
├── scripts/
│   ├── main.py                       # Main pipeline
│   ├── run_youtube_to_podcast.sh     # One-click runner
│   ├── download_audio.py             # Download YouTube audio
│   ├── transcribe.py                 # Whisper transcription
│   ├── translate_podcast.py          # GPT-4 translation
│   ├── upload_123pan.py              # Upload to cloud
│   ├── setup_crontab.sh              # Automation setup
│   └── requirements.txt              # Python dependencies
├── references/
│   ├── TROUBLESHOOTING.md            # Issue diagnosis
│   └── API_DOCS.md                   # API documentation
└── assets/
    └── templates/
        └── podcast_template.md       # Output template
```

## Best Practices

1. **Test with short videos first** (5-10 minutes) to verify setup
2. **Check API quotas** before processing long videos
3. **Review output quality** and adjust prompts as needed
4. **Monitor cloud storage** space for large batches
5. **Keep transcripts** for reference and quality control

## Credits

Created by Jarvis (贾维斯) ⚡
Open source on GitHub: [repository URL]
