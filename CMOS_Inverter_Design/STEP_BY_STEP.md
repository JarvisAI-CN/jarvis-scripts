# CMOS反相器详细设计步骤

## 学号：20232107111 | 姓名：李文馨 | 工艺：180nm

---

## 第一步：环境准备

### 1.1 启动Cadence Virtuoso
```bash
# 终端中执行
virtuoso &
```

### 1.2 创建新库
1. 打开 **Library Manager**
   - 菜单：File → New → Library
   - Library Name: `20232107111李文馨`
   - 选择：Attach to an existing tech library
   - Technology: `tsmc18` (或其他180nm工艺)

### 1.3 验证库创建
```
Library Manager中应显示：
📁 20232107111李文馨
   📂 tech
```

---

## 第二步：原理图设计

### 2.1 创建原理图单元
1. 在Library Manager中：
   - 选中库：`20232107111李文馨`
   - File → New → Cell View
   - Cell Name: `inv`
   - View Name: `schematic`
   - Tool: `Composer-Schematic`
   - 点击 **OK**

### 2.2 打开Component面板
- 快捷键：**i** (Insert)
- 或菜单：Create → Instance

### 2.3 放置PMOS晶体管

#### 操作步骤：
1. 在Component面板中Browse，找到库中的 `p18` 符号
2. 点击编辑属性：
   ```
   W = 1u
   L = 180n
   m = 1
   ```
3. 在画布上方点击放置PMOS
4. 按 **Esc** 退出放置模式

#### 预期位置：
```
放置坐标大约：(1.5, 2.0)
```

### 2.4 放置NMOS晶体管

#### 操作步骤：
1. Component面板Browse，找到 `n18` 符号
2. 编辑属性：
   ```
   W = 600n
   L = 180n
   m = 1
   ```
3. 在PMOS下方点击放置NMOS

#### 预期位置：
```
放置坐标大约：(1.5, 0.5)
```

### 2.5 绘制连线

#### 连接顺序：
1. **vdd连线** (快捷键：**w** - Wire)
   - 从PMOS源极（上方）向上画线
   - 标注网络名：`vdd!` (快捷键：**l** - Label)

2. **vss连线**
   - 从NMOS源极（下方）向下画线
   - 标注网络名：`vss!`

3. **输入A连线**
   - 从两管栅极向左引出
   - 先向上连到PMOS栅极
   - 再向下连到NMOS栅极
   - 最后向左引出并标注：`A`

4. **输出Y连线**
   - 从两管漏极连接处向右引出
   - 标注：`Y`

### 2.6 添加端口

#### 操作步骤：
1. 添加Pin（快捷键：**p** 或 Create → Pin）
2. 按以下顺序添加：

| 端口名 | 类型 | 位置 |
|--------|------|------|
| vdd | InputOutput | PMOS源极上方连线 |
| vss | InputOutput | NMOS源极下方连线 |
| A | Input | 输入连线端点 |
| Y | Output | 输出连线端点 |

### 2.7 检查并保存
- 快捷键：**Ctrl + S** 或 **X** (Check and Save)
- 确保CIW窗口无错误信息
- 如有错误，根据提示修改

### 2.8 原理图完成检查
```
✓ 晶体管数量：2个 (PMOS x1, NMOS x1)
✓ 端口数量：4个 (vdd, vss, A, Y)
✓ 网络连接：正确
✓ 器件参数：W和L正确
✓ Check and Save：无错误
```

---

## 第三步：版图设计

### 3.1 创建版图视图
1. 在Library Manager中：
   - 选中单元 `inv`
   - File → New → Cell View
   - View Name: `layout`
   - Tool: `Virtuoso`
   - 点击 **OK**

### 3.2 设置显示选项
1. 菜单：Options → Display
2. 设置：
   ```
   Grid Controls: 
   - Minor Spacing: 0.005
   - Major Spacing: 0.05
   
   Enable Grid: ✓
   Snap to Grid: ✓
   ```

### 3.3 选择层
- 快捷键：Shift + F (显示所有层)
- 或者LSW (Layer Selection Window)中选择层

