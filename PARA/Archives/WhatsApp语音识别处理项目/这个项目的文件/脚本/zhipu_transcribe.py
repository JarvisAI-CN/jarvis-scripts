#!/usr/bin/env python3
"""
使用智谱 AI (Zhipu) API 转录音频文件
"""

import os
import sys
import requests

def transcribe_audio(audio_file_path):
    # 智谱 API 密钥（从 PASSWORDS.md 中获取的）
    api_key = "9e65ece2efa781c15ecf344f62a8cf01.7BKc7Gj88ePbY74W"
    url = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"
    
    if not os.path.exists(audio_file_path):
        print(f"❌ 文件不存在: {audio_file_path}")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    files = {
        "file": open(audio_file_path, "rb")
    }
    
    data = {
        "model": "sensevoice"
    }

    try:
        print(f"🎙️ 正在向智谱发送转录请求: {os.path.basename(audio_file_path)}...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            text = result.get("text", "")
            print(f"✅ 转录成功！内容: {text}")
            return text
        else:
            print(f"❌ 转录失败 (HTTP {response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return None
    finally:
        files["file"].close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 zhipu_transcribe.py <音频文件路径>")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    transcribe_audio(audio_path)
