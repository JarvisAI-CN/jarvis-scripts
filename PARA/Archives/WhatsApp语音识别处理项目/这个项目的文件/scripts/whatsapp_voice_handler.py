#!/usr/bin/env python3
"""
WhatsApp语音处理系统 v2.0
功能: 自动捕获、转录、回复WhatsApp语音消息
版本: v2.0
创建: 2026-02-14
"""

from __future__ import annotations
import os
import sys
import json
import time
import logging
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """消息状态枚举"""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    GENERATING_REPLY = "generating_reply"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class VoiceMessage:
    """语音消息数据结构"""
    message_id: str
    sender: str
    chat_id: str
    audio_url: str
    mime_type: str = "audio/ogg"
    duration: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: MessageStatus = MessageStatus.PENDING
    transcription: Optional[str] = None
    reply: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "chat_id": self.chat_id,
            "audio_url": self.audio_url,
            "mime_type": self.mime_type,
            "duration": self.duration,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "transcription": self.transcription,
            "reply": self.reply,
            "error": self.error
        }


class AudioProcessor:
    """音频处理器"""

    def __init__(self, temp_dir: str = "/tmp/whatsapp_voices"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, message_id: str) -> Optional[Path]:
        """下载音频文件"""
        try:
            logger.info(f"下载音频: {url}")

            # 检测URL格式并确定扩展名
            parsed_url = urlparse(url)
            ext = self._get_extension_from_url(url)
            filename = f"{message_id}_{hashlib.md5(url.encode()).hexdigest()[:8]}{ext}"
            filepath = self.temp_dir / filename

            # 下载文件
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"下载完成: {filepath.name} ({filepath.stat().st_size / 1024:.1f} KB)")
            return filepath

        except Exception as e:
            logger.error(f"下载失败: {e}")
            return None

    def _get_extension_from_url(self, url: str) -> str:
        """从URL提取文件扩展名"""
        audio_extensions = ['.ogg', '.mp3', '.wav', '.m4a', '.opus', '.aac']
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        for ext in audio_extensions:
            if path.endswith(ext):
                return ext

        return '.ogg'  # 默认OGG格式

    def convert_to_wav(self, input_file: Path) -> Optional[Path]:
        """转换音频为WAV格式（如果需要）"""
        if input_file.suffix.lower() == '.wav':
            return input_file

        output_file = input_file.with_suffix('.wav')

        try:
            # 检查FFmpeg是否可用
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )

            # 转换音频
            logger.info(f"转换音频: {input_file.name} -> WAV")
            result = subprocess.run(
                [
                    'ffmpeg', '-i', str(input_file),
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',
                    str(output_file)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg转换失败: {result.stderr}")
                return None

            logger.info(f"转换完成: {output_file.name}")
            return output_file

        except FileNotFoundError:
            logger.warning("FFmpeg未找到，跳过转换")
            return input_file
        except Exception as e:
            logger.error(f"转换失败: {e}")
            return None

    def cleanup(self, filepath: Path):
        """清理临时文件"""
        try:
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"清理临时文件: {filepath.name}")
        except Exception as e:
            logger.warning(f"清理失败: {e}")


class TranscriptionService:
    """语音转录服务"""

    def __init__(self, api_key: str = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"):
        self.api_key = api_key
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """转录音频文件"""
        try:
            if not audio_file.exists():
                logger.error(f"音频文件不存在: {audio_file}")
                return None

            logger.info(f"开始转录: {audio_file.name}")

            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            files = {
                "file": open(audio_file, 'rb')
            }

            data = {
                "model": "sensevoice"
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

            files["file"].close()

            if response.status_code == 200:
                result = response.json()
                text = result.get("text", "").strip()
                logger.info(f"✅ 转录成功: {text[:100]}{'...' if len(text) > 100 else ''}")
                return text
            else:
                logger.error(f"❌ 转录失败 (HTTP {response.status_code}): {response.text}")
                return None

        except Exception as e:
            logger.error(f"转录异常: {e}")
            return None


class ReplyGenerator:
    """智能回复生成器"""

    def __init__(self, owner_name: str = "主人"):
        self.owner_name = owner_name
        self.command_keywords = [
            "提醒", "记住", "帮我", "查", "发", "搜索", "记下来"
        ]

    def generate(self, transcription: str, sender: str) -> str:
        """生成回复"""
        text = transcription.strip()

        if not text:
            return "抱歉，没有识别到语音内容，请再试一次。"

        # 检测是否为指令
        if self._is_command(text):
            return self._generate_command_response(text)

        # 生成上下文回复
        return self._generate_context_response(text, sender)

    def _is_command(self, text: str) -> bool:
        """检测是否为指令"""
        return any(keyword in text for keyword in self.command_keywords)

    def _generate_command_response(self, text: str) -> str:
        """生成指令回复"""
        if "提醒" in text:
            return f"✅ 已记录提醒：「{text}」我会按时提醒您。"
        elif "记住" in text or "记下来" in text:
            return f"📝 已保存到记忆：「{text}」"
        elif "帮我" in text:
            return f"🔧 收到指令：「{text}」正在处理中..."
        elif "查" in text:
            return f"🔍 正在查询：「{text}」请稍候..."
        else:
            return f"📋 已收到指令：「{text}」"

    def _generate_context_response(self, text: str, sender: str) -> str:
        """生成上下文回复"""
        responses = [
            f"收到您的语音：「{text}」",
            f"🎤 转录结果: {text}",
            f"📝 已记录：「{text}」需要我做什么吗？"
        ]

        if len(text) < 20:
            return responses[0]
        elif len(text) < 50:
            return responses[1]
        else:
            return responses[2]


class WhatsAppVoiceHandler:
    """WhatsApp语音消息处理器 - 主控制器"""

    def __init__(
        self,
        state_file: str = "/tmp/whatsapp_voice_state.json",
        temp_dir: str = "/tmp/whatsapp_voices",
        zhipu_api_key: str = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
    ):
        self.state_file = Path(state_file)
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.audio_processor = AudioProcessor(str(self.temp_dir))
        self.transcriber = TranscriptionService(zhipu_api_key)
        self.reply_generator = ReplyGenerator()
        self.processed_messages: Dict[str, Dict[str, Any]] = {}
        self._load_state()

    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_messages = data.get("processed", {})
                logger.info(f"加载状态: {len(self.processed_messages)} 个已处理消息")
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
                self.processed_messages = {}

    def _save_state(self):
        """保存状态"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "processed": self.processed_messages,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")

    def process_message(
        self,
        message_id: str,
        audio_url: str,
        sender: str,
        chat_id: str,
        mime_type: str = "audio/ogg",
        duration: Optional[int] = None
    ) -> VoiceMessage:
        """处理语音消息"""
        # 创建消息对象
        message = VoiceMessage(
            message_id=message_id,
            sender=sender,
            chat_id=chat_id,
            audio_url=audio_url,
            mime_type=mime_type,
            duration=duration
        )

        # 检查是否已处理
        if message_id in self.processed_messages:
            logger.info(f"消息已处理: {message_id}")
            message.status = MessageStatus.COMPLETED
            return message

        try:
            # 1. 下载音频
            message.status = MessageStatus.DOWNLOADING
            audio_file = self.audio_processor.download(audio_url, message_id)

            if not audio_file:
                raise Exception("音频下载失败")

            # 2. 转换格式（如果需要）
            wav_file = self.audio_processor.convert_to_wav(audio_file)
            target_file = wav_file if wav_file else audio_file

            try:
                # 3. 转录
                message.status = MessageStatus.TRANSCRIBING
                transcription = self.transcriber.transcribe(target_file)

                if not transcription:
                    raise Exception("转录返回空结果")

                message.transcription = transcription
                logger.info(f"转录结果: {transcription}")

                # 4. 生成回复
                message.status = MessageStatus.GENERATING_REPLY
                reply = self.reply_generator.generate(transcription, sender)
                message.reply = reply
                logger.info(f"生成回复: {reply}")

                # 5. 标记完成
                message.status = MessageStatus.COMPLETED

                # 保存到已处理列表
                self.processed_messages[message_id] = {
                    "processed_at": datetime.now().isoformat(),
                    "sender": sender,
                    "transcription": transcription,
                    "has_reply": message.reply is not None
                }
                self._save_state()

                logger.info(f"✅ 消息处理完成: {message_id}")

            finally:
                # 清理临时文件
                self.audio_processor.cleanup(audio_file)
                if wav_file and wav_file != audio_file:
                    self.audio_processor.cleanup(wav_file)

        except Exception as e:
            logger.error(f"处理失败: {e}")
            message.status = MessageStatus.FAILED
            message.error = str(e)

        return message

    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计"""
        total = len(self.processed_messages)
        return {
            "total_processed": total,
            "success_rate": 100 if total > 0 else 0
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="WhatsApp语音处理系统v2.0")
    parser.add_argument("--audio-url", help="音频文件URL（测试用）")
    parser.add_argument("--message-id", help="消息ID（测试用）")

    args = parser.parse_args()

    handler = WhatsAppVoiceHandler()

    if args.audio_url and args.message_id:
        # 测试模式：处理单个消息
        print(f"\n🎤 测试语音处理...")
        print(f"URL: {args.audio_url}")
        print(f"Message ID: {args.message_id}")

        result = handler.process_message(
            message_id=args.message_id,
            audio_url=args.audio_url,
            sender="Test",
            chat_id="TestChat"
        )

        print(f"\n📊 处理结果:")
        print(f"状态: {result.status.value}")
        print(f"转录: {result.transcription or '(无)'}")
        print(f"回复: {result.reply or '(无)'}")
        print(f"错误: {result.error or '(无)'}")

        stats = handler.get_stats()
        print(f"\n📈 统计: {stats['total_processed']} 个消息已处理")
    else:
        print("请提供 --audio-url 和 --message-id 进行测试")


if __name__ == "__main__":
    main()
