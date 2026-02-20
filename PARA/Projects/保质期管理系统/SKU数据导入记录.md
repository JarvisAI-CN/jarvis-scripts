# 批量导入SKU数据

**日期**: 2026-02-20 18:00 GMT+8
**数据来源**: 123盘共享资源/sku文件001.csv
**导入方式**: 自动化脚本处理

---

## 📊 导入统计

**总计**: 420 个SKU
**分类**: 17 个

### 分类分布

| 分类 | SKU数量 |
|------|---------|
| SERVEWARE | 133 |
| GIFT PACKS | 75 |
| BAR SUPPLIES | 68 |
| PASTRIES FRESH & FROZEN FOOD | 42 |
| STORE VALUE CARD | 26 |
| CUPS & LIDS | 17 |
| DAIRY | 14 |
| WHOLE BEAN | 14 |
| PACKAGED FOOD | 12 |
| BAR COFFEE | 4 |
| READY TO DRINK | 4 |
| PACKAGED TEA | 3 |
| FESTIVAL FOOD | 2 |
| BREWING EQUIPMENT | 2 |
| COUPON | 2 |
| BLENDED BEVERAGE MIX | 1 |
| VIA | 1 |

---

## 📝 处理流程

1. 从123盘下载CSV文件
2. 转换列顺序：分类,SKU,商品名 → SKU,商品名,分类
3. 清空旧数据
4. 批量导入到products表
5. 生成分类统计

---

## ⚠️ 注意事项

- 所有数据已替换为新的420个SKU
- 未设置盘点频次（需要后续配置）
- 未映射到系统分类（使用原始分类名称）

---

## 下一步

1. 按实际需求设置盘点频次
2. 映射原始分类到系统分类
3. 配置过期提醒规则
