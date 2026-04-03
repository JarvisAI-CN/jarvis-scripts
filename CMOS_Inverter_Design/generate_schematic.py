#!/usr/bin/env python3
"""
生成CMOS反相器示意图
学号：20232107111
姓名：李文馨
"""

from PIL import Image, ImageDraw, ImageFont
import os

# 创建图片
width = 800
height = 600
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# 尝试使用字体，如果不存在则使用默认
try:
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    normal_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except:
    title_font = ImageFont.load_default()
    normal_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# 颜色定义
black = (0, 0, 0)
red = (200, 0, 0)
blue = (0, 0, 200)
green = (0, 150, 0)
gray = (150, 150, 150)
light_blue = (200, 200, 255)

# 标题
draw.text((width//2, 20), "CMOS反相器原理图", fill=black, font=title_font, anchor='mm')
draw.text((width//2, 50), "学号：20232107111  姓名：李文馨", fill=gray, font=small_font, anchor='mm')

# PMOS部分
pmos_y = 120
pmos_x = 300

# PMOS符号
draw.rectangle([pmos_x-30, pmos_y-30, pmos_x+30, pmos_y+30], outline=black, width=2)
draw.ellipse([pmos_x+25, pmos_y-5, pmos_x+35, pmos_y+5], outline=black, width=2)  # PMOS圆圈

# vdd连线
draw.line([pmos_x, pmos_y-30, pmos_x, 80], fill=black, width=2)
draw.text((pmos_x+40, 75), "vdd (1.8V)", fill=red, font=small_font)

# PMOS源极
draw.line([pmos_x, pmos_y-30, pmos_x, pmos_y-40], fill=black, width=2)
draw.text((pmos_x+40, pmos_y-40), "源极", fill=gray, font=small_font)

# PMOS参数
draw.text((pmos_x-120, pmos_y-20), "PMOS (p18)", fill=red, font=normal_font)
draw.text((pmos_x-120, pmos_y+5), "W = 1.0 μm", fill=black, font=small_font)
draw.text((pmos_x-120, pmos_y+25), "L = 180 nm", fill=black, font=small_font)

# NMOS部分
nmos_y = 300
nmos_x = 300

# NMOS符号
draw.rectangle([nmos_x-30, nmos_y-30, nmos_x+30, nmos_y+30], outline=black, width=2)

# vss连线
draw.line([nmos_x, nmos_y+30, nmos_x, 380], fill=black, width=2)
draw.text((nmos_x+40, 370), "vss (0V)", fill=blue, font=small_font)

# NMOS源极
draw.line([nmos_x, nmos_y+30, nmos_x, nmos_y+40], fill=black, width=2)
draw.text((nmos_x+40, nmos_y+40), "源极", fill=gray, font=small_font)

# NMOS参数
draw.text((nmos_x-120, nmos_y-20), "NMOS (n18)", fill=blue, font=normal_font)
draw.text((nmos_x-120, nmos_y+5), "W = 0.6 μm", fill=black, font=small_font)
draw.text((nmos_x-120, nmos_y+25), "L = 180 nm", fill=black, font=small_font)

# 输入A（栅极连接）
gate_y = (pmos_y + nmos_y) // 2
draw.line([pmos_x, pmos_y-30, pmos_x, pmos_y-50], fill=black, width=2)
draw.line([pmos_x, nmos_y+30, pmos_x, nmos_y+50], fill=black, width=2)

# 水平栅极连线
draw.line([pmos_x, pmos_y-50, pmos_x-80, pmos_y-50], fill=black, width=2)
draw.line([pmos_x-80, pmos_y-50, pmos_x-80, nmos_y+50], fill=black, width=2)
draw.line([pmos_x-80, nmos_y+50, pmos_x, nmos_y+50], fill=black, width=2)

# 输入端口A
draw.line([pmos_x-80, gate_y, 150, gate_y], fill=black, width=2)
draw.text((130, gate_y-10), "输入 A", fill=green, font=normal_font)

# 栅极标记
draw.text((pmos_x+40, pmos_y-50), "栅极", fill=gray, font=small_font)
draw.text((pmos_x+40, nmos_y+50), "栅极", fill=gray, font=small_font)

# 输出Y（漏极连接）
draw.line([pmos_x, pmos_y, pmos_x+100, pmos_y], fill=black, width=2)
draw.line([pmos_x+100, pmos_y, pmos_x+100, nmos_y], fill=black, width=2)
draw.line([pmos_x+100, nmos_y, nmos_x, nmos_y], fill=black, width=2)
draw.line([pmos_x+100, gate_y, 650, gate_y], fill=black, width=2)

# 输出端口Y
draw.text((660, gate_y-10), "输出 Y", fill=green, font=normal_font)

# 漏极标记
draw.text((pmos_x+40, pmos_y), "漏极", fill=gray, font=small_font)
draw.text((pmos_x+40, nmos_y), "漏极", fill=gray, font=small_font)

# 底部信息框
draw.rectangle([50, 420, 750, 580], outline=black, width=2)
draw.text((400, 440), "设计规格", fill=black, font=normal_font, anchor='mm')

spec_text = [
    "工艺: 180nm CMOS",
    "PMOS: W=1.0μm, L=180nm, m=1",
    "NMOS: W=0.6μm, L=180nm, m=1",
    "vdd = 1.8V, vss = 0V",
    "单元名: inv",
    "库名: 20232107111李文馨"
]

y_offset = 470
for text in spec_text:
    draw.text((70, y_offset), text, fill=black, font=small_font)
    y_offset += 20

# 保存图片
output_path = '/home/ubuntu/.openclaw/workspace/CMOS_Inverter_Design/cmos_inverter_schematic.png'
img.save(output_path, 'PNG')
print(f"✓ CMOS反相器原理图已生成：{output_path}")
