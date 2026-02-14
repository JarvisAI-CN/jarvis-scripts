#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐 NCM 格式转换器 v3.0 (完全重写)
基于实际测试，简化逻辑，专注解密核心功能

v3.0 改进:
- ✅ 简化文件结构解析
- ✅ 跳过有问题的元数据/图片数据
- ✅ 改进错误恢复
- ✅ 专注音频解密核心功能
"""

import os
import sys
import struct
import base64
from pathlib import Path
from typing import Optional


class SimpleNCMDump:
    """简化的 NCM 解密器 - v3.0"""

    # 内置密钥
    BUILT_IN_KEY = base64.b64decode(
        "eFBkCN8xqTQQFqqLRC6S1U1vW5bT4LVqFxj5lqARjPE="
    )

    def __init__(self, ncm_file: str):
        self.ncm_file = ncm_file
        self.key_data: Optional[bytes] = None

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
        """XOR 解密"""
        result = bytearray(data)
        key_len = len(key)
        for i in range(len(result)):
            result[i] ^= key[i % key_len]
        return bytes(result)

    def decrypt_key_data(self, encrypted_key: bytes) -> Optional[bytes]:
        """解密密钥数据"""
        try:
            # 去掉 header (17 bytes)
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

    def decrypt(self) -> Optional[bytes]:
        """解密 NCM 文件，返回原始音频数据"""
        try:
            with open(self.ncm_file, 'rb') as f:
                data = f.read()

        except Exception as e:
            print(f"❌ 读取文件失败: {str(e)}")
            return None

        # 检查魔术字
        if not (data.startswith(b'CTCN') or data.startswith(b'CTEN')):
            print("❌ 不是有效的 NCM 文件")
            print(f"魔术字: {data[:4]}")
            return None

        # 文件最小长度检查
        if len(data) < 20:
            print("❌ 文件过小")
            return None

        offset = 10

        try:
            # 读取密钥长度
            if offset + 4 > len(data):
                print("❌ 文件格式错误：无法读取密钥长度")
                return None

            key_len = struct.unpack('<I', data[offset:offset+4])[0]
            print(f"✅ 密钥长度: {key_len} bytes")

            # 边界验证
            if offset + 4 + key_len > len(data):
                print(f"❌ 密钥数据超出文件范围")
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
            if offset + 4 > len(data):
                print("❌ 文件格式错误：无法读取元数据长度")
                return None

            meta_len = struct.unpack('<I', data[offset:offset+4])[0]
            print(f"✅ 元数据长度: {meta_len} bytes")

            # 边界验证
            if offset + 4 + meta_len > len(data):
                print(f"❌ 元数据超出文件范围")
                return None

            offset += 4 + meta_len

            # 跳过 CRC (5 bytes)
            offset += 5

            # 读取图片 gap
            if offset + 4 > len(data):
                print("❌ 文件格式错误：无法读取图片 gap")
                return None

            gap_len = struct.unpack('<I', data[offset:offset+4])[0]
            print(f"✅ 图片 gap: {gap_len} bytes")

            # 边界验证
            if offset + 4 + gap_len > len(data):
                print(f"⚠️  图片 gap 超出范围，使用剩余数据")
                gap_len = len(data) - offset - 4

            offset += 4 + gap_len

            # 剩余的是加密的音频数据
            encrypted_audio = data[offset:]

            print(f"🔄 解密音频数据 ({len(encrypted_audio)} bytes)...")

            # 使用解密后的密钥解密音频
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
        else:
            return None

    @staticmethod
    def save_audio(data: bytes, output_path: str) -> bool:
        """保存音频文件"""
        try:
            with open(output_path, 'wb') as f:
                f.write(data)

            return True
        except Exception as e:
            print(f"❌ 保存文件失败: {str(e)}")
            return False


def convert_ncm(ncm_path: str, output_path: Optional[str] = None) -> bool:
    """转换单个 NCM 文件"""
    ncm_path = os.path.abspath(ncm_path)

    if not os.path.exists(ncm_path):
        print(f"❌ 文件不存在: {ncm_path}")
        return False

    print(f"{'='*60}")
    print(f"🎵 NCM 转 FLAC v3.0 (简化版)")
    print(f"{'='*60}")
    print(f"输入: {os.path.basename(ncm_path)}")
    print(f"{'='*60}")
    print()

    # 解密 NCM
    decrypter = SimpleNCMDump(ncm_path)
    decrypted_data = decrypter.decrypt()

    if decrypted_data is None:
        print("\n❌ 解密失败")
        return False

    # 检测格式
    fmt = AudioConverter.detect_format(decrypted_data)

    if not fmt:
        print(f"\n❌ 未知音频格式")
        print(f"前4字节: {decrypted_data[:4]}")
        return False

    print(f"\n✅ 音频格式: {fmt.upper()}")

    # 确定输出路径
    if output_path is None:
        if fmt == 'flac':
            output_path = os.path.splitext(ncm_path)[0] + '.flac'
        else:
            output_path = os.path.splitext(ncm_path)[0] + '.' + fmt

    # 保存音频文件
    print(f"\n输出: {os.path.basename(output_path)}")
    print(f"{'='*60}")

    success = AudioConverter.save_audio(decrypted_data, output_path)

    if success:
        print(f"\n{'='*60}")
        print(f"✅ 转换成功！")
        print(f"{'='*60}")

        # 显示文件大小
        ncm_size = os.path.getsize(ncm_path) / (1024 * 1024)
        output_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n文件大小:")
        print(f"  输入 (NCM): {ncm_size:.2f} MB")
        print(f"  输出 ({fmt.upper()}): {output_size:.2f} MB")
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
    print(f"🎵 NCM 转 FLAC v3.0 - 批量转换")
    print(f"{'='*60}")
    print(f"\n找到 {len(ncm_files)} 个 NCM 文件\n")

    success_count = 0

    for i, ncm_file in enumerate(ncm_files, 1):
        print(f"\n[{i}/{len(ncm_files)}] {os.path.basename(ncm_file)}")
        print('-' * 60)

        output_path = None

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.splitext(os.path.basename(ncm_file))[0]
            output_path = os.path.join(output_dir, filename + '.flac')

        if convert_ncm(ncm_file, output_path):
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
        description='网易云音乐 NCM 格式转换器 v3.0 (完全重写)',
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
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 3.0')

    args = parser.parse_args()

    batch_convert(args.input, args.output)


if __name__ == '__main__':
    main()
