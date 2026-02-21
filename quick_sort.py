#!/usr/bin/env python3
"""
快速排序算法的简单实现
快速排序是一种分治算法，通过选择一个基准元素，将数组分为小于基准和大于基准的两部分，
然后递归地对这两部分进行排序。

平均时间复杂度: O(n log n)
空间复杂度: O(log n) (递归栈空间)
"""


def quick_sort(arr):
    """
    快速排序函数

    Args:
        arr (list): 需要排序的列表

    Returns:
        list: 排序后的列表
    """
    # 递归终止条件：如果数组为空或只有一个元素，直接返回
    if len(arr) <= 1:
        return arr
    
    # 选择基准元素（这里选择中间的元素，可以避免极端情况）
    pivot = arr[len(arr) // 2]
    
    # 将数组分为三部分：小于基准、等于基准、大于基准
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    # 递归调用快速排序并组合结果
    return quick_sort(left) + middle + quick_sort(right)


def main():
    """
    主函数，用于演示快速排序的使用
    """
    # 测试数据
    test_data = [
        [10, 7, 8, 9, 1, 5],
        [3, 6, 8, 10, 1, 2, 1],
        [5, 3, 8, 6, 4],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [],
        [1],
        [2, 1]
    ]
    
    print("快速排序算法演示")
    print("=" * 40)
    
    for i, data in enumerate(test_data, 1):
        print(f"\n测试 {i}: {data}")
        sorted_data = quick_sort(data.copy())
        print(f"排序后: {sorted_data}")
    
    print("\n" + "=" * 40)
    print("所有测试完成！")


if __name__ == "__main__":
    main()
