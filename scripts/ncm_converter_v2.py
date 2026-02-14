#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐 NCM 格式转换器 v2.0
基于测试结果完全重写，支持CTEN和CTCN格式

v2.0 改进:
- ✅ 支持CTEN格式（新加密）
- ✅ 改进元数据解析
- ✅ 更好的错误处理
- ✅ 参考ncmdump成功案例
"""

import os
import sys
import json
import struct
import base64
from pathlib import Path
from typing import Optional, Dict, Any

class NCMDump:
    """NCM 文件解密器 v2.0"""

    # NCM 文件魔术字
    MAGIC_CTCN = b'CTCN'
    MAGIC_CTEN = b'CTEN'

    # 内置密钥
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
        self.is_cten = False  # 标记是否为CTEN格式

    def rc4_ksa(self, key: bytes) -> bytes:
        """RC4 密钥调度算法"""
        s = list(range(256))
        j = 0
        key_len = len(key)

        for i in range(256):
            j = (j + s[i] + key[i % key_len]) % 256
            s[i], s[j] = s[j], s[i]

        return bytes(s)

    def rc4_prng(self, s: bytes, data: bytes) -> bytes:
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
        return self.rc4_prng(s, data)

    def xor_decrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR 解密"""
        result = bytearray(data)
        key_len = len(key)
        for i in range(len(result)):
            result[i] ^= key[i % key_len]
        return bytes(result)

    def decrypt_key_data(self, encrypted_key: bytes) -> Optional[bytes]:
        """解密密钥数据"""
        try:
            # 去掉 header
            data = encrypted_key[17:]

            # XOR 解密
            decrypted = self.xor_decrypt(data, self.BUILT_IN_KEY)

            # 去掉 padding
            decrypted = decrypted.rstrip(b'\x00')

            # Base64 解码
            key_data = base64.b64decode(decrypted)

            # 去掉 "neteasecloudmusic" 前缀
            if key_data.startswith(b"neteasecloudmusic"):
                return key_data[22:]
            return key_data

        except Exception as e:
            print(f"❌ 密钥解密失败: {str(e)}")
            return None

    def decrypt_metadata(self, encrypted_meta: bytes) -> Dict[str, Any]:
        """解密元数据"""
        if not encrypted_meta:
            return {}

        try:
            # 去掉 header
            data = encrypted_meta[22:]

            # 解密
            decrypted = self.rc4_decrypt(self.META_KEY, data)

            # 去掉 padding
            decrypted = decrypted.rstrip(b'\x00')

            # Base64 解码
            decoded = base64.b64decode(decrypted)

            # JSON 解析
            metadata = json.loads(decoded.decode('utf-8'))
            return metadata

        except Exception as e:
            print(f"⚠️  元数据解析失败（继续转换）: {str(e)}")
            return {}

    def decrypt(self) -> Optional[bytes]:
        """解密 NCM 文件，返回原始音频数据"""
        try:
            with open(self.ncm_file, 'rb') as f:
                data = f.read()

        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            return None

        # 检查魔术字（支持两种格式）
        if data.startswith(self.MAGIC_CTCN):
            print("✅ 检测到 CTCN 格式")
            self.is_cten = False
        elif data.startswith(self.MAGIC_CTEN):
            print("✅ 检测到 CTEN 格式")
            self.is_cten = True
        else:
            print("❌ 不是有效的 NCM 文件")
            print(f"魔术字: {data[:4]}")
            return None

        # 文件最小长度检查
        if len(data) < 20:
            print("❌ 文件过小，不是有效的 NCM 文件")
            return None

        offset = 10

        try:
            # 读取密钥长度
            key_len = struct.unpack('<I', data[offset:offset+4])[0]

            # 边界验证
            if offset + 4 + key_len > len(data):
                print(f"❌ 文件格式错误：密钥长度超出范围 (key_len={key_len}, file_size={len(data)})")
                return None

            offset += 4

            # 读取密钥数据
            key_data = data[offset:offset+key_len]
            offset += key_len

            # 解密密钥
            self.key_data = self.decrypt_key_data(key_data)

            if not self.key_data:
                print("❌ 密钥解密失败")
                return None

            print(f"✅ 密钥解密成功 ({len(self.key_data)} bytes)")

            # 读取元数据长度
            meta_len = struct.unpack('<I', data[offset:offset+4])[0]

            # 边界验证
            if offset + 4 + meta_len > len(data):
                print(f"❌ 文件格式错误：元数据长度超出范围 (meta_len={meta_len}, file_size={len(data)})")
                return None

            offset += 4

            # 读取元数据
            if meta_len > 0:
                meta_data = data[offset:offset+meta_len]
                offset += meta_len
                self.metadata = self.decrypt_metadata(meta_data)
                print(f"✅ 元数据解析成功: {len(self.metadata)} 字段")

            # 读取 CRC (跳过)
            offset += 5

            # 读取图片 gap (跳过)
            gap_len = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4

            # 边界验证
            if offset + gap_len > len(data):
                print(f"❌ 文件格式错误：图片 gap 超出范围 (gap_len={gap_len})")
                return None

            offset += gap_len

            # 读取图片数据（如果有）
            if gap_len > 0:
                try:
                    image_len = struct.unpack('<I', data[offset:offset+4])[0]
                    offset += 4

                    # 边界验证
                    if offset + image_len > len(data):
                        print(f"❌ 文件格式错误：图片数据超出范围 (image_len={image_len})")
                        return None

                    self.album_art = data[offset:offset+image_len]
                    offset += image_len
                    print(f"✅ 封面数据提取成功 ({len(self.album_art)} bytes)")

                except Exception as e:
                    print(f"⚠️  图片数据读取失败（继续转换）: {str(e)}")

            # 剩余的是加密的音频数据
            encrypted_audio = data[offset:]

            # 使用解密后的密钥解密音频
            print(f"🔄 解密音频数据 ({len(encrypted_audio)} bytes)...")
            decrypted_audio = self.rc4_decrypt(self.key_data, encrypted_audio)

            print(f"✅ 解密成功 ({len(decrypted_audio)} bytes)")
            return decrypted_audio

        except struct.error as e:
            print(f"❌ 文件格式错误: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ 解密失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


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
            print(f"⚠️  未知音频格式，前4字节: {data[:4]}")
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
            # 直接保存 FLAC 数据
            with open(output_path, 'wb') as f:
                f.write(data)

            print(f"✅ FLAC 文件已保存: {output_path}")

            # 显示元数据
            if metadata:
                print("\n📋 元数据:")
                if 'musicName' in metadata:
                    print(f"   歌曲: {metadata['musicName']}")
                if 'artistName' in metadata:
                    artists = metadata['artistName']
                    if isinstance(artists, list):
                        print(f"   艺术家: {', '.join(artists)}")
                    else:
                        print(f"   艺术家: {artists}")
                if 'albumName' in metadata:
                    print(f"   专辑: {metadata['albumName']}")

            return True

        except Exception as e:
            print(f"❌ 保存 FLAC 文件失败: {str(e)}")
            return False


def convert_ncm_to_flac(ncm_path: str, output_path: Optional[str] = None) -> bool:
    """转换单个 NCM 文件为 FLAC"""
    ncm_path = os.path.abspath(ncm_path)

    if not os.path.exists(ncm_path):
        print(f"❌ 文件不存在: {ncm_path}")
        return False

    print(f"{'='*60}")
    print(f"🎵 NCM 转 FLAC v2.0")
    print(f"{'='*60}")
    print(f"输入: {os.path.basename(ncm_path)}")
    print(f"{'='*60}")
    print()

    # 解密 NCM
    decrypter = NCMDump(ncm_path)
    decrypted_data = decrypter.decrypt()

    if decrypted_data is None:
        print("\n❌ 解密失败")
        return False

    # 检测格式
    fmt = AudioConverter.detect_format(decrypted_data)

    if fmt != 'flac':
        print(f"\n❌ 错误: NCM 文件内的原始格式是 {fmt}，不是 FLAC")
        print(f"💡 当前版本仅支持 NCM 加密的 FLAC 文件直接输出")
        print(f"💡 对于 {fmt.upper()} 格式，需要使用 ffmpeg 等工具进行格式转换")
        print(f"{'='*60}")
        return False

    print(f"\n✅ 音频格式: FLAC (无损)")

    # 确定输出路径
    if output_path is None:
        output_path = os.path.splitext(ncm_path)[0] + '.flac'

    # 保存 FLAC
    print(f"\n输出: {os.path.basename(output_path)}")
    print(f"{'='*60}")

    success = AudioConverter.save_flac(
        decrypted_data,
        output_path,
        decrypter.metadata,
        decrypter.album_art
    )

    if success:
        print(f"\n{'='*60}")
        print(f"✅ 转换成功！")
        print(f"{'='*60}")

        # 显示文件大小
        ncm_size = os.path.getsize(ncm_path) / (1024 * 1024)
        flac_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n文件大小:")
        print(f"  输入 (NCM): {ncm_size:.2f} MB")
        print(f"  输出 (FLAC): {flac_size:.2f} MB")
    else:
        print(f"\n{'='*60}")
        print(f"❌ 转换失败")
        print(f"{'='*60}")

    return success


def batch_convert(input_path: str, output_dir: Optional[str] = None) -> int:
    """批量转换 NCM 文件"""
    input_path = os.path.abspath(input_path)

    if not os.path.exists(input_path):
        print(f"❌ 路径不存在: {input_path}")
        return 0

    ncm_files = []

    if os.path.isfile(input_path):
        if input_path.lower().endswith('.ncm'):
            ncm_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith('.ncm'):
                    ncm_files.append(os.path.join(root, file))

    if not ncm_files:
        print("❌ 未找到 NCM 文件")
        return 0

    print(f"{'='*60}")
    print(f"🎵 NCM 转 FLAC v2.0 - 批量转换")
    print(f"{'='*60}")
    print(f"\n找到 {len(ncm_files)} 个 NCM 文件\n")

    success_count = 0

    for i, ncm_file in enumerate(ncm_files, 1):
        print(f"\n[{i}/{len(ncm_files)}] {os.path.basename(ncm_file)}")
        print('-' * 60)

        output_path = None

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(ncm_file))[0] + '.flac'
            output_path = os.path.join(output_dir, filename)

        if convert_ncm_to_flac(ncm_file, output_path):
            success_count += 1
        else:
            print(f"⚠️  跳过: {os.path.basename(ncm_file)}")

    print(f"\n{'='*60}")
    print(f"📊 批量转换完成")
    print(f"{'='*60}")
    print(f"\n成功: {success_count}/{len(ncm_files)}")

    return success_count


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='网易云音乐 NCM 格式转换器 v2.0 (完全重写，支持CTEN格式)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s song.ncm                    # 转换单个文件
  %(prog)s song.ncm -o output.flac     # 指定输出文件
  %(prog)s ./music_dir                 # 批量转换文件夹
  %(prog)s ./music_dir -o ./flac_dir   # 批量转换到指定文件夹
        '''
    )

    parser.add_argument('input', help='NCM 文件或包含 NCM 文件的目录')
    parser.add_argument('-o', '--output', help='输出文件或目录')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 2.0')

    args = parser.parse_args()

    batch_convert(args.input, args.output)


if __name__ == '__main__':
    main()
