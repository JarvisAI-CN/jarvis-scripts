#!/usr/bin/env python3
"""
保质期管理系统 - 配置测试脚本
验证优化版本是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """测试必要的库是否可用"""
    print("=== 测试导入 ===")
    
    try:
        import mysql.connector
        print("✅ mysql.connector")
    except ImportError as e:
        print(f"❌ mysql.connector: {e}")
        return False
    
    try:
        from datetime import datetime, timedelta
        print("✅ datetime")
    except ImportError as e:
        print(f"❌ datetime: {e}")
        return False
    
    try:
        from typing import List, Dict, Optional
        print("✅ typing")
    except ImportError as e:
        print(f"❌ typing: {e}")
        return False
    
    return True

def test_code_quality():
    """测试代码质量"""
    print("\n=== 测试代码质量 ===")
    
    # 测试black
    import subprocess
    result = subprocess.run(
        ["black", "--check", "optimized_expiry_manager.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Black格式检查通过")
    else:
        print("⚠️ Black格式需要调整")
    
    # 测试ruff
    result = subprocess.run(
        ["ruff", "check", "optimized_expiry_manager.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Ruff质量检查通过")
    else:
        print("⚠️ Ruff发现问题:")
        print(result.stdout)

def test_database_connection():
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===")
    
    try:
        import mysql.connector
        
        # 尝试连接
        conn = mysql.connector.connect(
            host='localhost',
            user='expiry_user',
            password='Expiry2024!',
            database='expiry_system'
        )
        
        if conn.is_connected():
            print("✅ 数据库连接成功")
            
            # 测试查询
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM items")
            count = cursor.fetchone()[0]
            print(f"✅ 数据库查询成功 (共{count}条记录)")
            
            cursor.close()
            conn.close()
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_class_structure():
    """测试类结构"""
    print("\n=== 测试类结构 ===")
    
    try:
        from optimized_expiry_manager import ExpiryManager
        
        # 检查类是否有必要的方法
        methods = ['__init__', 'connect', 'disconnect', 'check_expiry', 'generate_alert']
        
        for method in methods:
            if hasattr(ExpiryManager, method):
                print(f"✅ ExpiryManager.{method}")
            else:
                print(f"❌ 缺少方法: {method}")
                return False
        
        return True
    except ImportError as e:
        print(f"❌ 无法导入类: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 保质期管理系统 - 优化版本测试")
    print("=" * 60)
    
    # 运行测试
    tests = [
        ("导入测试", test_imports),
        ("代码质量测试", test_code_quality),
        ("类结构测试", test_class_structure),
        ("数据库连接测试", test_database_connection),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name}出错: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！可以部署！")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())