### 3.4 绘制PMOS版图（上方）

#### 步骤1：绘制nwell
1. LSW中选择 `nwell` 层
2. 快捷键：**r** (Rectangle)
3. 绘制矩形：
   ```
   左下角: (0.0, 1.0)
   右上角: (3.0, 3.0)
   尺寸: 3.0 um × 2.0 um
   ```

#### 步骤2：绘制active（有源区）
1. LSW中选择 `active` 层
2. 在nwell中心绘制：
   ```
   左下角: (0.5, 1.5)
   右上角: (2.5, 2.5)
   尺寸: 2.0 um × 1.0 um
   ```

#### 步骤3：绘制pselect（P+注入）
1. LSW中选择 `pselect` 层
2. 包围active层，有0.3um重叠：
   ```
   左下角: (0.2, 1.2)
   右上角: (2.8, 2.8)
   ```

#### 步骤4：绘制poly（栅极）
1. LSW中选择 `poly` 层
2. 垂直穿过active中心：
   ```
   左下角: (1.41, 1.3)
   右上角: (1.59, 2.7)
   宽度: 0.18 um
   X中心: 1.5 um
   ```

#### 步骤5：绘制接触孔 (cc)
1. LSW中选择 `cc` (contact) 层
2. PMOS源极接触：
   ```
   中心: (1.0, 2.0)
   尺寸: 0.22 um × 0.22 um
   ```
3. PMOS漏极接触：
   ```
   中心: (2.0, 2.0)
   尺寸: 0.22 um × 0.22 um
   ```

### 3.5 绘制NMOS版图（下方）

#### 步骤1：绘制active
1. LSW中选择 `active` 层
2. 在PMOS下方绘制：
   ```
   左下角: (0.5, 0.0)
   右上角: (2.0, 1.0)
   尺寸: 1.5 um × 1.0 um
   注意：宽度600nm需要足够空间放置接触
   ```

#### 步骤2：绘制nselect（N+注入）
1. LSW中选择 `nselect` 层
2. 包围active层：
   ```
   左下角: (0.2, -0.3)
   右上角: (2.3, 1.3)
   ```

#### 步骤3：绘制poly（栅极）
1. LSW中选择 `poly` 层
2. 与PMOS栅极对齐：
   ```
   左下角: (1.41, -0.2)
   右上角: (1.59, 1.2)
   X中心: 1.5 um (与PMOS对齐)
   ```

#### 步骤4：绘制接触孔 (cc)
1. LSW中选择 `cc` 层
2. NMOS源极接触：
   ```
   中心: (1.0, 0.5)
   尺寸: 0.22 um × 0.22 um
   ```
3. NMOS漏极接触：
   ```
   中心: (2.0, 0.5)
   尺寸: 0.22 um × 0.22 um
   ```

### 3.6 绘制金属1互连 (metal1)

#### vdd连线
1. LSW中选择 `metal1` 层
2. 水平连接PMOS源极接触：
   ```
   左下角: (0.5, 2.5)
   右上角: (2.5, 2.8)
   ```

#### vss连线
1. 垂直连接NMOS源极接触：
   ```
   左下角: (0.5, -0.3)
   右上角: (2.0, 0.0)
   ```

#### 输出Y连线
1. 垂直连接两管漏极接触：
   ```
   左下角: (1.8, 0.5)
   右上角: (2.5, 2.0)
   ```

### 3.7 绘制通孔1 (via1)

#### vdd via
1. LSW中选择 `via1` 层
2. 在vdd metal1上：
   ```
   中心: (1.0, 2.65)
   尺寸: 0.2 um × 0.2 um
   ```

#### vss via
1. 在vss metal1上：
   ```
   中心: (1.0, -0.15)
   尺寸: 0.2 um × 0.2 um
   ```

### 3.8 绘制金属2 (metal2)

#### vdd metal2
1. LSW中选择 `metal2` 层
2. 顶部水平走线：
   ```
   左下角: (0.0, 2.8)
   右上角: (3.0, 3.2)
   宽度: 0.4 um
   ```

