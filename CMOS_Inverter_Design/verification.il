/*
 * Cadence SKILL脚本 - DRC和LVS验证
 * 工艺: 180nm
 * 学号: 20232107111
 * 姓名: 李文馨
 */

; ===== DRC验证函数 =====
procedure( RunDRC()
    let((libName cellName)
        libName = "20232107111李文馨"
        cellName = "inv"
        
        ; 获取版图
        cv = ddGetObj(libName cellName "layout")
        
        when(!cv
            error("无法找到版图视图: %s/%s/layout" libName cellName)
        )
        
        ; 打开版图
        lay = rodOpenCellViewByType(libName cellName "layout" "maskLayout" "r")
        
        ; 运行DRC
        ; 注意：实际运行需要配置DRC规则文件
        ; 这里提供模板代码
        
        println("========================================")
        println("  开始运行DRC验证...")
        println("========================================")
        
        ; 设置DRC参数（示例）
        drcRules = list(
            "minWidth"        0.18    ; 最小栅宽
            "minSpacing"      0.22    ; 最小间距
            "minEnclosure"    0.09    ; 最小包围
            "contactSize"     0.22    ; 接触孔尺寸
        )
        
        ; 实际DRC运行命令（需要在Virtuoso中执行）
        ; Verify → DRC → OK
        
        println("  DRC规则配置:")
        println("  - 最小宽度: 0.18 um")
        println("  - 最小间距: 0.22 um")
        println("  - 接触孔尺寸: 0.22 um")
        println("")
        println("  请在Virtuoso中执行:")
        println("  Verify → DRC → OK")
        println("")
        println("  预期结果:")
        println("  - 仅显示 PD_XX 类警告")
        println("  - 无其他错误")
        println("========================================")
        
        ; 返回
        t
    )
)

; ===== LVS验证函数 =====
procedure( RunLVS()
    let((libName cellName)
        libName = "20232107111李文馨"
        cellName = "inv"
        
        println("========================================")
        println("  开始运行LVS验证...")
        println("========================================")
        
        ; 检查原理图
        schCv = ddGetObj(libName cellName "schematic")
        when(!schCv
            error("无法找到原理图视图: %s/%s/schematic" libName cellName)
        )
        
        ; 检查版图
        layCv = ddGetObj(libName cellName "layout")
        when(!layCv
            error("无法找到版图视图: %s/%s/layout" libName cellName)
        )
        
        println("  原理图: ✓ 找到")
        println("  版图:   ✓ 找到")
        println("")
        println("  比对项:")
        println("  - 晶体管数量: PMOS x1, NMOS x1")
        println("  - 晶体管尺寸:")
        println("      PMOS: W=1u, L=180n")
        println("      NMOS: W=600n, L=180n")
        println("  - 端口连接:")
        println("      A:   Input")
        println("      Y:   Output")
        println("      vdd: InputOutput")
        println("      vss: InputOutput")
        println("")
        println("  请在Virtuoso中执行:")
        println("  Verify → LVS → Run")
        println("")
        println("  预期结果:")
        println("  - 所有项显示黄色笑脸 😊")
        println("  - 最终结果: CORRECT")
        println("========================================")
        
        ; 返回
        t
    )
)

