#!/usr/bin/env python3
"""
生成CMOS反相器版图示意图
学号：20232107111
姓名：李文馨
"""

from PIL import Image, ImageDraw, ImageFont

# 创建图片
width = 800
height = 700
img = Image.new('RGB', (width, height), color='white')
draw = ImageDraw.Draw(img)

# 颜色定义
black = (0, 0, 0)
red = (220, 50, 50)        # nwell
green = (50, 180, 50)      # active
blue = (50, 50, 220)       # poly
gray = (150, 150, 150)
light_red = (255, 200, 200)
light_green = (200, 255, 200)
light_blue = (200, 200, 255)
yellow = (255, 200, 0)

# 字体
try:
    title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
    normal_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    small_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
except:
    title_font = ImageFont.load_default()
    normal_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# 标题
draw.text((width//2, 20), "CMOS反相器版图 (180nm工艺)", fill=black, font=title_font, anchor='mm')
draw.text((width//2, 50), "学号：20232107111  姓名：李文馨", fill=gray, font=small_font, anchor='mm')
draw.text((width//2, 70), "库路径：20232107111李文馨/inv/layout", fill=gray, font=small_font, anchor='mm')

# 坐标定义
x_start = 150
y_pm = 120  # PMOS区域起始Y
y_nm = 380  # NMOS区域起始Y

# ===== PMOS部分（上方）=====
# nwell (红色背景)
draw.rectangle([x_start, y_pm, x_start+500, y_pm+180], fill=light_red, outline=red, width=3)
draw.text((x_start+250, y_pm+10), "nwell (PMOS阱)", fill=red, font=normal_font, anchor='mm')

# PMOS active (绿色有源区)
pm_active_x = x_start + 80
pm_active_y = y_pm + 40
draw.rectangle([pm_active_x, pm_active_y, pm_active_x+340, pm_active_y+100], fill=light_green, outline=green, width=2)
draw.text((pm_active_x+170, pm_active_y+50), "active (有源区)", fill=green, font=small_font, anchor='mm')

# PMOS poly (蓝色栅极)
pm_poly_x = pm_active_x + 170
draw.rectangle([pm_poly_x-8, pm_active_y-10, pm_poly_x+8, pm_active_y+120], fill=light_blue, outline=blue, width=2)
draw.text((pm_poly_x, pm_active_y-20), "poly", fill=blue, font=small_font, anchor='mm')

# PMOS接触孔 (cc)
pm_cc1_x = pm_active_x + 80
pm_cc_y = pm_active_y + 50
draw.rectangle([pm_cc1_x-10, pm_cc_y-10, pm_cc1_x+10, pm_cc_y+10], fill=yellow, outline=black, width=2)

pm_cc2_x = pm_active_x + 260
draw.rectangle([pm_cc2_x-10, pm_cc_y-10, pm_cc2_x+10, pm_cc_y+10], fill=yellow, outline=black, width=2)
draw.text((pm_cc1_x, pm_cc_y-20), "cc", fill=black, font=small_font, anchor='mm')

# PMOS pselect标记
draw.rectangle([pm_active_x-20, pm_active_y-20, pm_active_x+360, pm_active_y+140], outline=red, width=2)
draw.text((pm_active_x-40, pm_active_y+80), "pselect", fill=red, font=small_font, anchor='mm')

# ===== NMOS部分（下方）=====
# NMOS active (绿色有源区)
nm_active_x = x_start + 80
nm_active_y = y_nm + 30
draw.rectangle([nm_active_x, nm_active_y, nm_active_x+260, nm_active_y+90], fill=light_green, outline=green, width=2)
draw.text((nm_active_x+130, nm_active_y+45), "active (有源区)", fill=green, font=small_font, anchor='mm')

# NMOS poly (蓝色栅极)
nm_poly_x = nm_active_x + 130
draw.rectangle([nm_poly_x-8, nm_active_y-10, nm_poly_x+8, nm_active_y+110], fill=light_blue, outline=blue, width=2)
draw.text((nm_poly_x, nm_active_y-20), "poly", fill=blue, font=small_font, anchor='mm')

# NMOS接触孔 (cc)
nm_cc1_x = nm_active_x + 60
nm_cc_y = nm_active_y + 45
draw.rectangle([nm_cc1_x-10, nm_cc_y-10, nm_cc1_x+10, nm_cc_y+10], fill=yellow, outline=black, width=2)

nm_cc2_x = nm_active_x + 200
draw.rectangle([nm_cc2_x-10, nm_cc_y-10, nm_cc2_x+10, nm_cc_y+10], fill=yellow, outline=black, width=2)
draw.text((nm_cc1_x, nm_cc_y-20), "cc", fill=black, font=small_font, anchor='mm')

# NMOS nselect标记
draw.rectangle([nm_active_x-20, nm_active_y-20, nm_active_x+280, nm_active_y+130], outline=green, width=2)
draw.text((nm_active_x-40, nm_active_y+70), "nselect", fill=green, font=small_font, anchor='mm')

# ===== 金属互连 =====
# vdd metal1 (粗灰色线)
draw.line([pm_cc1_x, pm_cc_y-10, pm_cc1_x, pm_cc_y-40], fill=gray, width=4)
draw.text((pm_cc1_x+20, pm_cc_y-35), "metal1", fill=gray, font=small_font)

# vss metal1
draw.line([nm_cc1_x, nm_cc_y+10, nm_cc1_x, nm_cc_y+40], fill=gray, width=4)

# 输出Y metal1 (连接PMOS和NMOS漏极)
draw.line([pm_cc2_x, pm_cc_y+10, pm_cc2_x, pm_cc_y+40], fill=gray, width=4)
draw.line([pm_cc2_x, pm_cc_y+40, pm_cc2_x, nm_cc_y-10], fill=gray, width=4)
draw.line([nm_cc2_x, nm_cc_y-10, nm_cc2_x, nm_cc_y-40], fill=gray, width=4)

# ===== 端口标注 =====
# vdd端口
draw.line([x_start+30, y_pm-20, x_start+30, pm_cc_y-50], fill=red, width=3)
draw.text((x_start+20, y_pm-25), "vdd端口", fill=red, font=small_font, anchor='mm')

# vss端口
draw.line([x_start+30, y_nm+130, x_start+30, nm_cc_y+50], fill=blue, width=3)
draw.text((x_start+20, y_nm+135), "vss端口", fill=blue, font=small_font, anchor='mm')

# 输入A端口 (左侧栅极)
draw.line([x_start-30, pm_poly_x-60, pm_poly_x-20, pm_poly_x], fill=green, width=3)
draw.text((x_start-40, pm_poly_x-70), "A端口", fill=green, font=small_font, anchor='mm')

# 输出Y端口 (右侧)
draw.line([x_start+530, pm_cc2_x, x_start+560, pm_cc2_x], fill=green, width=3)
draw.text((x_start+570, pm_cc2_x), "Y端口", fill=green, font=small_font, anchor='mm')

# ===== 图例 =====
legend_y = 600
draw.rectangle([50, legend_y, 200, legend_y+80], outline=black, width=2)
draw.text((125, legend_y+10), "图例", fill=black, font=normal_font, anchor='mm')

# nwell
draw.rectangle([60, legend_y+25, 90, legend_y+40], fill=light_red, outline=red, width=2)
draw.text([100, legend_y+30], "nwell", fill=black, font=small_font)

# active
draw.rectangle([60, legend_y+45, 90, legend_y+60], fill=light_green, outline=green, width=2)
draw.text([100, legend_y+50], "active", fill=black, font=small_font)

# poly
draw.rectangle([60, legend_y+65, 90, legend_y+80], fill=light_blue, outline=blue, width=2)
draw.text([100, legend_y+70], "poly", fill=black, font=small_font)

# ===== 尺寸标注 =====
# PMOS尺寸
draw.line([pm_active_x-30, pm_active_y, pm_active_x-30, pm_active_y+100], fill=black, width=1)
draw.text([pm_active_x-50, pm_active_y+50], "100", fill=black, font=small_font, anchor='mm')

# NMOS尺寸
draw.line([nm_active_x-30, nm_active_y, nm_active_x-30, nm_active_y+90], fill=black, width=1)
draw.text([nm_active_x-50, nm_active_y+45], "90", fill=black, font=small_font, anchor='mm')

# 保存图片
output_path = '/home/ubuntu/.openclaw/workspace/CMOS_Inverter_Design/cmos_inverter_layout.png'
img.save(output_path, 'PNG')
print(f"✓ CMOS反相器版图已生成：{output_path}")
