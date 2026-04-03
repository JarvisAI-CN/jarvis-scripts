#!/bin/bash
# CMOS反相器设计 - 一键设置脚本
# 学号：20232107111
# 姓名：李文馨

echo "=========================================="
echo "  180nm CMOS反相器设计 - 环境设置"
echo "=========================================="
echo ""
echo "学号：20232107111"
echo "姓名：李文馨"
echo "工艺：180nm CMOS"
echo ""

# 创建工作目录
echo "创建工作目录..."
mkdir -p CMOS_Inverter_Design
cd CMOS_Inverter_Design

echo "✓ 工作目录创建完成"
echo "  当前路径: $(pwd)"
echo ""

# 检查Cadence是否安装
if command -v virtuoso &> /dev/null; then
    echo "✓ Cadence Virtuoso 已安装"
    virtuoso -v
else
    echo "⚠ Cadence Virtuoso 未找到"
    echo "  请确保已安装并配置环境变量"
fi
echo ""

# 显示设计规格
echo "=========================================="
echo "  设计规格"
echo "=========================================="
echo "PMOS: W=1.0um, L=180nm, m=1"
echo "NMOS: W=0.6um, L=180nm, m=1"
echo "单元名: inv"
echo "库名: 20232107111李文馨"
echo ""
echo "端口定义:"
echo "  A   - Input"
echo "  Y   - Output"
echo "  vdd - InputOutput (1.8V)"
echo "  vss - InputOutput (0V)"
echo ""

# 显示文件清单
echo "=========================================="
echo "  文件清单"
echo "=========================================="
ls -lh *.md *.il 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# 显示使用说明
echo "=========================================="
echo "  使用说明"
echo "=========================================="
echo ""
echo "1. 查看完整文档:"
echo "   cat README.md"
echo ""
echo "2. 查看详细步骤:"
echo "   cat STEP_BY_STEP.md"
echo ""
echo "3. 查看快速参考:"
echo "   cat QUICK_REFERENCE.md"
echo ""
echo "4. 启动Cadence Virtuoso:"
echo "   virtuoso &"
echo ""
echo "5. 在Virtuoso CIW窗口加载脚本:"
echo "   load(\"create_schematic.il\")"
echo "   load(\"create_layout.il\")"
echo "   load(\"verification.il\")"
echo ""
echo "6. 运行设计函数:"
echo "   CMOSInverterSchematic()"
echo "   CMOSInverterLayout()"
echo "   RunDRC()"
echo "   RunLVS()"
echo ""
echo "=========================================="
echo "  准备完成！开始设计吧！"
echo "=========================================="
