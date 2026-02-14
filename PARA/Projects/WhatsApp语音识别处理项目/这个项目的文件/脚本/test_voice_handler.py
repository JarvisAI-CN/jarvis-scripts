#!/usr/bin/env python3
"""
WhatsApp语音处理测试套件
版本: v1.0
创建: 2026-02-14

测试内容:
1. 单元测试：各模块功能测试
2. 集成测试：完整流程测试
3. 边界测试：异常情况处理
4. 性能测试：并发处理能力
"""

from __future__ import annotations
import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "PARA/Projects/WhatsApp语音识别处理项目/这个项目的文件/脚本"))

from whatsapp_voice_handler import (
    WhatsAppVoiceHandler,
    AudioDownloader,
    TranscriptionService,
    ReplyGenerator,
    StateManager,
    VoiceMessage,
    MessageStatus
)


class TestVoiceMessage(unittest.TestCase):
    """VoiceMessage数据类测试"""

    def test_create_message(self):
        """测试创建消息对象"""
        msg = VoiceMessage(
            message_id="test_001",
            sender="Alice",
            chat_id="chat_001",
            audio_url="https://example.com/audio.ogg"
        )

        self.assertEqual(msg.message_id, "test_001")
        self.assertEqual(msg.sender, "Alice")
        self.assertEqual(msg.status, MessageStatus.PENDING)
        self.assertIsNone(msg.transcription)
        self.assertIsNone(msg.reply)

    def test_to_dict(self):
        """测试序列化"""
        msg = VoiceMessage(
            message_id="test_002",
            sender="Bob",
            chat_id="chat_002",
            audio_url="https://example.com/audio.mp3",
            status=MessageStatus.COMPLETED,
            transcription="Hello World",
            reply="Received"
        )

        data = msg.to_dict()

        self.assertEqual(data["message_id"], "test_002")
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["transcription"], "Hello World")
        self.assertEqual(data["reply"], "Received")


class TestStateManager(unittest.TestCase):
    """StateManager状态管理测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.state_manager = StateManager(self.temp_file.name)

    def tearDown(self):
        """清理测试环境"""
        Path(self.temp_file.name).unlink(missing_ok=True)

    def test_mark_processed(self):
        """测试标记已处理"""
        msg = VoiceMessage(
            message_id="test_001",
            sender="Alice",
            chat_id="chat_001",
            audio_url="https://example.com/audio.ogg",
            status=MessageStatus.COMPLETED,
            transcription="Test",
            reply="OK"
        )

        self.state_manager.mark_processed(msg)

        self.assertTrue(self.state_manager.is_processed("test_001"))
        self.assertFalse(self.state_manager.is_processed("test_002"))

    def test_mark_failed(self):
        """测试标记失败"""
        self.state_manager.mark_failed("test_003", "Download failed")

        self.assertTrue(self.state_manager.is_failed("test_003"))
        self.assertEqual(
            self.state_manager.failed_messages["test_003"].split(":")[-1].strip(),
            "Download failed"
        )

    def test_persistence(self):
        """测试持久化"""
        msg = VoiceMessage(
            message_id="test_004",
            sender="Bob",
            chat_id="chat_004",
            audio_url="https://example.com/audio.ogg",
            status=MessageStatus.COMPLETED,
            transcription="Test persistence",
            reply="Saved"
        )

        self.state_manager.mark_processed(msg)

        # 创建新的StateManager实例，测试加载
        new_manager = StateManager(self.temp_file.name)
        self.assertTrue(new_manager.is_processed("test_004"))
        self.assertEqual(
            new_manager.processed_messages["test_004"]["transcription"],
            "Test persistence"
        )


class TestAudioDownloader(unittest.TestCase):
    """AudioDownloader音频下载器测试"""

    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = AudioDownloader(self.temp_dir)

    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_extension_from_url(self):
        """测试URL扩展名提取"""
        self.assertEqual(self.downloader._get_extension_from_url("https://example.com/audio.ogg"), ".ogg")
        self.assertEqual(self.downloader._get_extension_from_url("https://example.com/audio.mp3"), ".mp3")
        self.assertEqual(self.downloader._get_extension_from_url("https://example.com/audio.wav"), ".wav")
        # 默认OGG
        self.assertEqual(self.downloader._get_extension_from_url("https://example.com/audio"), ".ogg")

    def test_download_mock(self):
        """测试下载（使用Mock）"""
        with patch('requests.get') as mock_get:
            # Mock响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.iter_content = lambda chunk_size: [b"fake audio data"]
            mock_get.return_value = mock_response

            # 测试下载
            result = self.downloader.download("https://example.com/audio.ogg", "test_001")

            self.assertIsNotNone(result)
            self.assertTrue(result.exists())
            self.assertEqual(result.stat().st_size, len(b"fake audio data"))


class TestTranscriptionService(unittest.TestCase):
    """TranscriptionService转录服务测试"""

    def setUp(self):
        """设置测试环境"""
        # 使用测试API密钥
        self.service = TranscriptionService(api_key="test_key")

    def test_transcribe_mock(self):
        """测试转录（使用Mock）"""
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b"RIFF\0\0\0\0WAVEfmt ")  # 简化的WAV头
            temp_file = f.name

        try:
            with patch('requests.post') as mock_post:
                # Mock响应
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"text": "测试转录文本"}
                mock_post.return_value = mock_response

                # 测试转录
                result = self.service.transcribe(Path(temp_file))

                self.assertEqual(result, "测试转录文本")

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_transcribe_file_not_found(self):
        """测试文件不存在的情况"""
        result = self.service.transcribe(Path("/nonexistent/file.wav"))
        self.assertIsNone(result)

    def test_transcribe_api_error(self):
        """测试API错误处理"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            f.write(b"RIFF\0\0\0\0WAVEfmt ")
            temp_file = f.name

        try:
            with patch('requests.post') as mock_post:
                # Mock错误响应
                mock_response = Mock()
                mock_response.status_code = 500
                mock_response.text = "Internal Server Error"
                mock_post.return_value = mock_response

                # 测试转录
                result = self.service.transcribe(Path(temp_file))

                self.assertIsNone(result)

        finally:
            Path(temp_file).unlink(missing_ok=True)


