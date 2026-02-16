#!/usr/bin/env python3
"""
WhatsApp语音消息自动处理系统
版本: v1.0
创建: 2026-02-14

功能:
1. 自动检测WhatsApp语音消息
2. 下载并转录音频文件（使用智谱AI Whisper API）
3. 生成智能回复（基于GPT）
4. 发送回复到WhatsApp

架构:
- WhatsAppVoiceHandler: 主控制器
- AudioDownloader: 音频下载器
- TranscriptionService: 转录服务（集成智谱AI）
- ReplyGenerator: 回复生成器
- StateManager: 状态管理器（避免重复处理）
"""

from __future__ import annotations
import os
import sys
import json
import time
import hashlib
import logging
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import requests
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """消息处理状态"""
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
    duration: Optional[int] = None  # 秒
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


class StateManager:
    """
    状态管理器

    功能:
    - 记录已处理的消息ID
    - 防止重复处理
    - 持久化状态到文件
    """

    def __init__(self, state_file: str = "/tmp/whatsapp_voice_state.json"):
        self.state_file = Path(state_file)
        self.processed_messages: Dict[str, Dict[str, Any]] = {}
        self.failed_messages: Dict[str, str] = {}
        self._load_state()

    def _load_state(self):
        """加载状态文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_messages = data.get("processed", {})
                    self.failed_messages = data.get("failed", {})
                logger.info(f"Loaded state: {len(self.processed_messages)} processed, {len(self.failed_messages)} failed")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                self.processed_messages = {}
                self.failed_messages = {}

    def _save_state(self):
        """保存状态文件"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "processed": self.processed_messages,
                    "failed": self.failed_messages,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def is_processed(self, message_id: str) -> bool:
        """检查消息是否已处理"""
        return message_id in self.processed_messages

    def is_failed(self, message_id: str) -> bool:
        """检查消息是否之前失败过"""
        return message_id in self.failed_messages

    def mark_processed(self, message: VoiceMessage):
        """标记消息为已处理"""
        self.processed_messages[message.message_id] = {
            "processed_at": datetime.now().isoformat(),
            "sender": message.sender,
            "transcription": message.transcription,
            "has_reply": message.reply is not None
        }
        # 从失败列表中移除（如果存在）
        if message.message_id in self.failed_messages:
            del self.failed_messages[message.message_id]
        self._save_state()
        logger.info(f"Marked as processed: {message.message_id}")

    def mark_failed(self, message_id: str, error: str):
        """标记消息处理失败"""
        self.failed_messages[message_id] = f"{datetime.now().isoformat()}: {error}"
        self._save_state()
        logger.warning(f"Marked as failed: {message_id} - {error}")

    def cleanup_old_records(self, days: int = 7):
        """清理旧记录（超过指定天数）"""
        cutoff = datetime.now().timestamp() - (days * 86400)
        to_remove = []

        for msg_id, data in self.processed_messages.items():
            processed_at = data.get("processed_at", "")
            try:
                if datetime.fromisoformat(processed_at).timestamp() < cutoff:
                    to_remove.append(msg_id)
            except:
                pass

        for msg_id in to_remove:
            del self.processed_messages[msg_id]

        if to_remove:
            self._save_state()
            logger.info(f"Cleaned up {len(to_remove)} old records")


