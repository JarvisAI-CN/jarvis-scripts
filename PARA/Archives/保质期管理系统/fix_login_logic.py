#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def main():
    # 读取合并后的文件
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_full.php', 'r', encoding='utf-8') as f:
        content = f.read()

    # 找到pastView结束后，modal开始前的位置
    pattern = re.compile(
        r'''
        <div\s+id="pastView".*?</div>
        \s*
        <div\s+class="modal\s+fade".*?id="entryModal"
        ''',
        re.DOTALL
    )

    match = pattern.search(content)
    if not match:
        raise ValueError("未找到pastView到entryModal的结构")

    print(f"找到了匹配的模式，位置: {match.start()} - {match.end()}")

    # 在pastView结束后添加<?php endif; ?>
    replacement = '''
        </div>
        <?php endif; ?>
    <div class="modal fade" id="entryModal"
    '''

    fixed_content = pattern.sub(replacement, content)

    # 保存修改后的文件
    output_path = '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_fixed.php'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"✅ 登录逻辑修复完成，文件已保存为: {output_path}")

    # 检查PHP语法
    import subprocess
    try:
        result = subprocess.run(['php', '-l', output_path], capture_output=True, text=True)
        if 'No syntax errors' in result.stdout:
            print("✅ PHP语法检查通过")
        else:
            print(f"❌ PHP语法检查失败: {result.stdout}")
    except FileNotFoundError:
        print("⚠️ 未找到php命令，跳过语法检查")

if __name__ == "__main__":
    main()
