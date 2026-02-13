# Quick Start Guide

Get up and running with YouTube to Chinese Podcast in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- (Optional) WebDAV mount point for cloud upload

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/youtube-to-podcast.git
cd youtube-to-podcast
```

### 2. Install Dependencies

```bash
pip3 install -r skills/public/youtube-to-podcast/scripts/requirements.txt
```

Or manually:

```bash
pip3 install yt-dlp openai
```

### 3. Configure API Key

Create or edit `PASSWORDS.md`:

```markdown
## OpenAI
OpenAI API Key: sk-your-api-key-here
```

Or set environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

## Usage

### Basic Usage

Convert a YouTube video to podcast:

```bash
cd skills/public/youtube-to-podcast
./scripts/run_youtube_to_podcast.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Advanced Usage

#### Process specific video

```bash
python3 scripts/main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Only download audio

```bash
python3 scripts/download_audio.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Only transcribe

```bash
python3 scripts/transcribe.py audio.mp3 transcript.txt
```

#### Only translate

```bash
python3 scripts/translate_podcast.py transcript.txt "https://youtube.com/watch?v=VIDEO_ID" podcast.md
```

## Automation

### Set up Daily Processing

```bash
./scripts/setup_crontab.sh
```

This schedules execution at 00:30 daily.

### Custom Schedule

Edit `setup_crontab.sh`:

```bash
# Every 6 hours
0 */6 * * * /path/to/run.sh "URL"

# Weekly on Sunday at 2AM
0 2 * * 0 /path/to/run.sh "URL"
```

## Output

Generated files:

```
/tmp/youtube_podcast/TIMESTAMP/
├── audio/
│   └── video_title.mp3          # Downloaded audio
├── transcript.txt               # English transcript
└── podcast.md                   # Chinese podcast script
```

Cloud upload location (if configured):

```
/home/ubuntu/123pan/播客/
└── video_title.md               # Final podcast
```

## Troubleshooting

### Issue: "API key not found"

**Solution:** Check PASSWORDS.md or set OPENAI_API_KEY environment variable.

### Issue: "yt-dlp download failed"

**Solution:** Update yt-dlp:

```bash
pip3 install --upgrade yt-dlp
```

### Issue: "Upload to cloud failed"

**Solution:** Check WebDAV mount:

```bash
mount | grep 123pan
```

For more issues, see [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md).

## Next Steps

- Customize translation style in `translate_podcast.py`
- Set up automation for your favorite channels
- Integrate with your podcast workflow
- Share your feedback and improvements!

## Support

- GitHub Issues: [Report a problem](https://github.com/YOUR_USERNAME/youtube-to-podcast/issues)
- Documentation: [Full docs](README.md)
- Troubleshooting: [Help guide](references/TROUBLESHOOTING.md)

---

**Happy podcasting!** 🎙️
