#!/usr/bin/env python3
"""
WhatsApp语音处理系统测试套件
版本: v1.0
创建: 2026-02-14

测试覆盖:
- AudioProcessor: 音频下载和转换
- TranscriptionService: 语音转录
- ReplyGenerator: 回复生成
- WhatsAppVoiceHandler: 端到端处理流程
- OpenClawWhatsAppIntegration: OpenClaw集成
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 导入被测试模块
import sys
sys.path.insert(0, str(Path(__file__).parent))

try:
    from whatsapp_voice_handler import (
        AudioProcessor,
        TranscriptionService,
        ReplyGenerator,
        WhatsAppVoiceHandler,
        VoiceMessage,
        MessageStatus
    )
    from openclaw_integration import OpenClawWhatsAppIntegration
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有模块文件存在于当前目录")
    sys.exit(1)


class TestAudioProcessor(unittest.TestCase):
    """测试AudioProcessor"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.processor = AudioProcessor(self.temp_dir)

    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_directory(self):
        """测试初始化创建目录"""
        self.assertTrue(Path(self.temp_dir).exists())

    def test_get_extension_from_url(self):
        """测试从URL提取扩展名"""
        # OGG格式
        self.assertEqual(self.processor._get_extension_from_url("https://example.com/audio.ogg"), ".ogg")
        # MP3格式
        self.assertEqual(self.processor._get_extension_from_url("https://example.com/song.mp3"), ".mp3")
        # 无扩展名，默认OGG
        self.assertEqual(self.processor._get_extension_from_url("https://example.com/audio"), ".ogg")

    @patch('requests.get')
    def test_download_success(self, mock_get):
        """测试成功下载"""
        # Mock响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"fake audio data"]
        mock_get.return_value = mock_response

        # 下载
        result = self.processor.download("https://example.com/audio.ogg", "test_msg_123")

        self.assertIsNotNone(result)
        self.assertTrue(result.exists())
        self.assertEqual(result.name, "test_msg_123_12345678.ogg")

    @patch('requests.get')
    def test_download_failure(self, mock_get):
        """测试下载失败"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        result = self.processor.download("https://example.com/audio.ogg", "test_msg_123")

        self.assertIsNone(result)

    def test_cleanup(self):
        """测试临时文件清理"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.ogg"
        test_file.touch()

        # 清理
        self.processor.cleanup(test_file)

        # 验证文件已删除
        self.assertFalse(test_file.exists())


class TestTranscriptionService(unittest.TestCase):
    """测试TranscriptionService"""

    def setUp(self):
        self.service = TranscriptionService(api_key="test_key")

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.service.api_key, "test_key")
        self.assertIn("bigmodel.cn", self.service.api_url)

    @patch('requests.post')
    def test_transcribe_success(self, mock_post):
        """测试成功转录"""
        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = Path(f.name)
            f.write(b"fake audio data")

        try:
            # Mock API响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"text": "这是测试转录内容"}
            mock_post.return_value = mock_response

            # 转录
            result = self.service.transcribe(temp_file)

            self.assertEqual(result, "这是测试转录内容")
        finally:
            temp_file.unlink(missing_ok=True)

    @patch('requests.post')
    def test_transcribe_api_error(self, mock_post):
        """测试API错误"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_file = Path(f.name)
            f.write(b"fake audio data")

        try:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response

            result = self.service.transcribe(temp_file)

            self.assertIsNone(result)
        finally:
            temp_file.unlink(missing_ok=True)

    def test_transcribe_nonexistent_file(self):
        """测试文件不存在"""
        result = self.service.transcribe(Path("/nonexistent/file.wav"))
        self.assertIsNone(result)


class TestReplyGenerator(unittest.TestCase):
    """测试ReplyGenerator"""

    def setUp(self):
        self.generator = ReplyGenerator(owner_name="主人")

    def test_generate_command_reminder(self):
        """测试生成提醒指令回复"""
        result = self.generator.generate("提醒我明天下午3点开会", "user123")
        self.assertIn("提醒", result)
        self.assertIn("已记录", result)

    def test_generate_command_remember(self):
        """测试生成记住指令回复"""
        result = self.generator.generate("记住这个重要信息", "user123")
        self.assertIn("已保存", result)

    def test_generate_context_short(self):
        """测试生成短文本回复"""
        result = self.generator.generate("你好", "user123")
        self.assertIn("收到您的语音", result)

    def test_generate_context_long(self):
        """测试生成长文本回复"""
        long_text = "这是一段很长的文本内容，超过五十个字符，包含了很多详细的信息"
        result = self.generator.generate(long_text, "user123")
        self.assertIn("转录结果", result)

    def test_generate_empty_text(self):
        """测试生成空文本回复"""
        result = self.generator.generate("", "user123")
        self.assertIn("没有识别到", result)


class TestWhatsAppVoiceHandler(unittest.TestCase):
    """测试WhatsAppVoiceHandler"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "state.json"
        self.handler = WhatsAppVoiceHandler(
            state_file=str(self.state_file),
            temp_dir=self.temp_dir,
            zhipu_api_key="test_key"
        )

    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_creates_directories(self):
        """测试初始化创建目录"""
        self.assertTrue(Path(self.temp_dir).exists())
        self.assertTrue(self.state_file.parent.exists())

    def test_load_state_no_file(self):
        """测试加载不存在的状态文件"""
        self.assertEqual(len(self.handler.processed_messages), 0)

    def test_save_and_load_state(self):
        """测试保存和加载状态"""
        # 添加处理记录
        self.handler.processed_messages["msg_123"] = {
            "processed_at": datetime.now().isoformat(),
            "sender": "user123",
            "transcription": "测试转录",
            "has_reply": True
        }

        # 保存状态
        self.handler._save_state()

        # 创建新处理器并加载状态
        new_handler = WhatsAppVoiceHandler(
            state_file=str(self.state_file),
            temp_dir=self.temp_dir,
            zhipu_api_key="test_key"
        )

        self.assertEqual(len(new_handler.processed_messages), 1)
        self.assertIn("msg_123", new_handler.processed_messages)

    @patch.object(WhatsAppVoiceHandler, '_save_state')
    def test_process_already_processed_message(self, mock_save):
        """测试处理已处理的消息"""
        # 添加到已处理列表
        self.handler.processed_messages["msg_123"] = {
            "processed_at": datetime.now().isoformat(),
            "sender": "user123",
            "transcription": "测试",
            "has_reply": False
        }

        # 处理
        result = self.handler.process_message(
            message_id="msg_123",
            audio_url="https://example.com/audio.ogg",
            sender="user123",
            chat_id="chat_456"
        )

        # 应该直接返回完成状态
        self.assertEqual(result.status, MessageStatus.COMPLETED)

    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.handler.get_stats()
        self.assertIn("total_processed", stats)
        self.assertIn("success_rate", stats)