#### vss metal2
1. 底部水平走线：
   ```
   左下角: (0.0, -0.5)
   右上角: (3.0, -0.1)
   宽度: 0.4 um
   ```

#### 输出Y metal2
1. 右侧垂直走线：
   ```
   左下角: (2.5, 0.5)
   右上角: (3.2, 2.0)
   宽度: 0.7 um
   ```

### 3.9 添加端口 (Pins)

#### 添加vdd端口
1. Create → Pin (或快捷键：**p**)
2. 设置：
   ```
   Terminal Names: vdd
   Mode: Shape Pin
   I/O Type: inputOutput
   ```
3. 在vdd metal2上绘制矩形：
   ```
   左下角: (0.0, 2.8)
   右上角: (3.0, 3.2)
   ```

#### 添加vss端口
1. 同样方式创建vss pin
2. 在vss metal2上绘制

#### 添加A端口（输入）
1. Create → Pin
2. 设置：
   ```
   Terminal Names: A
   I/O Type: input
   ```
3. 在poly栅极左侧绘制：
   ```
   左下角: (0.0, 1.0)
   右上角: (0.3, 2.0)
   ```

#### 添加Y端口（输出）
1. Create → Pin
2. 设置：
   ```
   Terminal Names: Y
   I/O Type: output
   ```
3. 在Y metal2上绘制：
   ```
   左下角: (2.5, 0.5)
   右上角: (3.2, 2.0)
   ```

### 3.10 设置标题
1. 选中版图
2. Edit → Properties
3. 设置Title显示库路径：
   ```
   20232107111李文馨/inv/layout
   ```

### 3.11 保存版图
- 快捷键：**Ctrl + S**
- 或 File → Save

---

## 第四步：DRC验证

### 4.1 打开DRC窗口
1. 菜单：Verify → DRC
2. 弹出DRC Form

### 4.2 配置DRC参数
```
DRC Form设置:
- Switch Name: 选择标准180nm规则
- Commands: 保持默认
- 点击 "OK" 运行
```

### 4.3 查看DRC结果
1. DRC运行后自动弹出结果窗口
2. **预期结果**：
   ```
   ✓ 仅显示 PD_XX 类警告
   ✓ 无其他错误信息
   ```
   
3. **PD类警告说明**：
   - PD (Permissible Deviation) = 允许的偏差
   - 通常是由于最小尺寸的舍入误差
   - 不影响电路功能

### 4.4 处理DRC错误（如果有）
如果出现非PD类错误：
1. 点击错误条目
2. 版图会自动定位到错误位置
3. 根据错误提示修改版图
4. 重新运行DRC

### 4.5 保存DRC结果截图
- 确保DRC窗口显示完整结果
- 截图保存

---

## 第五步：LVS验证

### 5.1 打开LVS窗口
1. 菜单：Verify → LVS
2. 弹出LVS Form

### 5.2 配置LVS参数
```
LVS Form设置:

【File】标签:
- Schematic: 20232107111李文馨 inv schematic
- Layout:    20232107111李文馨 inv layout
- Run:       选择 "LVS only" (不含寄生提取)

【NCSU】标签或其他:
- 根据工艺库配置保持默认

点击 "Run" 按钮
```

### 5.3 查看LVS结果
1. LVS运行完成后自动弹出结果窗口
2. **预期结果**：
   ```
   ✓ Netlists matched successfully
   ✓ 所有项显示黄色笑脸 😊
   ✓ 最终结果: CORRECT
   ```

### 5.4 LVS结果解读

#### 正确结果示例：
```
==================================================================
                    SIEMENS LVS REPORT
==================================================================

Circuit: 20232107111李文馨 inv schematic
Layout:  20232107111李文馨 inv layout

------------------------------------------------
DEVICE RECOGNITION SUMMARY
------------------------------------------------
Total Components:         2
  - MOSFETs:              2
    PMOS:                 1 😊
    NMOS:                 1 😊

------------------------------------------------
PORT COMPARISON
------------------------------------------------
Total Ports:              4
  A (input):              MATCHED 😊
  Y (output):             MATCHED 😊
  vdd (inputOutput):      MATCHED 😊
  vss (inputOutput):      MATCHED 😊

------------------------------------------------
NET COMPARISON
------------------------------------------------
Total Nets:               5
  Matched:                5 😊

------------------------------------------------
FINAL RESULT
------------------------------------------------
LVS COMPARISON:           CORRECT 😊

==================================================================
```

