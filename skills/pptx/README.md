# PPTX技能 - 安装完成

**安装日期**: 2026-02-18
**状态**: ✅ 安装成功，所有功能正常

---

## 📦 已安装组件

### Python依赖 (虚拟环境: ~/.venv/pptx-skill/)
- ✅ markitdown[pptx] - PPTX文本提取
- ✅ Pillow - 图像处理

### Node.js依赖
- ✅ pptxgenjs@4.0.1 - 创建PPTX演示文稿

### 系统工具
- ✅ LibreOffice 24.2.7.2 - PPTX/PDF转换
- ✅ Poppler 24.02.0 - PDF工具

### 技能文件
- ✅ SKILL.md - 技能主文档
- ✅ editing.md - 编辑工作流
- ✅ pptxgenjs.md - 创建指南
- ✅ scripts/ - 工具脚本

---

## 🚀 快速开始

### 激活环境
```bash
source ~/.venv/pptx-skill/bin/activate
```

### 读取PPTX内容
```bash
# 文本提取
python -m markitdown presentation.pptx

# 保存到文件
python -m markitdown presentation.pptx -o presentation.md

# 生成缩略图预览
python /home/ubuntu/.openclaw/workspace/skills/pptx/scripts/thumbnail.py presentation.pptx
```

### 编辑PPTX
详见 `editing.md`:
```bash
cd /home/ubuntu/.openclaw/workspace/skills/pptx
less editing.md
```

### 从零创建PPTX
详见 `pptxgenjs.md`:
```bash
cd /home/ubuntu/.openclaw/workspace/skills/pptx
less pptxgenjs.md
```

---

## 📋 验证安装

运行验证脚本确认所有组件正常:
```bash
source ~/.venv/pptx-skill/bin/activate
python /home/ubuntu/.openclaw/workspace/skills/pptx/verify_installation.py
```

预期输出: 7/7 项测试通过

---

## 🛠️ 技能位置

- 技能目录: `/home/ubuntu/.openclaw/workspace/skills/pptx/`
- 虚拟环境: `~/.venv/pptx-skill/`
- 验证脚本: `/home/ubuntu/.openclaw/workspace/skills/pptx/verify_installation.py`

---

## 📚 参考文档

- [SKILL.md](SKILL.md) - 技能总览
- [editing.md](editing.md) - 编辑工作流
- [pptxgenjs.md](pptxgenjs.md) - 创建指南
- [scripts/](scripts/) - 工具脚本

---

## 🎯 主要功能

1. **读取/分析PPTX**
   - 提取文本内容到Markdown
   - 生成缩略图网格预览
   - 解析原始XML结构

2. **编辑PPTX**
   - 使用模板修改内容
   - 添加/删除幻灯片
   - 清理和优化文件

3. **创建PPTX**
   - 从零生成演示文稿
   - 使用JavaScript API
   - 支持布局和样式

4. **格式转换**
   - PPTX → PDF (LibreOffice)
   - PDF → 图片 (Poppler)
   - 批量处理

---

**安装完成！可以开始使用PPTX技能了。** 🎉