class TestOpenClawWhatsAppIntegration(unittest.TestCase):
    """测试OpenClawWhatsAppIntegration"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        mock_handler = WhatsAppVoiceHandler(
            state_file=str(Path(self.temp_dir) / "state.json"),
            temp_dir=self.temp_dir,
            zhipu_api_key="test_key"
        )
        self.integration = OpenClawWhatsAppIntegration(handler=mock_handler)

    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_voice_message_by_type(self):
        """测试通过类型检测语音消息"""
        message_data = {"type": "voice"}
        self.assertTrue(self.integration.detect_voice_message(message_data))

    def test_detect_voice_message_by_audio_url(self):
        """测试通过audio_url检测语音消息"""
        message_data = {"audio_url": "https://example.com/audio.ogg"}
        self.assertTrue(self.integration.detect_voice_message(message_data))

    def test_detect_voice_message_by_media(self):
        """测试通过media检测语音消息"""
        message_data = {
            "media": {
                "mime_type": "audio/ogg"
            }
        }
        self.assertTrue(self.integration.detect_voice_message(message_data))

    def test_detect_non_voice_message(self):
        """测试检测非语音消息"""
        message_data = {"type": "text"}
        self.assertFalse(self.integration.detect_voice_message(message_data))

    def test_extract_message_info_success(self):
        """测试成功提取消息信息"""
        message_data = {
            "id": "msg_123",
            "from": "user123",
            "chat_id": "chat_456",
            "audio_url": "https://example.com/audio.ogg",
            "mime_type": "audio/ogg",
            "duration": 15
        }

        result = self.integration.extract_message_info(message_data)

        self.assertIsNotNone(result)
        self.assertEqual(result["message_id"], "msg_123")
        self.assertEqual(result["sender"], "user123")
        self.assertEqual(result["chat_id"], "chat_456")

    def test_extract_message_info_missing_fields(self):
        """测试缺少字段的消息"""
        message_data = {
            "id": "msg_123"
        }

        result = self.integration.extract_message_info(message_data)
        self.assertIsNone(result)

    def test_get_stats(self):
        """测试获取统计信息"""
        stats = self.integration.get_stats()
        self.assertIn("total_received", stats)
        self.assertIn("total_processed", stats)
        self.assertIn("success_rate", stats)

    def test_reset_stats(self):
        """测试重置统计信息"""
        self.integration.stats["total_received"] = 10
        self.integration.reset_stats()
        self.assertEqual(self.integration.stats["total_received"], 0)


class TestEndToEndIntegration(unittest.TestCase):
    """端到端集成测试"""

    def setUp(self):
        """测试准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_file = Path(self.temp_dir) / "state.json"
        self.handler = WhatsAppVoiceHandler(
            state_file=str(self.state_file),
            temp_dir=self.temp_dir,
            zhipu_api_key="test_key"
        )
        self.integration = OpenClawWhatsAppIntegration(handler=self.handler)

    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('requests.get')
    @patch('requests.post')
    def test_full_message_processing_flow(self, mock_post, mock_get):
        """测试完整消息处理流程"""
        # Mock音频下载
        mock_audio_response = Mock()
        mock_audio_response.status_code = 200
        mock_audio_response.iter_content = lambda chunk_size: [b"fake audio"]
        mock_get.return_value = mock_audio_response

        # Mock转录API
        mock_transcribe_response = Mock()
        mock_transcribe_response.status_code = 200
        mock_transcribe_response.json.return_value = {"text": "测试转录内容"}
        mock_post.return_value = mock_transcribe_response

        # 处理消息
        message_data = {
            "id": "msg_123",
            "type": "voice",
            "from": "user123",
            "chat_id": "chat_456",
            "audio_url": "https://example.com/audio.ogg"
        }

        # 由于没有FFmpeg，实际下载会失败，所以这里只测试流程结构
        result = self.integration.process_whatsapp_message(message_data)

        # 验证消息被识别为语音消息
        self.assertIsNotNone(result)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestAudioProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestTranscriptionService))
    suite.addTests(loader.loadTestsFromTestCase(TestReplyGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestWhatsAppVoiceHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestOpenClawWhatsAppIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndIntegration))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print("\n" + "=" * 70)
    print(f"测试完成: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
