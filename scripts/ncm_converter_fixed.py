#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐 NCM 格式转换器（修复版）
支持将 NCM 格式转换为 FLAC 格式，保留元数据

修复：
- 支持 CTEN 和 CTCN 两种魔术字
- 修复文件名编码问题
- 改进错误处理
"""

import os
import json
import struct
import base64
from pathlib import Path
from typing import Optional, Dict, Any

class NCMDecrypter:
    """NCM 文件解密器"""

    # NCM 文件魔术字（支持两种格式）
    MAGIC_CTCN = b'CTCN'
    MAGIC_CTEN = b'CTEN'

    # 内置密钥（用于解密 NCM 的密钥数据）
    BUILT_IN_KEY = base64.b64decode(
        "eFBkCN8xqTQQFqqLRC6S1U1vW5bT4LVqFxj5lqARjPE="
    )

    # RC4 盒生成的标准密钥
    CORE_KEY = b"\x68\x7A\x48\x52\x41\x6D\x73\x6F\x35\x6B\x49\x6E\x62\x61\x78\x57"
    META_KEY = b"\x23\x31\x34\x6C\x6A\x6B\x5F\x21\x5C\x5D\x26\x30\x55\x3C\x27\x28"

    def __init__(self, ncm_file: str):
        self.ncm_file = ncm_file
        self.metadata: Dict[str, Any] = {}
        self.album_art: Optional[bytes] = None
        self.key_data: Optional[bytes] = None
        self.is_cten_format = False  # 标记是否为CTEN格式

    def rc4_ksa(self, key: bytes) -> bytes:
        """RC4 密钥调度算法"""
        s = list(range(256))
        j = 0
        key_len = len(key)

        for i in range(256):
            j = (j + s[i] + key[i % key_len]) % 256
            s[i], s[j] = s[j], s[i]

        return bytes(s)

    def rc4_prga(self, s: bytes, data: bytes) -> bytes:
        """RC4 伪随机生成算法"""
        s_box = list(s)
        i = j = 0
        result = bytearray(data)

        for k in range(len(result)):
            i = (i + 1) % 256
            j = (j + s_box[i]) % 256
            s_box[i], s_box[j] = s_box[j], s_box[i]
            result[k] ^= s_box[(s_box[i] + s_box[j]) % 256]

        return bytes(result)

    def rc4_decrypt(self, key: bytes, data: bytes) -> bytes:
        """RC4 解密"""
        s = self.rc4_ksa(key)
        return self.rc4_prga(s, data)

    def xor_decrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR 解密（用于密钥数据）"""
        result = bytearray(data)
        key_len = len(key)
        for i in range(len(result)):
            result[i] ^= key[i % key_len]
        return bytes(result)

    def decrypt_key_data(self, encrypted_key: bytes) -> Optional[bytes]:
        """解密密钥数据"""
        # 去掉 header
        data = encrypted_key[17:]

        # XOR 解密
        decrypted = self.xor_decrypt(data, self.BUILT_IN_KEY)

        # 去掉 padding
        decrypted = decrypted.rstrip(b'\x00')

        # Base64 解码
        try:
            key_data = base64.b64decode(decrypted)
            # 去掉 "neteasecloudmusic" 前缀
            if key_data.startswith(b"neteasecloudmusic"):
                return key_data[22:]
            return key_data
        except (base64.binascii.Error, ValueError) as e:
            print(f"Base64 解码失败: {e}")
            return None

    def decrypt_metadata(self, encrypted_meta: bytes) -> Dict[str, Any]:
        """解密元数据"""
        if not encrypted_meta:
            return {}

        # 去掉 header
        data = encrypted_meta[22:]

        # 解密
        decrypted = self.rc4_decrypt(self.META_KEY, data)

        # 去掉 padding
        decrypted = decrypted.rstrip(b'\x00')

        # Base64 解码
        try:
            decoded = base64.b64decode(decrypted)
            # JSON 解析
            return json.loads(decoded.decode('utf-8'))
        except (base64.binascii.Error, ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"元数据解析失败: {e}")
            return {}

    def extract_album_art(self) -> Optional[bytes]:
        """从元数据中提取封面"""
        if 'albumPic' in self.metadata:
            pic_url = self.metadata['albumPic']
            # 这里只保存URL，实际下载需要网络请求
            # 可以考虑添加图片下载功能
            pass
        return None

    def decrypt(self) -> Optional[bytes]:
        """解密 NCM 文件，返回原始音频数据"""
        try:
            with open(self.ncm_file, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"读取文件失败: {e}")
            return None

        # 检查魔术字（支持两种格式）
        if data.startswith(self.MAGIC_CTCN):
            print("检测到 CTCN 格式")
            self.is_cten_format = False
        elif data.startswith(self.MAGIC_CTEN):
            print("检测到 CTEN 格式")
            self.is_cten_format = True
        else:
            print("不是有效的 NCM 文件")
            return None

        # 文件最小长度检查
        if len(data) < 20:
            print("文件过小，不是有效的 NCM 文件")
            return None

        offset = 10

        # 读取密钥长度（增加异常捕获）
        try:
            if offset + 4 > len(data):
                print("文件格式错误：无法读取密钥长度")
                return None
            key_len = struct.unpack('<I', data[offset:offset+4])[0]
        except struct.error as e:
            print(f"读取密钥长度失败: {e}")
            return None

        # 边界验证
        if offset + 4 + key_len > len(data):
            print(f"文件格式错误：密钥长度超出文件范围 (key_len={key_len}, file_size={len(data)})")
            return None

        offset += 4

        # 读取密钥数据
        key_data = data[offset:offset+key_len]
        offset += key_len

        # 解密密钥
        self.key_data = self.decrypt_key_data(key_data)

        if not self.key_data:
            print("密钥解密失败")
            return None

        # 读取元数据长度（增加异常捕获）
        try:
            if offset + 4 > len(data):
                print("文件格式错误：无法读取元数据长度")
                return None
            meta_len = struct.unpack('<I', data[offset:offset+4])[0]
        except struct.error as e:
            print(f"读取元数据长度失败: {e}")
            return None

        # 边界验证
        if offset + 4 + meta_len > len(data):
            print(f"文件格式错误：元数据长度超出文件范围 (meta_len={meta_len}, file_size={len(data)})")
            return None

        offset += 4

        # 读取元数据
        if meta_len > 0:
            meta_data = data[offset:offset+meta_len]
            offset += meta_len
            self.metadata = self.decrypt_metadata(meta_data)

        # 读取 CRC (跳过)
        if offset + 5 > len(data):
            print("文件格式错误：无法读取 CRC")
            return None
        offset += 5

        # 读取图片 gap (跳过，增加异常捕获)
        try:
            if offset + 4 > len(data):
                print("文件格式错误：无法读取图片 gap 长度")
                return None
            gap_len = struct.unpack('<I', data[offset:offset+4])[0]
        except struct.error as e:
            print(f"读取图片 gap 长度失败: {e}")
            return None

        offset += 4

        # 边界验证
        if offset + gap_len > len(data):
            print(f"文件格式错误：图片 gap 超出文件范围 (gap_len={gap_len})")
            return None

        offset += gap_len

        # 读取图片数据
        if gap_len > 0:
            try:
                if offset + 4 > len(data):
                    print("文件格式错误：无法读取图片长度")
                    return None
                image_len = struct.unpack('<I', data[offset:offset+4])[0]
                offset += 4

                # 边界验证
                if offset + image_len > len(data):
                    print(f"文件格式错误：图片数据超出文件范围 (image_len={image_len})")
                    return None

                self.album_art = data[offset:offset+image_len]
                offset += image_len
            except struct.error as e:
                print(f"读取图片数据失败: {e}")
                return None

        # 剩余的是加密的音频数据
        encrypted_audio = data[offset:]

        # 使用解密后的密钥解密音频
        decrypted_audio = self.rc4_decrypt(self.key_data, encrypted_audio)

        return decrypted_audio


