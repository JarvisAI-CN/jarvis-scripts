#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 index_v2.14.2_working.php 文件末尾的语法错误
"""

def main():
    file_path = '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_working.php'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找是否有未闭合的函数或if语句
    # 统计大括号的数量
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    print(f"大括号统计: {open_braces} 个打开, {close_braces} 个关闭")
    
    if open_braces != close_braces:
        print(f"发现语法错误: 大括号不匹配，相差 {abs(open_braces - close_braces)} 个")
        
        # 需要添加缺失的闭合括号
        missing = open_braces - close_braces
        if missing > 0:
            print(f"需要添加 {missing} 个闭合括号")
            
            # 在文件末尾添加缺失的闭合括号
            content += '}' * missing
    
    # 检查generateInventoryTable函数是否正确闭合
    if 'generateInventoryTable' in content and not content.endswith('}'):
        print("generateInventoryTable函数可能未闭合")
    
    # 保存修复后的文件
    output_path = '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_working_fixed.php'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复完成，保存到: {output_path}")
    
    # 检查PHP语法
    import subprocess
    try:
        result = subprocess.run(['php', '-l', output_path], capture_output=True, text=True)
        if 'No syntax errors' in result.stdout:
            print("✅ PHP语法检查通过")
        else:
            print(f"❌ PHP语法检查失败: {result.stdout}")
    except FileNotFoundError:
        print("⚠️ 未找到php命令")

if __name__ == "__main__":
    main()
