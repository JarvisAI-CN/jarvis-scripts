"""
Python课程上机实验报告（一）
学院：信息学院
班级：数据科学与大数据技术2301班
学号：20232107111
姓名：李文馨
实验名称：熟悉Python编程环境和简单的Python程序
实验地点：13号机 302机房
指导教师：王芳
实验日期：2024年4月8日
"""

import math

# ========================================
# 题目1：计算圆的周长和面积
# ========================================
def circle_calculation():
    """
    输入圆的半径，计算并输出圆的周长和面积
    """
    print("\n" + "="*50)
    print("题目1：计算圆的周长和面积")
    print("="*50)

    try:
        radius = float(input("请输入圆的半径："))

        if radius <= 0:
            print("错误：半径必须为正数！")
            return

        # 计算周长和面积
        circumference = 2 * math.pi * radius
        area = math.pi * radius ** 2

        print(f"\n半径为 {radius} 的圆：")
        print(f"周长 = {circumference:.2f}")
        print(f"面积 = {area:.2f}")

    except ValueError:
        print("错误：请输入有效的数字！")


# ========================================
# 题目2：判断三位水仙花数
# ========================================
def narcissistic_number():
    """
    判断输入的三位数是否为水仙花数
    水仙花数：三位数abc = a³ + b³ + c³
    """
    print("\n" + "="*50)
    print("题目2：判断三位水仙花数")
    print("="*50)

    try:
        num = int(input("请输入一个三位数："))

        if num < 100 or num > 999:
            print("错误：请输入100-999之间的三位数！")
            return

        # 分解各位数字
        hundreds = num // 100        # 百位
        tens = (num // 10) % 10      # 十位
        units = num % 10             # 个位

        # 计算各位的立方和
        sum_of_cubes = hundreds ** 3 + tens ** 3 + units ** 3

        print(f"\n{num} 的各位数字：")
        print(f"百位：{hundreds}")
        print(f"十位：{tens}")
        print(f"个位：{units}")
        print(f"\n{hundreds}³ + {tens}³ + {units}³ = {sum_of_cubes}")

        if num == sum_of_cubes:
            print(f"\n✓ {num} 是水仙花数！")
        else:
            print(f"\n✗ {num} 不是水仙花数！")

    except ValueError:
        print("错误：请输入有效的整数！")


# ========================================
# 题目4：判断闰年
# ========================================
def leap_year():
    """
    判断输入的年份是否为闰年
    闰年规则：
    1. 能被4整除但不能被100整除，或者
    2. 能被400整除
    """
    print("\n" + "="*50)
    print("题目3：判断闰年")
    print("="*50)

    try:
        year = int(input("请输入年份："))

        if year < 1:
            print("错误：年份必须大于0！")
            return

        # 判断闰年
        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

        print(f"\n{year} 年：")
        if is_leap:
            print(f"✓ {year} 是闰年（366天）")
        else:
            print(f"✗ {year} 不是闰年（365天）")

        # 额外信息：显示二月天数
        if is_leap:
            print(f"   该年2月有29天")
        else:
            print(f"   该年2月有28天")

    except ValueError:
        print("错误：请输入有效的整数！")


# ========================================
# 主菜单
# ========================================
def main():
    print("\n" + "="*50)
    print("     Python上机实验 - 实验题目演示")
    print("="*50)

    while True:
        print("\n请选择要运行的题目：")
        print("1. 计算圆的周长和面积")
        print("2. 判断三位水仙花数")
        print("3. 判断闰年")
        print("0. 退出程序")

        choice = input("\n请输入选项（0-3）：").strip()

        if choice == '1':
            circle_calculation()
        elif choice == '2':
            narcissistic_number()
        elif choice == '3':
            leap_year()
        elif choice == '0':
            print("\n感谢使用！再见！")
            break
        else:
            print("\n错误：无效的选项，请重新输入！")


if __name__ == "__main__":
    main()