class AudioConverter:
    """音频格式转换器"""

    @staticmethod
    def detect_format(data: bytes) -> Optional[str]:
        """检测音频格式"""
        if data.startswith(b'ID3') or data.startswith(b'\xFF\xFB') or data.startswith(b'\xFF\xFA'):
            return 'mp3'
        elif data.startswith(b'fLaC'):
            return 'flac'
        elif data.startswith(b'OggS'):
            return 'ogg'
        elif data.startswith(b'\xFF\xF1') or data.startswith(b'\xFF\xF9'):
            return 'aac'
        else:
            return None

    @staticmethod
    def is_flac(data: bytes) -> bool:
        """检查是否已经是 FLAC 格式"""
        return data.startswith(b'fLaC')

    @staticmethod
    def save_flac(data: bytes, output_path: str, metadata: Dict[str, Any] = None,
                  album_art: Optional[bytes] = None) -> bool:
        """保存为 FLAC 文件"""
        try:
            # 检查是否已经是 FLAC
            if not data.startswith(b'fLaC'):
                print("警告: 解密后的数据不是 FLAC 格式，可能需要转换")
                print(f"实际格式: {AudioConverter.detect_format(data)}")
                print("提示: 本脚本仅处理 NCM 加密的 FLAC 文件，对于 MP3 等格式需要额外转换")
                return False

            # 直接保存 FLAC 数据
            with open(output_path, 'wb') as f:
                f.write(data)

            # 如果有元数据，可以考虑使用 mutagen 添加
            # 这需要安装: pip install mutagen
            try:
                from mutagen.flac import FLAC
                audio = FLAC(output_path)

                if metadata:
                    if 'musicName' in metadata:
                        audio['TITLE'] = metadata['musicName']
                    if 'albumName' in metadata:
                        audio['ALBUM'] = metadata['albumName']
                    if 'artistName' in metadata:
                        artists = metadata['artistName']
                        if isinstance(artists, list):
                            audio['ARTIST'] = ', '.join(artists)
                        else:
                            audio['ARTIST'] = artists
                    if 'albumPic' in metadata:
                        # 这里可以保存图片URL到注释
                        audio['COMMENT'] = f"Cover: {metadata['albumPic']}"

                if album_art:
                    audio.add_picture(album_art)

                audio.save()
                print(f"已添加元数据到 FLAC 文件")
            except ImportError:
                print("未安装 mutagen 库，元数据未添加")
                print("安装命令: pip install mutagen")
            except Exception as e:
                print(f"添加元数据失败: {e}")

            return True
        except Exception as e:
            print(f"保存 FLAC 文件失败: {e}")
            return False


