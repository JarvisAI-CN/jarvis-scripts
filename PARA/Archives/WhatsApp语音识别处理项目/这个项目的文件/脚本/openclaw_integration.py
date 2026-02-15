#!/usr/bin/env python3
"""
OpenClaw集成模块 - WhatsApp语音处理
版本: v1.0
创建: 2026-02-14

功能:
1. 作为OpenClaw子进程运行
2. 监听WhatsApp消息事件
3. 自动处理语音消息
4. 发送转录结果和回复

使用方式:
1. 在OpenClaw配置中添加监听规则
2. 运行此脚本作为独立服务
3. 通过stdin接收消息事件（JSON格式）
"""

from __future__ import annotations
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目路径到sys.path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "PARA/Projects/WhatsApp语音识别处理项目/这个项目的文件/脚本"))

from whatsapp_voice_handler import (
    WhatsAppVoiceHandler,
    VoiceMessage,
    MessageStatus,
    StateManager
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [WhatsAppVoice] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class OpenClawBridge:
    """
    OpenClaw桥接器

    接收OpenClaw消息事件，处理语音消息，返回回复
    """

    def __init__(self):
        self.handler = WhatsAppVoiceHandler()
        self.running = True

    def process_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        处理OpenClaw消息事件

        Args:
            event: 事件字典，格式:
                {
                    "type": "message",
                    "channel": "whatsapp",
                    "message_id": "3EB0xxx",
                    "from": "8613220103449",
                    "chat_id": "8613220103449",
                    "media_url": "https://...",
                    "mime_type": "audio/ogg",
                    "duration": 15,
                    "timestamp": "2026-02-14T20:00:00Z"
                }

        Returns:
            响应字典，格式:
                {
                    "message_id": "3EB0xxx",
                    "status": "completed",
                    "transcription": "转录文本",
                    "reply": "回复文本",
                    "send_reply": True
                }
        """
        try:
            # 验证事件类型
            if event.get("type") != "message":
                logger.debug(f"Ignoring non-message event: {event.get('type')}")
                return None

            if event.get("channel") != "whatsapp":
                logger.debug(f"Ignoring non-WhatsApp message: {event.get('channel')}")
                return None

            # 提取消息信息
            message_id = event.get("message_id") or event.get("id")
            media_url = event.get("media_url") or event.get("audio_url")

            if not message_id or not media_url:
                logger.warning("Missing message_id or media_url in event")
                return None

            # 处理语音消息
            logger.info(f"Processing voice message {message_id}")
            result = self.handler.process_message(
                message_id=message_id,
                audio_url=media_url,
                sender=event.get("from", "Unknown"),
                chat_id=event.get("chat_id", event.get("from", "Unknown")),
                mime_type=event.get("mime_type", "audio/ogg"),
                duration=event.get("duration")
            )

            # 构建响应
            response = {
                "message_id": message_id,
                "status": result.status.value,
                "transcription": result.transcription,
                "reply": result.reply,
                "send_reply": result.status == MessageStatus.COMPLETED and result.reply is not None,
                "error": result.error
            }

            logger.info(f"Processed: {message_id} - {result.status.value}")
            return response

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def run(self):
        """
        主循环：从stdin读取事件并处理

        输入格式（每行一个JSON）:
            {"type": "message", "channel": "whatsapp", ...}

        输出格式（每行一个JSON）:
            {"status": "completed", "transcription": "...", "reply": "..."}
        """
        logger.info("OpenClaw Bridge started, waiting for events...")

        try:
            for line in sys.stdin:
                if not self.running:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                    response = self.process_event(event)

                    if response:
                        # 输出响应（stdout）
                        print(json.dumps(response, ensure_ascii=False))
                        sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON input: {e}")
                except Exception as e:
                    logger.error(f"Error processing line: {e}", exc_info=True)

        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down...")
        finally:
            logger.info("OpenClaw Bridge stopped")

    def stop(self):
        """停止服务"""
        self.running = False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="OpenClaw WhatsApp Voice Handler")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (process one event from stdin and exit)"
    )
    parser.add_argument(
        "--cleanup-days",
        type=int,
        default=7,
        help="Cleanup records older than N days (default: 7)"
    )
    parser.add_argument(
        "--cleanup-only",
        action="store_true",
        help="Only cleanup old records and exit"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics and exit"
    )

    args = parser.parse_args()

    bridge = OpenClawBridge()

    # 清理旧记录
    bridge.handler.cleanup_old_records(args.cleanup_days)

    # 如果只是清理，退出
    if args.cleanup_only:
        logger.info("Cleanup completed")
        return

    # 显示统计
    if args.stats:
        stats = bridge.handler.get_stats()
        print("\n📊 WhatsApp语音处理统计:")
        print(f"总处理: {stats['total_processed']}")
        print(f"成功: {stats['successful']}")
        print(f"失败: {stats['failed']}")
        print(f"成功率: {stats['success_rate']:.1f}%")
        print(f"平均时长: {stats['avg_duration']:.1f}秒")
        return

    # 测试模式
    if args.test:
        logger.info("Running in test mode...")
        try:
            event = json.loads(sys.stdin.readline())
            response = bridge.process_event(event)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Test failed: {e}", exc_info=True)
        return

    # 正常模式：持续监听
    bridge.run()


if __name__ == "__main__":
    main()
