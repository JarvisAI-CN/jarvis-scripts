#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐 NCM 格式转换器 v3.1 (使用 ncmdump 后端）
完全重写，使用成熟的 ncmdump 工具作为后端

v3.1 改进:
- ✅ 使用 ncmdump 作为后端（稳定可靠）
- ✅ 简化逻辑，专注批量处理
- ✅ 自动检测格式（CTEN/CTCN）
- ✅ 保留文件名和元数据
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List


class NCMDumpConverter:
    """使用 ncmdump 后端的转换器"""

    def __init__(self):
        # 检查 ncmdump 是否可用
        self.ncmdump_path = self._find_ncmdump()

        if not self.ncmdump_path:
            raise RuntimeError(
                "ncmdump 未安装！\n"
                "安装命令: pip3 install --break-system-packages ncmdump"
            )

    def _find_ncmdump(self) -> Optional[str]:
        """查找 ncmdump 可执行文件"""
        # 检查系统路径
        ncmdump_path = shutil.which('ncmdump')
        if ncmdump_path:
            return ncmdump_path

        # 检查用户安装路径
        user_paths = [
            os.path.expanduser('~/.local/bin/ncmdump'),
            '/usr/local/bin/ncmdump',
        ]

        for path in user_paths:
            if os.path.exists(path):
                return path

        return None

    def convert_file(self, ncm_file: str, output_dir: Optional[str] = None) -> Optional[str]:
        """转换单个 NCM 文件"""
        ncm_file = os.path.abspath(ncm_file)

        if not os.path.exists(ncm_file):
            print(f"❌ 文件不存在: {ncm_file}")
            return None

        if not ncm_file.lower().endswith('.ncm'):
            print(f"❌ 不是 NCM 文件: {ncm_file}")
            return None

        # 确定输出目录
        if output_dir is None:
            output_dir = os.path.dirname(ncm_file)

        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        # 构建 ncmdump 命令
        cmd = [
            self.ncmdump_path,
            ncm_file,
            '-o', output_dir
        ]

        print(f"{'='*60}")
        print(f"🎵 NCM 转 FLAC v3.1 (ncmdump 后端)")
        print(f"{'='*60}")
        print(f"输入: {os.path.basename(ncm_file)}")
        print(f"输出目录: {output_dir}")
        print(f"{'='*60}")
        print()

        try:
            # 执行转换
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode == 0:
                # 查找输出文件
                ncm_name = os.path.splitext(os.path.basename(ncm_file))[0]

                # 可能的输出文件格式
                possible_outputs = [
                    os.path.join(output_dir, ncm_name + '.flac'),
                    os.path.join(output_dir, ncm_name + '.mp3'),
                    os.path.join(output_dir, ncm_name + '.ogg'),
                ]

                output_file = None
                for path in possible_outputs:
                    if os.path.exists(path):
                        output_file = path
                        break

                if output_file:
                    # 获取文件信息
                    ncm_size = os.path.getsize(ncm_file) / (1024 * 1024)
                    output_size = os.path.getsize(output_file) / (1024 * 1024)
                    fmt = os.path.splitext(output_file)[1][1:].upper()

                    print(f"✅ 转换成功")
                    print(f"{'='*60}")
                    print(f"\n输出文件: {os.path.basename(output_file)}")
                    print(f"格式: {fmt}")
                    print(f"\n文件大小:")
                    print(f"  输入 (NCM): {ncm_size:.2f} MB")
                    print(f"  输出 ({fmt}): {output_size:.2f} MB")

                    return output_file
                else:
                    print(f"❌ 未找到输出文件")
                    print(f"输出目录内容: {os.listdir(output_dir)}")
                    return None
            else:
                print(f"❌ ncmdump 执行失败")
                print(f"错误: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"❌ 转换超时 (5分钟)")
            return None
        except Exception as e:
            print(f"❌ 转换失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def batch_convert(
        self,
        input_path: str,
        output_dir: Optional[str] = None,
        recursive: bool = False
    ) -> List[str]:
        """批量转换 NCM 文件"""
        input_path = os.path.abspath(input_path)

        if not os.path.exists(input_path):
            print(f"❌ 路径不存在: {input_path}")
            return []

        # 收集 NCM 文件
        ncm_files = []

        if os.path.isfile(input_path):
            if input_path.lower().endswith('.ncm'):
                ncm_files.append(input_path)
        elif os.path.isdir(input_path):
            if recursive:
                # 递归搜索
                for root, dirs, files in os.walk(input_path):
                    for file in files:
                        if file.lower().endswith('.ncm'):
                            ncm_files.append(os.path.join(root, file))
            else:
                # 只搜索当前目录
                for file in os.listdir(input_path):
                    if file.lower().endswith('.ncm'):
                        ncm_files.append(os.path.join(input_path, file))

        if not ncm_files:
            print("❌ 未找到 NCM 文件")
            return []

        print(f"{'='*60}")
        print(f"🎵 NCM 转 FLAC v3.1 - 批量转换")
        print(f"{'='*60}")
        print(f"\n找到 {len(ncm_files)} 个 NCM 文件\n")

        success_files = []

        for i, ncm_file in enumerate(ncm_files, 1):
            print(f"\n[{i}/{len(ncm_files)}] {os.path.basename(ncm_file)}")
            print('-' * 60)

            output_file = self.convert_file(ncm_file, output_dir)

            if output_file:
                success_files.append(output_file)
            else:
                print(f"⚠️  跳过: {os.path.basename(ncm_file)}")

        print(f"\n{'='*60}")
        print(f"📊 批量转换完成")
        print(f"{'='*60}")
        print(f"\n成功: {len(success_files)}/{len(ncm_files)}")

        return success_files


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='网易云音乐 NCM 格式转换器 v3.1 (ncmdump 后端)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s song.ncm                    # 转换单个文件
  %(prog)s song.ncm -o ./flac/         # 转换到指定目录
  %(prog)s ./music_dir                 # 批量转换文件夹
  %(prog)s ./music_dir -o ./flac_dir -r # 递归批量转换
        '''
    )

    parser.add_argument('input', help='NCM 文件或目录')
    parser.add_argument('-o', '--output', help='输出目录')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='递归搜索子目录')

    args = parser.parse_args()

    try:
        converter = NCMDumpConverter()

        if os.path.isfile(args.input):
            # 单个文件转换
            output_file = converter.convert_file(args.input, args.output)

            if output_file:
                print(f"\n✅ 转换成功: {output_file}")
                sys.exit(0)
            else:
                print(f"\n❌ 转换失败")
                sys.exit(1)
        else:
            # 批量转换
            success_files = converter.batch_convert(
                args.input,
                args.output,
                args.recursive
            )

            if success_files:
                print(f"\n✅ 成功转换 {len(success_files)} 个文件")
                sys.exit(0)
            else:
                print(f"\n❌ 没有文件被转换")
                sys.exit(1)

    except RuntimeError as e:
        print(f"❌ {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n⚠️  用户中断")
        sys.exit(130)


if __name__ == '__main__':
    main()