#### 常见错误：
- **Device Mismatch**: 检查晶体管W和L参数
- **Port Mismatch**: 检查端口名称和类型
- **Connection Mismatch**: 检查网络连接

### 5.6 保存LVS结果截图
- 确保所有笑脸显示
- 显示 "CORRECT" 结果
- 截图保存

---

## 第六步：交付物准备

### 6.1 截图清单

#### 截图1：原理图
```
内容要求:
✓ 完整的晶体管符号
✓ 所有连线清晰
✓ 4个端口可见
✓ 显示器件参数 (W, L)
```

#### 截图2：版图
```
内容要求:
✓ 所有层可见
✓ 标题栏显示：
   - 库名：20232107111李文馨
   - Cell名：inv
   - View：layout
✓ 4个端口标注清晰
```

#### 截图3：DRC+LVS验证结果
```
可以分两张或合并：

DRC部分:
✓ 仅显示PD_XX类结果
✓ 无其他错误

LVS部分:
✓ 所有项显示黄色笑脸
✓ 最终结果：CORRECT
```

### 6.2 设计说明文档

包含以下内容：
1. 设计规格（工艺、参数）
2. 原理图说明
3. 版图说明
4. 验证结果

---

## 第七步：常见问题解决

### 问题1：DRC显示间距错误
**错误信息**：`Spacing violation: metal1 spacing < 0.3`
**解决方案**：
```
- 检查metal1宽度，确保 ≥ 0.3 um
- 增加金属线之间的间距
- 使用stretch工具 (快捷键：k) 调整
```

### 问题2：LVS显示端口不匹配
**错误信息**：`Port mismatch: schematic has 'A', layout has 'IN'`
**解决方案**：
```
1. 检查原理图端口名称 (在schematic中)
2. 检查版图pin名称 (在layout中)
3. 确保完全匹配 (区分大小写)
4. 检查端口类型 (Input/Output/InputOutput)
```

### 问题3：LVS显示器件数量不匹配
**错误信息**：`Device count mismatch: schematic 2, layout 1`
**解决方案**：
```
1. 检查版图是否识别出两个晶体管
2. Verify → Markers → Delete All 删除旧标记
3. Verify → Extract 提取版图器件
4. 重新运行LVS
```

### 问题4：接触孔未连接
**DRC错误**：`Contact not fully enclosed`
**解决方案**：
```
- 确保contact完全被metal和active包围
- 重叠至少0.05 um
- 检查LSW中是否选择了正确的层
```

---

## 完成检查清单

### 原理图
- [ ] PMOS: W=1u, L=180n, m=1
- [ ] NMOS: W=600n, L=180n, m=1
- [ ] PMOS源极接vdd
- [ ] NMOS源极接vss
- [ ] 两管栅极连为输入A
- [ ] 两管漏极连为输出Y
- [ ] 4个端口类型正确
- [ ] Check and Save无错误

### 版图
- [ ] PMOS在nwell中
- [ ] 所有层绘制完整
- [ ] 金属宽度≥0.3um
- [ ] 接触孔尺寸0.22um
- [ ] 4个端口引出
- [ ] 标题栏显示正确

### 验证
- [ ] DRC通过 (仅PD_XX)
- [ ] LVS通过 (CORRECT)
- [ ] 器件匹配 (PMOS x1, NMOS x1)
- [ ] 端口匹配 (A, Y, vdd, vss)

### 交付物
- [ ] 原理图截图
- [ ] 版图截图
- [ ] DRC结果截图
- [ ] LVS结果截图
- [ ] 设计说明文档

---

**设计完成后，所有项目都打勾 ✓ 即可提交！**