def convert_ncm_to_flac(ncm_path: str, output_path: Optional[str] = None) -> bool:
    """转换单个 NCM 文件为 FLAC"""
    ncm_path = os.path.abspath(ncm_path)

    if not os.path.exists(ncm_path):
        print(f"文件不存在: {ncm_path}")
        return False

    print(f"正在转换: {os.path.basename(ncm_path)}")

    # 解密 NCM
    decrypter = NCMDecrypter(ncm_path)
    decrypted_data = decrypter.decrypt()

    if decrypted_data is None:
        print("解密失败")
        return False

    # 检测格式
    fmt = AudioConverter.detect_format(decrypted_data)
    print(f"检测到音频格式: {fmt if fmt else '未知'}")

    if fmt != 'flac':
        print(f"警告: NCM 文件内的原始格式是 {fmt}，不是 FLAC")
        print("当前脚本仅支持 NCM 加密的 FLAC 文件直接输出")
        print("对于 MP3 等格式，需要使用 ffmpeg 音频工具进行格式转换")
        return False

    # 确定输出路径
    if output_path is None:
        output_path = os.path.splitext(ncm_path)[0] + '.flac'

    # 保存 FLAC
    success = AudioConverter.save_flac(
        decrypted_data,
        output_path,
        decrypter.metadata,
        decrypter.album_art
    )

    if success:
        print(f"转换成功: {output_path}")

        # 显示元数据
        if decrypter.metadata:
            print("\n元数据信息:")
            if 'musicName' in decrypter.metadata:
                print(f"  标题: {decrypter.metadata['musicName']}")
            if 'artistName' in decrypter.metadata:
                print(f"  艺术家: {decrypter.metadata['artistName']}")
            if 'albumName' in decrypter.metadata:
                print(f"  专辑: {decrypter.metadata['albumName']}")
    else:
        print("转换失败")

    return success


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python3 ncm_converter_fixed.py <ncm_file> [output_file]")
        print("\n示例:")
        print("  python3 ncm_converter_fixed.py song.ncm")
        print("  python3 ncm_converter_fixed.py song.ncm -o output.flac")
        sys.exit(1)

    ncm_file = sys.argv[1]
    output_file = None

    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    print("="*60)
    print("网易云音乐 NCM 格式转换器（修复版）")
    print("="*60)
    print()

    success = convert_ncm_to_flac(ncm_file, output_file)

    print()
    print("="*60)

    if success:
        print("✅ 转换成功！")
    else:
        print("❌ 转换失败")

    print("="*60)


if __name__ == "__main__":
    main()