; ===== 设计规则检查清单 =====
procedure( DesignCheckList()
    let(()
        
        println("========================================")
        println("  CMOS反相器设计检查清单")
        println("========================================")
        println("")
        
        println("【1. 晶体管参数】")
        println("  [ ] PMOS: W = 1.0 um, L = 180 nm")
        println("  [ ] NMOS: W = 0.6 um, L = 180 nm")
        println("  [ ] m = 1 (无并联)")
        println("")
        
        println("【2. 连接关系】")
        println("  [ ] PMOS源极 → vdd")
        println("  [ ] NMOS源极 → vss")
        println("  [ ] 两管栅极互连 → 输入A")
        println("  [ ] 两管漏极互连 → 输出Y")
        println("")
        
        println("【3. 版图层】")
        println("  [ ] nwell: PMOS阱区域")
        println("  [ ] active: PMOS和NMOS有源区")
        println("  [ ] pselect: PMOS注入")
        println("  [ ] nselect: NMOS注入")
        println("  [ ] poly: 栅极")
        println("  [ ] cc: 接触孔")
        println("  [ ] metal1: 第一层金属")
        println("  [ ] via1: 通孔1")
        println("  [ ] metal2: 第二层金属")
        println("")
        
        println("【4. 端口定义】")
        println("  [ ] vdd: InputOutput, 连接到metal2")
        println("  [ ] vss: InputOutput, 连接到metal2")
        println("  [ ] A:   Input,     连接到poly")
        println("  [ ] Y:   Output,    连接到metal1/metal2")
        println("")
        
        println("【5. 设计规则】")
        println("  [ ] 最小栅长: 180 nm")
        println("  [ ] 最小金属宽度: 0.3 um")
        println("  [ ] 最小金属间距: 0.3 um")
        println("  [ ] 接触孔尺寸: 0.22 um")
        println("  [ ] 针孔隔离: PMOS在nwell中")
        println("")
        
        println("【6. 验证结果】")
        println("  [ ] DRC通过 (仅PD_XX警告)")
        println("  [ ] LVS通过 (结果CORRECT)")
        println("  [ ] 器件匹配: PMOS x1, NMOS x1")
        println("  [ ] 端口匹配: A, Y, vdd, vss")
        println("")
        
        println("【7. 文档准备】")
        println("  [ ] 原理图截图")
        println("  [ ] 版图截图 (含标题栏)")
        println("  [ ] DRC结果截图")
        println("  [ ] LVS结果截图")
        println("")
        
        println("========================================")
        println("  检查完成！")
        println("  所有项目均满足要求后，可以提交。")
        println("========================================")
        
        t
    )
)

; ===== 生成验证报告 =====
procedure( GenerateReport()
    let((reportFile)
        
        reportFile =outfile("CMOS_Inverter_Report.txt")
        
        fprintf(reportFile "========================================\n")
        fprintf(reportFile "  CMOS反相器设计验证报告\n")
        fprintf(reportFile "========================================\n\n")
        
        fprintf(reportFile "学生信息:\n")
        fprintf(reportFile "  学号: 20232107111\n")
        fprintf(reportFile "  姓名: 李文馨\n\n")
        
        fprintf(reportFile "设计规格:\n")
        fprintf(reportFile "  工艺: 180nm CMOS\n")
        fprintf(reportFile "  单元: inv\n")
        fprintf(reportFile "  库: 20232107111李文馨\n\n")
        
        fprintf(reportFile "晶体管参数:\n")
        fprintf(reportFile "  PMOS: W=1.0um, L=0.18um, m=1\n")
        fprintf(reportFile "  NMOS: W=0.6um, L=0.18um, m=1\n\n")
        
        fprintf(reportFile "端口定义:\n")
        fprintf(reportFile "  A:   Input\n")
        fprintf(reportFile "  Y:   Output\n")
        fprintf(reportFile "  vdd: InputOutput (1.8V)\n")
        fprintf(reportFile "  vss: InputOutput (0V)\n\n")
        
        fprintf(reportFile "验证状态:\n")
        fprintf(reportFile "  [ ] DRC: 通过 (仅PD_XX警告)\n")
        fprintf(reportFile "  [ ] LVS: 通过 (CORRECT)\n\n")
        
        fprintf(reportFile "========================================\n")
        fprintf(reportFile "  报告生成时间: %s\n" getCurrentTime())
        fprintf(reportFile "========================================\n")
        
        close(reportFile)
        
        println("✓ 验证报告已生成: CMOS_Inverter_Report.txt")
        
        t
    )
)

; ===== 快捷命令 =====
println("")
println("========================================")
println("  CMOS反相器验证脚本加载完成！")
println("========================================")
println("")
println("可用命令:")
println("  RunDRC()           - 运行DRC验证")
println("  RunLVS()           - 运行LVS验证")
println("  DesignCheckList()  - 显示检查清单")
println("  GenerateReport()   - 生成验证报告")
println("")
println("使用示例:")
println("  在CIW中输入: RunDRC()")
println("========================================")
println("")
