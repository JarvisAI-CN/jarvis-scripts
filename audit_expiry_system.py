#!/usr/bin/env python3
"""
保质期管理系统代码审计工具
使用专业工具全面检查代码质量
"""

import subprocess
import os
from pathlib import Path

# 项目路径
PROJECT_PATHS = [
    "/home/ubuntu/.openclaw/workspace/PARA/Projects/保质期管理系统/",
    "/home/ubuntu/.openclaw/workspace/保质期管理系统/",
    "/var/www/html/expiry/",
    "/home/ubuntu/expiry-system/",
]

def find_project():
    """查找保质期管理系统代码"""
    for path in PROJECT_PATHS:
        if os.path.exists(path):
            print(f"✅ 找到项目: {path}")
            return path
    print("❌ 未找到本地项目代码")
    return None

def audit_with_black(project_path):
    """使用black检查代码格式"""
    print("\n=== Black 代码格式检查 ===")
    py_files = list(Path(project_path).rglob("*.py"))
    
    if not py_files:
        print("未找到Python文件")
        return
    
    for py_file in py_files:
        print(f"\n检查: {py_file.name}")
        try:
            # 检查格式
            result = subprocess.run(
                ["black", "--check", str(py_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ 格式正确")
            else:
                print("  ⚠️ 需要格式化")
                # 自动格式化
                subprocess.run(["black", str(py_file)], capture_output=True)
                print("  ✅ 已自动格式化")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def audit_with_ruff(project_path):
    """使用ruff检查代码质量"""
    print("\n=== Ruff 代码质量检查 ===")
    
    try:
        result = subprocess.run(
            ["ruff", "check", project_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 没有发现问题")
        else:
            print("⚠️ 发现问题:")
            print(result.stdout)
            
        # 显示统计信息
        result = subprocess.run(
            ["ruff", "check", "--statistics", project_path],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print("\n📊 问题统计:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ 错误: {e}")

def audit_with_mypy(project_path):
    """使用mypy进行类型检查"""
    print("\n=== Mypy 类型检查 ===")
    
    py_files = list(Path(project_path).rglob("*.py"))
    
    if not py_files:
        print("未找到Python文件")
        return
    
    for py_file in py_files:
        print(f"\n检查: {py_file.name}")
        try:
            result = subprocess.run(
                ["mypy", str(py_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("  ✅ 类型检查通过")
            else:
                print("  ⚠️ 类型问题:")
                print("  " + "\n  ".join(result.stdout.split("\n")[:10]))
        except Exception as e:
            print(f"  ⚠️ 无法检查: {e}")

def audit_with_pylint(project_path):
    """使用pylint深度分析"""
    print("\n=== Pylint 深度分析 ===")
    
    py_files = list(Path(project_path).rglob("*.py"))
    
    if not py_files:
        print("未找到Python文件")
        return
    
    for py_file in py_files[:3]:  # 只检查前3个文件，避免太慢
        print(f"\n分析: {py_file.name}")
        try:
            result = subprocess.run(
                ["pylint", str(py_file)],
                capture_output=True,
                text=True
            )
            
            # 提取评分
            for line in result.stdout.split("\n"):
                if "Your code has been rated" in line:
                    print(f"  📊 {line.strip()}")
                    break
        except Exception as e:
            print(f"  ⚠️ 无法分析: {e}")

def security_audit(project_path):
    """安全审计"""
    print("\n=== 安全审计 ===")
    
    # 检查敏感信息
    sensitive_patterns = [
        ("password", "密码"),
        ("api_key", "API密钥"),
        ("secret", "密钥"),
        ("token", "令牌"),
    ]
    
    py_files = list(Path(project_path).rglob("*.py"))
    
    issues_found = False
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for i, (pattern, name) in enumerate(sensitive_patterns):
                    if pattern in content.lower():
                        print(f"⚠️ {py_file.name}: 可能包含{name}")
                        issues_found = True
        except:
            pass
    
    if not issues_found:
        print("✅ 未发现明显的安全问题")

def performance_audit(project_path):
    """性能审计"""
    print("\n=== 性能审计 ===")
    
    py_files = list(Path(project_path).rglob("*.py"))
    
    total_lines = 0
    large_files = []
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                
                if lines > 500:
                    large_files.append((py_file.name, lines))
        except:
            pass
    
    print(f"📊 代码统计:")
    print(f"  总文件数: {len(py_files)}")
    print(f"  总行数: {total_lines}")
    
    if large_files:
        print(f"\n⚠️ 大文件 (>500行):")
        for name, lines in large_files:
            print(f"  {name}: {lines}行")
            print(f"    💡 建议: 拆分为多个模块")

def main():
    print("=" * 60)
    print("🔍 保质期管理系统代码审计")
    print("=" * 60)
    
    # 查找项目
    project_path = find_project()
    
    if not project_path:
        print("\n💡 提示: 可以从宝塔服务器下载代码进行审计")
        print("   服务器: 82.157.20.7")
        print("   路径: /www/wwwroot/ceshi.dhmip.cn")
        return
    
    # 执行审计
    audit_with_black(project_path)
    audit_with_ruff(project_path)
    audit_with_mypy(project_path)
    audit_with_pylint(project_path)
    security_audit(project_path)
    performance_audit(project_path)
    
    print("\n" + "=" * 60)
    print("✅ 审计完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