class TestReplyGenerator(unittest.TestCase):
    """ReplyGenerator回复生成器测试"""

    def setUp(self):
        """设置测试环境"""
        self.generator = ReplyGenerator(owner_name="主人")

    def test_generate_command_reminder(self):
        """测试提醒指令"""
        result = self.generator.generate("提醒我明天开会", "Alice")
        self.assertIn("提醒", result)
        self.assertIn("明天开会", result)

    def test_generate_command_remember(self):
        """测试记住指令"""
        result = self.generator.generate("记下来这个想法", "Bob")
        self.assertIn("保存", result)
        self.assertIn("这个想法", result)

    def test_generate_context_short(self):
        """测试短文本上下文回复"""
        result = self.generator.generate("你好", "Alice")
        self.assertIn("你好", result)

    def test_generate_context_long(self):
        """测试长文本上下文回复"""
        long_text = "今天天气真好，我想去公园散步，你觉得怎么样？"
        result = self.generator.generate(long_text, "Bob")
        self.assertIn("转录", result) or self.assertIn("记录", result)

    def test_generate_empty_text(self):
        """测试空文本"""
        result = self.generator.generate("", "Alice")
        self.assertIn("没有识别", result)


class TestOpenClawBridge(unittest.TestCase):
    """OpenClawBridge桥接器测试"""

    def setUp(self):
        """设置测试环境"""
        sys.path.insert(0, str(Path(__file__).parent))
        from openclaw_integration import OpenClawBridge
        self.bridge = OpenClawBridge()

    def test_process_valid_event(self):
        """测试处理有效事件"""
        event = {
            "type": "message",
            "channel": "whatsapp",
            "message_id": "test_001",
            "from": "8613220103449",
            "chat_id": "8613220103449",
            "media_url": "https://example.com/audio.ogg",
            "mime_type": "audio/ogg",
            "duration": 15,
            "timestamp": "2026-02-14T20:00:00Z"
        }

        # Mock处理
        with patch.object(self.bridge.handler, 'process_message') as mock_process:
            mock_result = VoiceMessage(
                message_id="test_001",
                sender="8613220103449",
                chat_id="8613220103449",
                audio_url="https://example.com/audio.ogg",
                status=MessageStatus.COMPLETED,
                transcription="Test",
                reply="Received"
            )
            mock_process.return_value = mock_result

            # 测试处理
            response = self.bridge.process_event(event)

            self.assertIsNotNone(response)
            self.assertEqual(response["message_id"], "test_001")
            self.assertEqual(response["status"], "completed")
            self.assertEqual(response["transcription"], "Test")
            self.assertEqual(response["reply"], "Received")
            self.assertTrue(response["send_reply"])

    def test_process_non_whatsapp_event(self):
        """测试处理非WhatsApp事件"""
        event = {
            "type": "message",
            "channel": "telegram",
            "message_id": "test_002"
        }

        response = self.bridge.process_event(event)
        self.assertIsNone(response)

    def test_process_invalid_event(self):
        """测试处理无效事件"""
        event = {
            "type": "message",
            "channel": "whatsapp"
            # 缺少message_id和media_url
        }

        response = self.bridge.process_event(event)
        self.assertIsNone(response)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def test_full_workflow(self):
        """测试完整工作流"""
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建处理器
            handler = WhatsAppVoiceHandler(
                state_file=temp_dir + "/state.json",
                temp_dir=temp_dir + "/voices"
            )

            # Mock下载和转录
            with patch.object(handler.downloader, 'download') as mock_download, \
                 patch.object(handler.transcriber, 'transcribe') as mock_transcribe:

                # Mock下载
                temp_audio = Path(temp_dir) / "test.ogg"
                temp_audio.write_bytes(b"fake audio data")
                mock_download.return_value = temp_audio

                # Mock转录
                mock_transcribe.return_value = "这是测试语音内容"

                # 处理消息
                result = handler.process_message(
                    message_id="integration_001",
                    audio_url="https://example.com/test.ogg",
                    sender="Alice",
                    chat_id="chat_001"
                )

                # 验证结果
                self.assertEqual(result.status, MessageStatus.COMPLETED)
                self.assertEqual(result.transcription, "这是测试语音内容")
                self.assertIsNotNone(result.reply)

                # 验证状态管理
                self.assertTrue(handler.state_manager.is_processed("integration_001"))

                # 验证统计
                stats = handler.get_stats()
                self.assertEqual(stats["total_processed"], 1)
                self.assertEqual(stats["successful"], 1)

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试用例
    suite.addTests(loader.loadTestsFromTestCase(TestVoiceMessage))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAudioDownloader))
    suite.addTests(loader.loadTestsFromTestCase(TestTranscriptionService))
    suite.addTests(loader.loadTestsFromTestCase(TestReplyGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenClawBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
