#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动创建项目结构
遵循PARA系统 + Obsidian双链标准

使用方法:
  python3 create_project.py "项目名称"
"""

import os
import sys
from datetime import datetime

# 基础路径
BASE_PATH = "/home/ubuntu/.openclaw/workspace/PARA/Projects"

def create_project_structure(name):
    """创建标准项目结构"""

    project_path = f"{BASE_PATH}/{name}"

    # 创建目录结构
    dirs = [
        "截止日期跟结果描述",
        "项目任务",
        "项目闪念",
        f"这个项目的文件/脚本",
        f"这个项目的文件/文档",
        f"这个项目的文件/日志"
    ]

    print(f"📂 创建项目: {name}")
    print(f"   位置: {project_path}")

    for d in dirs:
        dir_path = f"{project_path}/{d}"
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ 创建目录: {d}")

    # 创建README.md
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    readme_content = f"""# {name}

**创建时间**: {datetime.now().strftime('%Y-%m-%d')}
**状态**: 🔄 进行中
**优先级**: ⭐⭐⭐

---

## 项目概述

简要描述项目的目标、背景和意义。

---

## 1. 截止日期跟结果描述

### 时间线
- **开始日期**: {datetime.now().strftime('%Y-%m-%d')}
- **截止日期**: 待定
- **实际完成**: 待定

### 交付成果
- [ ] 成果1: [[截止日期跟结果描述/成果1]]
- [ ] 成果2: [[截止日期跟结果描述/成果2]]
- [ ] 成果3: [[截止日期跟结果描述/成果3]]

### 成功标准
- [ ] 标准1: [[量化指标]]
- [ ] 标准2: [[量化指标]]
- [ ] 标准3: [[量化指标]]

---

## 2. 项目任务

### 任务列表
- [ ] [[项目任务/task-01-待定]] - 状态: ⏳ | 截止: 待定
- [ ] [[项目任务/task-02-待定]] - 状态: ⏳ | 截止: 待定
- [ ] [[项目任务/task-03-待定]] - 状态: ⏳ | 截止: 待定

### 任务详情
详见各任务文件：[[项目任务/]]

---

## 3. 项目闪念

### 💡 想法记录
- [[项目闪念/闪念-初始想法]] - {datetime.now().strftime('%Y-%m-%d')}

### 📝 灵感来源
- 来自: [[相关笔记/项目/资源]]
- 灵感: ...
- 行动: [[项目任务/新任务]]

### 🔄 待整理的闪念
- 临时想法1
- 临时想法2
- 临时想法3

---

## 4. 这个项目的文件

### 脚本文件
- [[这个项目的文件/脚本/script1.py]] - 功能描述
- [[这个项目的文件/脚本/script2.sh]] - 功能描述

### 文档文件
- [[这个项目的文件/文档/design.md]] - 设计文档
- [[这个项目的文件/文档/api.md]] - API文档

### 日志文件
- [[这个项目的文件/日志/log.txt]] - 运行日志
- [[这个项目的文件/日志/error.log]] - 错误日志

### 相关资源
- [[外部资源链接]]
- [[相关项目]]

---

## 🔗 相关链接

- **所属领域**: [[PARA/Areas/相关领域]]
- **相关资源**: [[PARA/Resources/相关资源]]
- **依赖项目**: [[其他项目]]

---

## 📊 进度追踪

### 完成度
- 总任务: 0个
- 已完成: 0个
- 进行中: 0个
- 完成率: 0%

### 最近更新
- {datetime.now().strftime('%Y-%m-%d')}: 项目创建

---

## 🎓 经验教训

### 做得好的
- 经验1: [[详细记录]]
- 经验2: [[详细记录]]

### 需要改进
- 问题1: [[详细记录]] + 改进方案
- 问题2: [[详细记录]] + 改进方案

### 下次优化
- 优化点1: [[具体方案]]
- 优化点2: [[具体方案]]

---

**最后更新**: {timestamp}
"""

    readme_path = f"{project_path}/README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"   ✅ 创建README.md")

    # 创建第一个闪念文件
    flash_path = f"{project_path}/项目闪念/闪念-初始想法.md"
    flash_content = f"""# 闪念 - 初始想法

**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**项目**: [[{name}]]

---

## 💡 想法

记录项目初始的想法和灵感。

---

## 🔗 相关

- 项目主页: [[../README.md]]
- 待办任务: [[../项目任务/]]

---

**创建时间**: {timestamp}
"""
    with open(flash_path, 'w', encoding='utf-8') as f:
        f.write(flash_content)

    print(f"   ✅ 创建初始闪念文件")

    print(f"\n✅ 项目 '{name}' 创建完成！")
    print(f"   路径: {project_path}")
    print(f"\n📝 下一步:")
    print(f"   1. 编辑README.md，填写项目概述")
    print(f"   2. 添加任务到 [[项目任务/]]")
    print(f"   3. 记录闪念到 [[项目闪念/]]")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("❌ 错误: 请提供项目名称")
        print("\n使用方法:")
        print("  python3 create_project.py \"项目名称\"")
        print("\n示例:")
        print("  python3 create_project.py \"ImageHub技术分享\"")
        print("  python3 create_project.py \"自建邮件网站\"")
        sys.exit(1)

    project_name = sys.argv[1]

    # 检查项目是否已存在
    project_path = f"{BASE_PATH}/{project_name}"
    if os.path.exists(project_path):
        print(f"⚠️ 项目 '{project_name}' 已存在")
        print(f"   路径: {project_path}")
        response = input("是否继续？(y/n): ")
        if response.lower() != 'y':
            print("❌ 已取消")
            sys.exit(1)

    try:
        create_project_structure(project_name)
    except Exception as e:
        print(f"❌ 创建失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
