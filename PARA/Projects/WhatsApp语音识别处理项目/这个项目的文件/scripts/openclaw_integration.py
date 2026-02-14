#!/usr/bin/env python3
"""
OpenClaw WhatsApp集成模块
功能：将语音处理器集成到OpenClaw消息框架
版本: v1.0
创建: 2026-02-14
"""

from __future__ import annotations
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "这个项目的文件/scripts"))

try:
    from whatsapp_voice_handler import WhatsAppVoiceHandler, VoiceMessage, MessageStatus
except ImportError:
    # 如果导入失败，使用相对导入
    sys.path.insert(0, str(Path(__file__).parent))
    from whatsapp_voice_handler import WhatsAppVoiceHandler, VoiceMessage, MessageStatus

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class OpenClawWhatsAppIntegration:
    """
    OpenClaw WhatsApp集成类

    功能:
    - 监听WhatsApp语音消息
    - 调用WhatsAppVoiceHandler处理
    - 发送回复到WhatsApp
    - 错误处理和日志记录
    """

    def __init__(
        self,
        handler: Optional[WhatsAppVoiceHandler] = None,
        openclaw_bin: str = "openclaw"
    ):
        self.handler = handler or WhatsAppVoiceHandler()
        self.openclaw_bin = openclaw_bin
        self.stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_failed": 0,
            "total_replies": 0
        }

    def detect_voice_message(self, message_data: Dict[str, Any]) -> bool:
        """
        检测是否为语音消息

        Args:
            message_data: OpenClaw消息数据

        Returns:
            bool: 是否为语音消息
        """
        # 检查消息类型
        message_type = message_data.get("type", "")

        if message_type in ["voice", "audio", "ptt"]:
            return True

        # 检查是否有音频URL
        if "audio_url" in message_data:
            return True

        # 检查是否有媒体附件
        media = message_data.get("media", {})
        if media.get("mime_type", "").startswith("audio/"):
            return True

        return False

    def extract_message_info(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        从OpenClaw消息数据提取信息

        Args:
            message_data: OpenClaw消息数据

        Returns:
            提取的消息信息或None
        """
        try:
            message_id = message_data.get("id") or message_data.get("message_id")
            sender = message_data.get("from") or message_data.get("sender")
            chat_id = message_data.get("chat_id") or message_data.get("chat")
            audio_url = message_data.get("audio_url") or message_data.get("media", {}).get("url")
            mime_type = message_data.get("mime_type") or message_data.get("media", {}).get("mime_type", "audio/ogg")
            duration = message_data.get("duration") or message_data.get("media", {}).get("duration")

            if not all([message_id, sender, chat_id, audio_url]):
                logger.error(f"缺少必要字段: message_id={message_id}, sender={sender}, chat_id={chat_id}, audio_url={audio_url}")
                return None

            return {
                "message_id": message_id,
                "sender": sender,
                "chat_id": chat_id,
                "audio_url": audio_url,
                "mime_type": mime_type,
                "duration": duration
            }
        except Exception as e:
            logger.error(f"提取消息信息失败: {e}")
            return None

    def process_whatsapp_message(self, message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理WhatsApp消息（主入口）

        Args:
            message_data: OpenClaw消息数据

        Returns:
            处理结果或None
        """
        self.stats["total_received"] += 1

        try:
            # 检测是否为语音消息
            if not self.detect_voice_message(message_data):
                logger.debug("不是语音消息，跳过")
                return None

            # 提取消息信息
            msg_info = self.extract_message_info(message_data)
            if not msg_info:
                logger.error("无法提取消息信息")
                self.stats["total_failed"] += 1
                return None

            logger.info(f"收到语音消息: {msg_info['message_id']} from {msg_info['sender']}")

            # 调用处理器
            result = self.handler.process_message(
                message_id=msg_info["message_id"],
                audio_url=msg_info["audio_url"],
                sender=msg_info["sender"],
                chat_id=msg_info["chat_id"],
                mime_type=msg_info["mime_type"],
                duration=msg_info.get("duration")
            )

            if result.status == MessageStatus.COMPLETED:
                self.stats["total_processed"] += 1
                logger.info(f"✅ 处理成功: {result.message_id}")

                # 发送回复
                if result.reply:
                    self.send_reply(
                        chat_id=msg_info["chat_id"],
                        message=result.reply,
                        reply_to=msg_info["message_id"]
                    )
                    self.stats["total_replies"] += 1

                return {
                    "status": "success",
                    "message_id": result.message_id,
                    "transcription": result.transcription,
                    "reply": result.reply
                }
            else:
                self.stats["total_failed"] += 1
                logger.error(f"❌ 处理失败: {result.error}")
                return {
                    "status": "failed",
                    "message_id": result.message_id,
                    "error": result.error
                }

        except Exception as e:
            logger.error(f"处理异常: {e}", exc_info=True)
            self.stats["total_failed"] += 1
            return {
                "status": "error",
                "error": str(e)
            }

    def send_reply(self, chat_id: str, message: str, reply_to: Optional[str] = None) -> bool:
        """
        发送回复到WhatsApp

        Args:
            chat_id: 聊天ID
            message: 消息内容
            reply_to: 回复的消息ID（可选）

        Returns:
            bool: 是否发送成功
        """
        try:
            # 构建命令
            cmd = [
                self.openclaw_bin,
                "message",
                "send",
                "whatsapp",
                "--to", chat_id,
                "--message", message
            ]

            if reply_to:
                cmd.extend(["--reply-to", reply_to])

            logger.info(f"发送回复: {message[:50]}{'...' if len(message) > 50 else ''}")

            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("✅ 回复发送成功")
                return True
            else:
                logger.error(f"❌ 回复发送失败: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"发送回复异常: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息

        Returns:
            统计数据
        """
        handler_stats = self.handler.get_stats()
        return {
            **handler_stats,
            "total_received": self.stats["total_received"],
            "total_processed": self.stats["total_processed"],
            "total_failed": self.stats["total_failed"],
            "total_replies": self.stats["total_replies"],
            "success_rate": round(self.stats["total_processed"] / max(self.stats["total_received"], 1) * 100, 2)
        }

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_failed": 0,
            "total_replies": 0
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw WhatsApp集成测试")
    parser.add_argument("--test-message", help="测试消息JSON文件")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")

    args = parser.parse_args()

    integration = OpenClawWhatsAppIntegration()

    if args.stats:
        # 显示统计信息
        stats = integration.get_stats()
        print("\n📊 OpenClaw WhatsApp集成统计")
        print("=" * 50)
        for key, value in stats.items():
            print(f"{key}: {value}")

    elif args.test_message:
        # 测试模式
        try:
            with open(args.test_message, 'r', encoding='utf-8') as f:
                test_data = json.load(f)

            print(f"\n🧪 测试消息处理")
            print(f"文件: {args.test_message}")
            result = integration.process_whatsapp_message(test_data)
            print(f"\n结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
    else:
        print("请使用 --stats 或 --test-message 参数")


if __name__ == "__main__":
    main()
