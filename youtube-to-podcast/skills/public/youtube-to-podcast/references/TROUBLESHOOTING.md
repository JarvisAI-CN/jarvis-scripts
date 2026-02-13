# Troubleshooting Guide

## Common Issues and Solutions

### 1. yt-dlp Download Fails

**Symptom:**
```
ERROR: Unable to extract video data
```

**Solutions:**

```bash
# Update yt-dlp to latest version
pip3 install --upgrade yt-dlp

# Try with direct URL format
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Check if video is region-restricted or private
```

**If still fails:**
- Video may be age-restricted (requires login)
- Video may be private
- Video may be geo-blocked

---

### 2. OpenAI API Errors

**Symptom:**
```
Error: Incorrect API key provided
Error: Insufficient quota
Error: Rate limit exceeded
```

**Solutions:**

```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API connectivity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check usage
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Check PASSWORDS.md:**
```bash
cat /home/ubuntu/.openclaw/workspace/PASSWORDS.md | grep -i openai
```

---

### 3. Transcription Incomplete

**Symptom:**
Transcript is cut off or missing sections

**Possible Causes:**
- Audio file too large (>25MB for Whisper API)
- Network interruption during upload
- API timeout

**Solutions:**

```python
# Split audio into chunks (edit transcribe.py)
# Use pydub to split audio
from pydub import AudioSegment

audio = AudioSegment.from_mp3("audio.mp3")
# Split into 10-minute chunks
for i, chunk in enumerate(audio[::600000]):
    chunk.export(f"chunk_{i}.mp3", format="mp3")
```

---

### 4. Translation Quality Issues

**Symptom:**
- Translation too formal
- Missing conversational tone
- Not podcast-style

**Solution:**

Edit `translate_podcast.py` prompt:

```python
prompt = f"""
请将以下英文演讲翻译成中文播客文稿。

**强调口语化**：
- 使用"咱们"、"这个"、"那个"等口语词
- 添加反问句："对吧？"、"是不是？"
- 自然地使用停顿和过渡语

**保持演讲者个性**：
- 如果演讲者幽默，保留幽默感
- 如果演讲者严肃，保持专业感

[Rest of prompt]
"""
```

---

### 5. Cloud Storage Upload Fails

**Symptom:**
```
❌ 123盘未挂载: /home/ubuntu/123pan
```

**Solutions:**

```bash
# Check if mounted
mount | grep 123pan

# Check mount directory
ls -la /home/ubuntu/123pan

# Remount if needed (adjust for your setup)
sudo mount -t davfs https://webdav.123pan.com /home/ubuntu/123pan
```

---

### 6. Crontab Task Not Running

**Symptom:**
Scheduled task doesn't execute at expected time

**Diagnosis:**

```bash
# Check crontab
crontab -l

# Check cron logs
sudo grep CRON /var/log/syslog | tail -20

# Check script permissions
ls -la scripts/run_youtube_to_podcast.sh

# Manual test
./scripts/run_youtube_to_podcast.sh "TEST_URL"
```

**Common Issues:**

1. **Relative paths in crontab**
   ```bash
   # Wrong
   30 0 * * * ./scripts/run.sh "URL"
   
   # Correct
   30 0 * * * /full/path/to/scripts/run.sh "URL"
   ```

2. **Missing environment variables**
   ```bash
   # Add to crontab
   OPENAI_API_KEY=sk-xxx
   30 0 * * * /path/to/run.sh "URL"
   ```

3. **Permission denied**
   ```bash
   chmod +x scripts/run_youtube_to_podcast.sh
   ```

---

### 7. Memory/Context Issues

**Symptom:**
```
Context overflow: prompt too large
```

**Cause:**
Transcript too long for single API call

**Solution:**

Split transcript into chunks:

```python
def split_transcript(transcript, max_chars=3000):
    """Split transcript into manageable chunks"""
    chunks = []
    current_chunk = ""
    
    for sentence in transcript.split('. '):
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Translate each chunk, then merge
chunks = split_transcript(transcript)
translated_chunks = [translate_chunk(chunk) for chunk in chunks]
final_podcast = merge_chunks(translated_chunks)
```

---

## Debug Mode

Enable verbose logging:

```bash
# In shell script
#!/bin/bash
set -x  # Enable debug mode
set -v  # Verbose mode

# In Python script
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Log Locations

- Main log: `这个项目的文件/日志/youtube_to_podcast.log`
- Error log: `这个项目的文件/日志/error.log`
- Cron log: `这个项目的文件/日志/cron.log`
- Run log: `这个项目的文件/日志/run_*.log`

## Getting Help

1. Check logs for error messages
2. Test each step individually
3. Verify API keys and quotas
4. Check network connectivity
5. Review this troubleshooting guide

## Recovery

If something goes wrong:

1. **Work directory preserved**: `/tmp/youtube_podcast/TIMESTAMP/`
2. **Partial results**: Check for `transcript.txt` or `podcast.md`
3. **Resume from failed step**: Edit `main.py` to skip completed steps

---

**Last updated**: 2026-02-08
