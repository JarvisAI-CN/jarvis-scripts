"""
测试程序 - 生成运行结果用于报告
"""
import math

print("="*50)
print("Python上机实验 - 运行结果演示")
print("="*50)

# 测试题目1：圆的计算
print("\n【题目1】计算圆的周长和面积")
print("-" * 50)
print("输入：半径 = 5.0")
radius = 5.0
circumference = 2 * math.pi * radius
area = math.pi * radius ** 2
print(f"输出：")
print(f"  周长 = {circumference:.2f}")
print(f"  面积 = {area:.2f}")

# 测试题目2：水仙花数
print("\n【题目2】判断三位水仙花数")
print("-" * 50)
test_numbers = [153, 370, 371, 407, 123, 456]
print("测试多个三位数：")
for num in test_numbers:
    hundreds = num // 100
    tens = (num // 10) % 10
    units = num % 10
    sum_of_cubes = hundreds ** 3 + tens ** 3 + units ** 3
    result = "✓ 水仙花数" if num == sum_of_cubes else "✗ 非水仙花数"
    print(f"  {num}: {result}")

# 测试题目3：闰年
print("\n【题目3】判断闰年")
print("-" * 50)
test_years = [2000, 2004, 2023, 2024, 1900, 2100]
print("测试多个年份：")
for year in test_years:
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    result = "✓ 闰年" if is_leap else "✗ 平年"
    print(f"  {year}: {result}")

print("\n" + "="*50)
print("程序运行结束")
print("="*50)
