#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import re

def main():
    # 读取78KB文件（包含编辑和AI分析功能）
    with open('/tmp/index_current_v2.14.2.php', 'r', encoding='utf-8') as f:
        file1_content = f.read()

    # 读取当前工作文件
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'r', encoding='utf-8') as f:
        file2_content = f.read()

    # 从78KB文件中提取编辑盘点单和AI分析功能的JavaScript部分
    # 编辑盘点单功能：搜索相关关键词
    edit_session_match = re.search(
        r'(function editSession|function displayEditSession|function saveBatchEdit|function cancelEdit|function finishEdit|function addToSessionInEdit)',
        file1_content
    )
    
    if edit_session_match:
        # 从找到的位置向前找<script>标签，向后找到</script>或下一个function之前
        start_index = file1_content.rfind('<script', 0, edit_session_match.start())
        if start_index == -1:
            start_index = 0
        
        # 向后找到下一个</script>或</body>
        end_index = file1_content.find('</script>', edit_session_match.start())
        if end_index == -1:
            end_index = len(file1_content)
    
        edit_session_code = file1_content[edit_session_match.start():end_index]
        print(f"✅ 提取到编辑盘点单功能代码，长度: {len(edit_session_code)}")
    
        # 保存到临时文件
        with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/edit_session_code.txt', 'w', encoding='utf-8') as f:
            f.write(edit_session_code)
    
    # 从78KB文件中提取AI分析功能的JavaScript部分
    ai_analysis_match = re.search(
        r'(function sendInventoryEmail|async function sendInventoryEmail)',
        file1_content
    )
    
    if ai_analysis_match:
        ai_analysis_code = file1_content[ai_analysis_match.start():]
        # 只取到第一个</script>标签
        end_ai_index = ai_analysis_code.find('</script>')
        if end_ai_index != -1:
            ai_analysis_code = ai_analysis_code[:end_ai_index]
    
        print(f"✅ 提取到AI分析功能代码，长度: {len(ai_analysis_code)}")
    
        # 保存到临时文件
        with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/ai_analysis_code.txt', 'w', encoding='utf-8') as f:
            f.write(ai_analysis_code)

    # 检查文件2中是否已包含这些功能
    has_edit_session = 'function editSession' in file2_content
    has_ai_analysis = 'function sendInventoryEmail' in file2_content
    
    print(f"\n文件2中是否包含编辑功能: {has_edit_session}")
    print(f"文件2中是否包含AI分析功能: {has_ai_analysis}")

    if not has_edit_session or not has_ai_analysis:
        print("\n⚠️ 需要合并这些功能到文件2中")
    else:
        print("\n✅ 文件2中已经包含这些功能")

if __name__ == "__main__":
    main()