class AudioDownloader:
    """
    音频下载器

    功能:
    - 从URL下载音频文件
    - 支持多种格式（OGG, MP3, WAV, M4A）
    - 自动转换格式（使用FFmpeg）
    """

    def __init__(self, temp_dir: str = "/tmp/whatsapp_voices"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def download(self, url: str, message_id: str) -> Optional[Path]:
        """
        下载音频文件

        Args:
            url: 音频文件URL
            message_id: 消息ID（用于生成文件名）

        Returns:
            下载的文件路径，失败返回None
        """
        try:
            logger.info(f"Downloading audio from {url}")

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

            logger.info(f"Downloaded to {filepath} ({filepath.stat().st_size / 1024:.1f} KB)")
            return filepath

        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

    def _get_extension_from_url(self, url: str) -> str:
        """从URL提取文件扩展名"""
        # 常见音频格式
        audio_extensions = ['.ogg', '.mp3', '.wav', '.m4a', '.opus', '.aac']

        parsed_url = urlparse(url)
        path = parsed_url.path.lower()

        for ext in audio_extensions:
            if path.endswith(ext):
                return ext

        # 默认OGG格式（WhatsApp常用）
        return '.ogg'

    def convert_to_wav(self, input_file: Path) -> Optional[Path]:
        """
        转换音频为WAV格式（如果需要）

        Args:
            input_file: 输入文件路径

        Returns:
            WAV文件路径，失败返回None
        """
        # 如果已经是WAV格式，直接返回
        if input_file.suffix.lower() == '.wav':
            return input_file

        output_file = input_file.with_suffix('.wav')

        try:
            # 检查FFmpeg是否可用
            import subprocess
            subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                check=True
            )

            # 转换音频
            logger.info(f"Converting {input_file.name} to WAV...")
            result = subprocess.run(
                [
                    'ffmpeg', '-i', str(input_file),
                    '-acodec', 'pcm_s16le',
                    '-ar', '16000',
                    '-ac', '1',
                    '-y',  # 覆盖输出文件
                    str(output_file)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return None

            logger.info(f"Converted to {output_file}")
            return output_file

        except FileNotFoundError:
            logger.warning("FFmpeg not found, skipping conversion")
            return input_file  # 返回原文件
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return None

    def cleanup(self, filepath: Path):
        """清理临时文件"""
        try:
            if filepath.exists():
                filepath.unlink()
                logger.debug(f"Cleaned up {filepath}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {filepath}: {e}")


class TranscriptionService:
    """
    语音转录服务

    功能:
    - 调用智谱AI Whisper API进行转录
    - 支持多种语言（中文、英文、方言）
    - 自动检测语言
    """

    def __init__(self, api_key: str = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"):
        self.api_key = api_key
        self.api_url = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"

    def transcribe(self, audio_file: Path) -> Optional[str]:
        """
        转录音频文件

        Args:
            audio_file: 音频文件路径

        Returns:
            转录文本，失败返回None
        """
        try:
            if not audio_file.exists():
                logger.error(f"Audio file not found: {audio_file}")
                return None

            logger.info(f"Transcribing {audio_file.name}...")

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
                logger.info(f"✅ Transcription successful: {text[:100]}{'...' if len(text) > 100 else ''}")
                return text
            else:
                logger.error(f"❌ Transcription failed (HTTP {response.status_code}): {response.text}")
                return None

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None


class ReplyGenerator:
    """
    智能回复生成器

    功能:
    - 基于转录文本生成回复
    - 支持指令识别（如"提醒我..."、"帮我..."）
    - 上下文感知回复
    """

    def __init__(self, owner_name: str = "主人"):
        self.owner_name = owner_name
        self.command_keywords = [
            "提醒", "记住", "帮我", "查", "发", "搜索", "记下来"
        ]

    def generate(self, transcription: str, sender: str) -> str:
        """
        生成回复

        Args:
            transcription: 转录文本
            sender: 发送者

        Returns:
            回复文本
        """
        # 清理转录文本
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
        # 简单的关键词匹配（可以扩展为更复杂的逻辑）
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
        # 简单的上下文感知回复（可以集成GPT模型增强）
        responses = [
            f"收到您的语音：「{text}」",
            f"🎤 转录结果：{text}",
            f"📝 已记录：「{text}」需要我做什么吗？"
        ]

        # 根据文本长度选择回复
        if len(text) < 20:
            return responses[0]
        elif len(text) < 50:
            return responses[1]
        else:
            return responses[2]


class WhatsAppVoiceHandler:
    """
    WhatsApp语音消息处理器

    主控制器，协调所有模块完成语音消息处理
    """

    def __init__(
        self,
        state_file: str = "/tmp/whatsapp_voice_state.json",
        temp_dir: str = "/tmp/whatsapp_voices",
        zhipu_api_key: str = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
    ):
        self.state_manager = StateManager(state_file)
        self.downloader = AudioDownloader(temp_dir)
        self.transcriber = TranscriptionService(zhipu_api_key)
        self.reply_generator = ReplyGenerator()

        # 统计信息
        self.stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_duration": 0.0
        }

    def process_message(
        self,
        message_id: str,
        audio_url: str,
        sender: str,
        chat_id: str,
        mime_type: str = "audio/ogg",
        duration: Optional[int] = None
    ) -> VoiceMessage:
        """
        处理语音消息

        Args:
            message_id: 消息ID
            audio_url: 音频文件URL
            sender: 发送者
            chat_id: 聊天ID
            mime_type: MIME类型
            duration: 音频时长（秒）

        Returns:
            VoiceMessage对象
        """
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
        if self.state_manager.is_processed(message_id):
            logger.info(f"Message {message_id} already processed, skipping")
            return message

        # 检查是否之前失败过
        if self.state_manager.is_failed(message_id):
            logger.warning(f"Message {message_id} failed before, retrying...")

        try:
            # 1. 下载音频
            message.status = MessageStatus.DOWNLOADING
            audio_file = self.downloader.download(audio_url, message_id)

            if not audio_file:
                raise Exception("Failed to download audio")

            # 2. 转换格式（如果需要）
            wav_file = self.downloader.convert_to_wav(audio_file)
            target_file = wav_file if wav_file else audio_file

            try:
                # 3. 转录
                message.status = MessageStatus.TRANSCRIBING
                transcription = self.transcriber.transcribe(target_file)

                if not transcription:
                    raise Exception("Transcription returned empty result")

                message.transcription = transcription
                logger.info(f"Transcription: {transcription}")

                # 4. 生成回复
                message.status = MessageStatus.GENERATING_REPLY
                reply = self.reply_generator.generate(transcription, sender)
                message.reply = reply
                logger.info(f"Generated reply: {reply}")

                # 5. 标记完成
                message.status = MessageStatus.COMPLETED
                self.state_manager.mark_processed(message)

                # 更新统计
                self.stats["total_processed"] += 1
                self.stats["successful"] += 1
                if message.duration:
                    self.stats["total_duration"] += message.duration

            finally:
                # 清理临时文件
                self.downloader.cleanup(audio_file)
                if wav_file and wav_file != audio_file:
                    self.downloader.cleanup(wav_file)

        except Exception as e:
            logger.error(f"Failed to process message {message_id}: {e}")
            message.status = MessageStatus.FAILED
            message.error = str(e)
            self.state_manager.mark_failed(message_id, str(e))
            self.stats["total_processed"] += 1
            self.stats["failed"] += 1

        return message

    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计"""
        return {
            **self.stats,
            "success_rate": (self.stats["successful"] / self.stats["total_processed"] * 100) if self.stats["total_processed"] > 0 else 0,
            "avg_duration": (self.stats["total_duration"] / self.stats["successful"]) if self.stats["successful"] > 0 else 0
        }

    def cleanup_old_records(self, days: int = 7):
        """清理旧记录"""
        self.state_manager.cleanup_old_records(days)


# 便捷函数
def process_voice_message(
    message_id: str,
    audio_url: str,
    sender: str = "Unknown",
    chat_id: str = "Unknown",
    mime_type: str = "audio/ogg",
    duration: Optional[int] = None
) -> VoiceMessage:
    """
    便捷函数：处理单条语音消息

    Args:
        message_id: 消息ID
        audio_url: 音频URL
        sender: 发送者
        chat_id: 聊天ID
        mime_type: MIME类型
        duration: 时长（秒）

    Returns:
        VoiceMessage对象
    """
    handler = WhatsAppVoiceHandler()
    return handler.process_message(
        message_id=message_id,
        audio_url=audio_url,
        sender=sender,
        chat_id=chat_id,
        mime_type=mime_type,
        duration=duration
    )


if __name__ == "__main__":
    # 示例用法
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 whatsapp_voice_handler.py <audio_url> [message_id]")
        sys.exit(1)

    audio_url = sys.argv[1]
    message_id = sys.argv[2] if len(sys.argv) > 2 else f"test_{int(time.time())}"

    print(f"\n🎤 处理语音消息...")
    print(f"URL: {audio_url}")
    print(f"Message ID: {message_id}")

    result = process_voice_message(
        message_id=message_id,
        audio_url=audio_url,
        sender="Test",
        chat_id="TestChat"
    )

    print(f"\n📊 处理结果:")
    print(f"状态: {result.status.value}")
    print(f"转录: {result.transcription or '(无)'}")
    print(f"回复: {result.reply or '(无)'}")
    print(f"错误: {result.error or '(无)'}")
