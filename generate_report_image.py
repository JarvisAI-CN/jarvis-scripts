"""
生成实验报告图片
"""
from PIL import Image, ImageDraw, ImageFont
import textwrap

# 创建图片
width = 900
height = 1300
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# 颜色定义
title_color = (51, 51, 51)
heading_color = (102, 126, 234)
text_color = (68, 68, 68)
border_color = (102, 126, 234)

# 绘制标题
try:
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 32)
    heading_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 22)
    normal_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
    code_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 13)
except:
    title_font = ImageFont.load_default()
    heading_font = ImageFont.load_default()
    normal_font = ImageFont.load_default()
    small_font = ImageFont.load_default()
    code_font = ImageFont.load_default()

y = 40

# 标题
title = "Python课程上机实验报告（一）"
draw.text((width//2, y), title, fill=title_color, font=title_font, anchor='mm')
y += 50

# 信息表格
info_data = [
    ("学院", "信息学院"),
    ("班级", "数据科学与大数据技术2301班"),
    ("学号", "20232107111"),
    ("姓名", "李文馨"),
    ("实验名称", "熟悉Python编程环境和简单的Python程序"),
    ("实验地点", "13号机 302机房"),
    ("指导教师", "王芳"),
    ("实验日期", "2024年4月8日"),
]

# 绘制表格边框
table_y = y
for i, (label, value) in enumerate(info_data):
    draw.rectangle([50, table_y + i*35, 850, table_y + (i+1)*35], outline='#ddd', width=1)
    draw.rectangle([50, table_y + i*35, 200, table_y + (i+1)*35], fill='#f8f9fa', outline='#ddd')
    draw.text((60, table_y + i*35 + 8), label, fill=text_color, font=normal_font)
    draw.text((210, table_y + i*35 + 8), value, fill=text_color, font=normal_font)

y = table_y + len(info_data) * 35 + 40

# 一、实验目的
draw.text((50, y), "一、实验目的", fill=heading_color, font=heading_font)
y += 35

objectives = [
    "1. 掌握Python环境的搭建与配置",
    "2. 掌握Python程序的编辑、运行和调试方法",
    "3. 掌握Python基本语法和编程规范",
    "4. 熟练掌握Python中的输入输出函数",
    "5. 熟练掌握Python中的运算符和表达式",
]

for obj in objectives:
    draw.text((70, y), obj, fill=text_color, font=normal_font)
    y += 25

y += 20

# 二、实验内容
draw.text((50, y), "二、实验内容", fill=heading_color, font=heading_font)
y += 35

contents = [
    "根据选题指南，选择以下3个题目：",
    "1. 计算圆的周长和面积：输入半径，计算周长和面积",
    "2. 判断三位水仙花数：输入三位数，判断是否为水仙花数",
    "3. 判断闰年：输入年份，判断是否为闰年",
]

for content in contents:
    draw.text((70, y), content, fill=text_color, font=normal_font)
    y += 25

y += 20

# 三、程序代码与运行结果
draw.text((50, y), "三、程序代码与运行结果", fill=heading_color, font=heading_font)
y += 35

# 题目1
draw.text((70, y), "【题目1】计算圆的周长和面积", fill='#333', font=normal_font)
y += 30

draw.rectangle([70, y, 830, y+130], fill='#f4f4f4', outline=heading_color, width=2)
code1 = [
    'import math',
    'radius = float(input("请输入圆的半径："))',
    'circumference = 2 * math.pi * radius',
    'area = math.pi * radius ** 2',
    'print(f"周长 = {circumference:.2f}")',
    'print(f"面积 = {area:.2f}")',
]
for line in code1:
    draw.text((80, y+5), line, fill='#333', font=code_font)
    y += 18
y += 10

draw.rectangle([70, y, 830, y+60], fill='#f0f7ff', outline='#2196F3', width=2)
draw.text((80, y+8), "运行结果：", fill='#2196F3', font=normal_font)
y += 22
draw.text((80, y+8), "输入：半径 = 5.0", fill=text_color, font=small_font)
y += 20
draw.text((80, y+8), "输出：周长 = 31.42，面积 = 78.54", fill=text_color, font=small_font)
y += 30

y += 15

# 题目2
draw.text((70, y), "【题目2】判断三位水仙花数", fill='#333', font=normal_font)
y += 30

draw.rectangle([70, y, 830, y+110], fill='#f4f4f4', outline=heading_color, width=2)
code2 = [
    'num = int(input("请输入一个三位数："))',
    'hundreds = num // 100',
    'tens = (num // 10) % 10',
    'units = num % 10',
    'sum_of_cubes = hundreds**3 + tens**3 + units**3',
    'if num == sum_of_cubes:',
    '    print(f"{num} 是水仙花数！")',
]
for line in code2:
    draw.text((80, y+5), line, fill='#333', font=code_font)
    y += 14
y += 10

draw.rectangle([70, y, 830, y+50], fill='#f0f7ff', outline='#2196F3', width=2)
draw.text((80, y+8), "测试结果：153(✓)、370(✓)、371(✓)、407(✓)、123(✗)", fill=text_color, font=small_font)
y += 30

# 保存图片
img.save('/home/ubuntu/.openclaw/workspace/实验报告.png', 'PNG', quality=95)
print("✓ 实验报告图片已生成：实验报告.png")
