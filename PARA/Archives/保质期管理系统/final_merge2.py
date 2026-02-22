#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def main():
    # 读取v2.8.2（有登录判断）
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_final.php', 'r', encoding='utf-8') as f:
        file2_content = f.read()

    # 读取78KB文件（含编辑和AI分析）
    with open('/tmp/index_current_v2.14.2.php', 'r', encoding='utf-8') as f:
        file1_content = f.read()

    # 提取编辑功能代码
    edit_code = None
    edit_match = re.search(r'(function editSession.*)', file1_content, re.DOTALL)
    if edit_match:
        edit_code = edit_match.group(1)
        edit_code = edit_code.split('</script>')[0]
        print(f"✅ 编辑功能代码长度: {len(edit_code)}")

    # 提取AI分析功能代码
    ai_code = None
    ai_match = re.search(r'(function sendInventoryEmail.*)', file1_content, re.DOTALL)
    if ai_match:
        ai_code = ai_match.group(1)
        ai_code = ai_code.split('</script>')[0]
        print(f"✅ AI分析功能代码长度: {len(ai_code)}")

    # 更新版本号到v2.14.2
    file2_content = re.sub(r"define\('APP_VERSION', '2.8.2'\);", "define('APP_VERSION', '2.14.2');", file2_content)

    # 在history页面添加编辑按钮
    history_card_pattern = re.compile(
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
                            const card = document.createElement('div');
                            card.className = 'custom-card';
                            card.innerHTML = `
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
                        `;
                        '''

    file2_content = history_card_pattern.sub(new_card_html, file2_content)

    # 在checkUpgrade函数之后添加编辑和AI分析代码
    insert_position = file2_content.find('        async function checkUpgrade() {')
    if insert_position == -1:
        raise ValueError("checkUpgrade函数未找到")

    insert_code = ""
    if edit_code:
        insert_code += edit_code + "\n\n"
    if ai_code:
        insert_code += ai_code + "\n\n"

    file2_content = file2_content[:insert_position] + insert_code + file2_content[insert_position:]

    # 保存最终文件
    with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_final.php', 'w', encoding='utf-8') as f:
        f.write(file2_content)

    print("✅ 最终合并完成")

    # 检查PHP语法
    import subprocess
    try:
        result = subprocess.run(['php', '-l', '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/index_v2.14.2_final.php'], capture_output=True, text=True)
        if 'No syntax errors' in result.stdout:
            print("✅ PHP语法检查通过")
        else:
            print(f"❌ PHP语法检查失败: {result.stdout}")
    except FileNotFoundError:
        print("⚠️ 未找到php命令，跳过语法检查")

if __name__ == "__main__":
    main()
