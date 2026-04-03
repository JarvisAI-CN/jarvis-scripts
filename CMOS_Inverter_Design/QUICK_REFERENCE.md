# CMOS反相器设计 - 快速参考

**学号：** 20232107111 | **姓名：** 李文馨

---

## 设计规格速查

### 晶体管参数
```
PMOS (p18):
  W = 1.0 μm
  L = 180 nm
  m = 1

NMOS (n18):
  W = 0.6 μm
  L = 180 nm
  m = 1
```

### 端口定义
```
A   - Input    (输入)
Y   - Output   (输出)
vdd - InputOutput (1.8V)
vss - InputOutput (0V)
```

---

## 原理图结构

```
      vdd (1.8V)
       |
      ┌┐
  ┌───┤ │PMOS
  │   │ │ W=1u, L=180n
A │┌──┤├┐
  ││  └┘│
  │└─┬─┘│
    │   │
    ├───┤─── Y (输出)
    │   │
  ┌─┴┐ ┌┴┐
  │  │ │ │NMOS
  │  └┬┘ │ W=600n, L=180n
  │   │  │
  └───┴──┘
      |
     vss (0V)
```

---

## 版图层叠结构

### PMOS部分 (上方)
```
层名          功能            尺寸/位置
─────────────────────────────────────
nwell         PMOS阱          3.0×2.0 μm
active       有源区          2.0×1.0 μm
pselect      P+注入          包围active
poly         栅极            0.18×1.4 μm
cc           接触孔          0.22×0.22 μm
metal1       第一层金属      0.3 μm宽
via1         通孔1           0.2×0.2 μm
metal2       第二层金属      0.4 μm宽
```

### NMOS部分 (下方)
```
层名          功能            尺寸/位置
─────────────────────────────────────
active       有源区          1.5×1.0 μm
nselect      N+注入          包围active
poly         栅极            0.18×1.4 μm
cc           接触孔          0.22×0.22 μm
metal1       第一层金属      0.3 μm宽
metal2       第二层金属      0.4 μm宽
```

---

## Cadence Virtuoso 快捷键

### 常用操作
```
i        - 添加元件/实例
w        - 绘制连线
p        - 添加引脚
r        - 绘制矩形
k        - 拉伸/编辑
c        - 复制
m        - 移动
Delete   - 删除选中
Ctrl+w   - 保存并检查
F        - 适合窗口显示
Shift+F  - 全屏显示选中
Ctrl+z   - 撤销
Shift+z  - 重做
```

### 层显示控制
```
Shift+F  - 显示所有层
Ctrl+F   - 隐藏未选中层
Enter    - 刷新显示
```

### 验证操作
```
Verify → DRC    - 运行设计规则检查
Verify → LVS    - 运行版图原理图对照
Verify → PEX    - 运行寄生提取
```

---

## 验证命令

### 在CIW窗口中执行

#### 运行DRC
```
Verify → DRC
→ 点击 OK
→ 等待完成
→ 查看结果窗口
```

#### 运行LVS
```
Verify → LVS
→ 确认schematic和layout路径
→ 点击 Run
→ 等待完成
→ 查看结果窗口
```

#### 查看LVS详细报告
```
在LVS窗口点击 "Output" 或 "Report"
→ 查看完整比对报告
→ 确认所有项显示笑脸
→ 确认最终结果为 CORRECT
```

---

## 常见错误速查

### DRC错误
| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| Minimum spacing violation | 线条间距太小 | 增加间距到≥0.3μm |
| Minimum width violation | 线条宽度太小 | 增加宽度到最小值 |
| Enclosure violation | 包围不足 | 增加重叠到≥0.09μm |
| Not inside well | PMOS未在nwell中 | 移动PMOS到nwell内 |

### LVS错误
| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| Port mismatch | 端口名称/类型不一致 | 检查原理图和版图端口 |
| Device count mismatch | 器件数量不对 | 检查是否所有器件都被识别 |
| Parameter mismatch | 器件参数不匹配 | 检查W/L值是否一致 |
| Net mismatch | 网络连接不一致 | 检查连线是否正确 |

---

## 设计规则（180nm工艺）

### 最小尺寸
```
栅长 (L):          180 nm
栅宽 (W):          220 nm
金属1宽度:         0.3 μm
金属1间距:         0.3 μm
接触孔尺寸:        0.22 μm
通孔1尺寸:         0.2 μm
多晶间距:          0.22 μm
有源区间距:        0.3 μm
```

### 重叠规则
```
接触孔包围:        ≥0.05 μm
阱包围有源区:      ≥0.3 μm
注入包围有源区:    ≥0.3 μm
多晶超越有源区:    ≥0.2 μm
```

---

## SKILL脚本使用

### 加载脚本
```skill
; 在CIW窗口中输入：
load("create_schematic.il")      ; 加载原理图生成脚本
load("create_layout.il")         ; 加载版图生成脚本
load("verification.il")          ; 加载验证脚本
```

### 运行函数
```skill
; 生成原理图
CMOSInverterSchematic()

; 生成版图
CMOSInverterLayout()

; 运行DRC
RunDRC()

; 运行LVS
RunLVS()

; 显示检查清单
DesignCheckList()

; 生成报告
GenerateReport()
```

---

## 验证结果标准

### DRC预期结果
```
✓ 仅显示 PD_XX 类警告
✓ PD (Permissible Deviation) 是允许的偏差
✓ 无其他类型错误
```

### LVS预期结果
```
==================================================================
                    LVS VERIFICATION RESULT
==================================================================

DEVICE COMPARISON:        CORRECT  😊
  PMOS:                   1        😊
  NMOS:                   1        😊

PORT COMPARISON:          CORRECT  😊
  A (input):              MATCHED  😊
  Y (output):             MATCHED  😊
  vdd (inputOutput):      MATCHED  😊
  vss (inputOutput):      MATCHED  😊

FINAL RESULT:             CORRECT  😊😊😊

==================================================================
```

---

## 文件清单

### 设计文件
```
20232107111李文馨/
├── inv/
│   ├── schematic        (原理图)
│   └── layout           (版图)
└── tech                 (工艺文件)
```

### 交付文件
```
CMOS_Inverter_Design/
├── README.md             (完整说明文档)
├── STEP_BY_STEP.md       (详细步骤文档)
├── create_schematic.il   (原理图生成脚本)
├── create_layout.il      (版图生成脚本)
├── verification.il       (验证脚本)
└── QUICK_REFERENCE.md    (本文档)
```

---

## 时间估算

| 任务 | 预计时间 |
|------|---------|
| 环境准备 | 5分钟 |
| 原理图设计 | 15分钟 |
| 版图设计 | 30-45分钟 |
| DRC验证 | 5分钟 |
| LVS验证 | 5分钟 |
| 截图准备 | 5分钟 |
| **总计** | **约1-1.5小时** |

---

**提示**：遇到问题时，先查看本文档的"常见错误速查"部分！
