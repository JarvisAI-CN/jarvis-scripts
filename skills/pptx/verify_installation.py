#!/usr/bin/env python3
"""
PPTX技能安装验证脚本
测试所有依赖和功能
"""

import os
import sys
import subprocess
import json

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n🔍 测试: {description}")
    print(f"命令: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ 成功")
            if result.stdout.strip():
                print(f"输出: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"❌ 失败")
            if result.stderr.strip():
                print(f"错误: {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"❌ 异常: {str(e)[:200]}")
        return False

def main():
    print("=" * 60)
    print("PPTX技能安装验证")
    print("=" * 60)

    tests = [
        ("python -m markitdown --help", "markitdown - 文本提取"),
        ("python -c 'from PIL import Image; print(\"PIL OK\")'", "Pillow - 图像处理"),
        ("soffice --version", "LibreOffice - PPTX/PDF转换"),
        ("pdftoppm -v", "Poppler - PDF工具"),
        ("npm list -g pptxgenjs 2>/dev/null | grep pptxgenjs", "pptxgenjs - 创建PPTX"),
    ]

    results = []
    for cmd, desc in tests:
        results.append((desc, run_command(cmd, desc)))

    # 检查脚本文件
    print("\n🔍 测试: 脚本文件")
    scripts_dir = "/home/ubuntu/.openclaw/workspace/skills/pptx/scripts"
    required_scripts = ["thumbnail.py", "add_slide.py", "clean.py"]
    scripts_ok = True
    for script in required_scripts:
        script_path = os.path.join(scripts_dir, script)
        if os.path.exists(script_path):
            print(f"✅ {script} 存在")
        else:
            print(f"❌ {script} 缺失")
            scripts_ok = False
    results.append(("脚本文件", scripts_ok))

    # 检查虚拟环境
    print("\n🔍 测试: Python虚拟环境")
    venv_ok = os.path.exists("/home/ubuntu/.venv/pptx-skill/bin/activate")
    if venv_ok:
        print("✅ 虚拟环境存在")
    else:
        print("❌ 虚拟环境缺失")
    results.append(("虚拟环境", venv_ok))

    # 总结
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for desc, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {desc}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！PPTX技能安装成功！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 项测试失败，请检查安装")
        return 1

if __name__ == "__main__":
    sys.exit(main())
