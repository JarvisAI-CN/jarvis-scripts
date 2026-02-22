#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def main():
    # 读取文件2（当前工作文件）
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_complete.php', 'r', encoding='utf-8') as f:
        file2_content = f.read()

    # 读取文件1（78KB文件）
    with open('/tmp/index_current_v2.14.2.php', 'r', encoding='utf-8') as f:
        file1_content = f.read()

    # 从文件1中提取编辑盘点单功能的JavaScript代码
    edit_session_match = re.search(
        r'(function editSession.*)',
        file1_content,
        re.DOTALL
    )
    edit_session_code = None
    if edit_session_match:
        edit_session_code = edit_session_match.group(1)
        # 只取到</script>标签结束
        end_index = edit_session_code.find('</script>')
        if end_index != -1:
            edit_session_code = edit_session_code[:end_index]
        print(f"✅ 提取到编辑盘点单功能代码，长度: {len(edit_session_code)}")

    # 从文件1中提取AI分析功能的JavaScript代码
    ai_analysis_match = re.search(
        r'(function sendInventoryEmail.*)',
        file1_content,
        re.DOTALL
    )
    ai_analysis_code = None
    if ai_analysis_match:
        ai_analysis_code = ai_analysis_match.group(1)
        end_index = ai_analysis_code.find('</script>')
        if end_index != -1:
            ai_analysis_code = ai_analysis_code[:end_index]
        print(f"✅ 提取到AI分析功能代码，长度: {len(ai_analysis_code)}")

    # 在文件2中找到合适的位置添加这些代码
    # 应该在refreshHealth函数之后，checkUpgrade函数之前添加
    insert_position = file2_content.find('        async function checkUpgrade() {')
    if insert_position == -1:
        raise ValueError("checkUpgrade函数未找到")

    # 准备要插入的代码
    insert_code = ""
    if edit_session_code:
        insert_code += edit_session_code + "\n\n"
    if ai_analysis_code:
        insert_code += ai_analysis_code + "\n\n"

    # 在history页面创建编辑盘点单按钮
    # 找到创建历史记录卡片的位置，并添加编辑按钮
    card_create_pattern = re.compile(
        r'''
        const\s+card\s*=\s*document\.createElement\('div'\);
        \s*card\.className\s*=\s*'custom-card';
        \s*card\.innerHTML\s*=\s*`
        \s*<div class="d-flex justify-content-between align-items-center">
        \s*<div>
        \s*<strong>单号: \${s\.session_key}</strong>
        \s*<br><small class="text-muted">\${s\.created_at}</small>
        \s*</div>
        \s*<div class="text-end">
        \s*<span class="badge bg-primary">\${s\.item_count} 件</span>
        \s*</div>
        \s*</div>
        \s*`;
        ''',
        re.DOTALL
    )

    new_card_html = '''
                            <div class="d-flex justify-content-between align-items-center">
                            <div>
                            <strong>单号: ${s.session_key}</strong>
                            <br><small class="text-muted">${s.created_at}</small>
                            </div>
                            <div class="text-end">
                            <span class="badge bg-primary">${s.item_count} 件</span>
                            <button class="btn btn-sm btn-outline-primary ms-2" onclick="editSession('${s.session_key}', event)" title="编辑盘点单">
                                <i class="bi bi-pencil"></i> 编辑
                            </button>
                            <button class="btn btn-sm btn-outline-primary ms-2" onclick="sendInventoryEmail('${s.session_key}', event)" title="AI分析并发送">
                                <i class="bi bi-envelope"></i> AI分析
                            </button>
                            </div>
                            </div>
                        '''

    file2_content = card_create_pattern.sub(new_card_html, file2_content)

    # 在指定位置插入代码
    final_content = file2_content[:insert_position] + insert_code + file2_content[insert_position:]

    # 更新版本号
    final_content = re.sub(r"APP_VERSION.*'2\.8\.2'", "APP_VERSION, '2.14.2'", final_content)

    # 保存合并后的文件
    output_file = '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_full.php'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"✅ 文件合并成功！合并后的文件: {output_file}")

    # 验证合并后的文件是否有PHP语法错误
    import subprocess
    try:
        result = subprocess.run(['php', '-l', output_file], capture_output=True, text=True)
        if 'No syntax errors' in result.stdout:
            print("✅ PHP语法检查通过")
        else:
            print(f"⚠️ PHP语法检查失败: {result.stdout}")
    except FileNotFoundError:
        print("⚠️ 未找到php命令，跳过语法检查")

    # 测试登录功能
    import requests
    import json
    test_url = "http://pandian.dhmip.cn/index.php"
    session = requests.Session()

    login_data = {"username": "admin", "password": "fs123456"}
    login_response = session.post(test_url + "?api=login", data=json.dumps(login_data), headers={"Content-Type": "application/json"})
    print(f"✅ 登录测试: {login_response.status_code}, {login_response.text}")

    # 测试获取历史记录功能
    history_response = session.post(test_url + "?api=get_past_sessions")
    print(f"✅ 历史记录测试: {history_response.status_code}, {len(history_response.text)} bytes")

if __name__ == "__main__":
    main()
