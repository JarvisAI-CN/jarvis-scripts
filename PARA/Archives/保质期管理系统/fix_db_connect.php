
<?php
/**
 * 修复数据库连接问题
 */

// 读取create_working_2142.php
with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/create_working_2142.php', 'r', encoding='utf-8') as f:
    content = f.read()

// 替换数据库连接参数
// 使用服务器上的数据库连接信息（从db.php获取）
// 从db.php读取连接信息
with open('/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/db.php', 'r', encoding='utf-8') as f:
    db_content = f.read()

// 从db.php中提取连接信息
import re
db_host = re.search(r"host\s*=\s*['\"](.*?)['\"]", db_content)
db_user = re.search(r"user\s*=\s*['\"](.*?)['\"]", db_content)
db_pass = re.search(r"password\s*=\s*['\"](.*?)['\"]", db_content)
db_name = re.search(r"dbname\s*=\s*['\"](.*?)['\"]", db_content)

if not all([db_host, db_user, db_pass, db_name]):
    print("❌ 无法从db.php提取连接信息")
    exit(1)

db_host = db_host.group(1)
db_user = db_user.group(1)
db_pass = db_pass.group(1)
db_name = db_name.group(1)

print(f"✅ 从db.php提取连接信息: host={db_host}, user={db_user}, dbname={db_name}")

// 替换getDBConnection函数
old_connection = '''
function getDBConnection() {
    $servername = 'localhost';
    $username = 'pandian';
    $password = 'pandian';
    $dbname = 'pandian';

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {
        die("连接失败: " . $conn->connect_error);
    }
    return $conn;
}
'''

new_connection = f'''
function getDBConnection() {{
    $servername = '{db_host}';
    $username = '{db_user}';
    $password = '{db_pass}';
    $dbname = '{db_name}';

    $conn = new mysqli($servername, $username, $password, $dbname);
    if ($conn->connect_error) {{
        die("连接失败: " . $conn->connect_error);
    }}
    return $conn;
}}
'''.strip()

content = content.replace(old_connection.strip(), new_connection)

// 保存修复后的文件
output_path = '/home/ubuntu/.openclaw/workspace/PARA/Archives/保质期管理系统/create_working_2142_fixed.php'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 数据库连接信息替换成功")
?>
