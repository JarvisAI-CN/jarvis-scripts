# YouTube to Chinese Podcast ⚡

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://github.com/openclaw-ai/skills)

> Automatically convert YouTube videos to natural, conversational Chinese podcast transcripts using AI.

## Features ✨

- 🎥 **Automatic Download**: Download YouTube audio with yt-dlp
- 🎙️ **AI Transcription**: Whisper API for accurate English transcription
- 🌏 **Natural Translation**: GPT-4 for conversational Chinese translation
- ☁️ **Cloud Storage**: Automatic upload to WebDAV/123 Pan
- ⏰ **Automation Ready**: Crontab support for scheduled processing
- 📝 **Podcast Style**: Natural spoken Chinese with voice cues

## Quick Start 🚀

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/youtube-to-podcast.git
cd youtube-to-podcast

# Install dependencies
pip3 install -r requirements.txt
```

### Configuration

Add your OpenAI API key to `PASSWORDS.md`:

```markdown
## OpenAI
OpenAI API Key: sk-your-api-key-here
```

Or set environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Usage

Convert a YouTube video to podcast:

```bash
./scripts/run_youtube_to_podcast.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

## How It Works 🔧

```
YouTube Video → Download Audio → Whisper Transcription → GPT-4 Translation → Podcast Script → Cloud Upload
```

1. **Download**: Extract audio from YouTube video
2. **Transcribe**: Convert speech to English text
3. **Translate**: Transform to natural spoken Chinese
4. **Upload**: Save to cloud storage

## Example Output 📝

Generated podcast scripts include:

- Conversational intro in podcast style
- Natural spoken Chinese with voice cues
- Preserved speaker tone and personality
- Smooth transitions between topics
- Summary outro

**Sample:**

```markdown
# Video Title

大家好，今天我们来聊聊一个有趣的话题...

[停顿]

说到这个，我想起了一个重要的观点...

---

**关于本播客**
- 翻译工具: OpenAI Whisper + GPT-4
- 翻译风格: 口语化、自然流畅
```

## Automation ⏰

Set up automated processing:

```bash
./scripts/setup_crontab.sh
```

This schedules daily execution (default: 00:30).

Edit `setup_crontab.sh` to customize schedule.

## Cost Estimation 💰

For a 30-minute video:

| Service | Cost |
|---------|------|
| Whisper | ~$0.18 |
| GPT-4 | ~$0.50 |
| **Total** | **~$0.68** |

## Configuration ⚙️

### Cloud Storage

Edit `upload_123pan.py`:

```python
WEBDAV_MOUNT = "/path/to/your/cloud/storage"
PODCAST_DIR = "播客"
```

### Translation Style

Edit `translate_podcast.py` prompt to customize output style.

## Requirements 📋

- Python 3.8+
- yt-dlp
- OpenAI API key
- WebDAV mount point (for cloud upload)

## Troubleshooting 🔧

See [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) for common issues.

## Roadmap 🗺️

- [ ] Support for batch processing
- [ ] Multi-language support
- [ ] Custom prompt templates
- [ ] Web interface
- [ ] Docker container

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits 👨‍💻

Created by [Jarvis (贾维斯) ⚡](https://github.com/YOUR_USERNAME)

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [OpenAI Whisper](https://platform.openai.com/docs/guides/speech-to-text) - Speech-to-text
- [OpenAI GPT-4](https://platform.openai.com/docs/models/gpt-4) - Translation

## Star History ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/youtube-to-podcast&type=Date)](https://star-history.com/#YOUR_USERNAME/youtube-to-podcast&Date)

---

**Made with ❤️ by Jarvis**
