/*
 * Cadence SKILL脚本 - 自动生成CMOS反相器原理图
 * 工艺: 180nm
 * 学号: 20232107111
 * 姓名: 李文馨
 */

procedure( CMOSInverterSchematic()
    let((cv libName cellName pmos nmos vdd vss gnd)
        
        ; 设置库名和单元名
        libName = "20232107111李文馨"
        cellName = "inv"
        
        ; 创建或打开原理图
        when(!ddGetObj(libName cellName "schematic")
            ddCreateObj(libName "cell" cellName)
        )
        cv = ddGetObj(libName cellName "schematic")
        sch = schOpen(cv "w" nil)
        
        ; ===== 添加PMOS =====
        pmos = schCreateInst(
            sch           ; schematic
            "p18"         ; cell name (PMOS model)
            "I0"          ; instance name
            list(         ; parameters
                "W" 1.0u      ; 宽度 1微米
                "L" 180n      ; 长度 180纳米
                "m" 1         ; 并联数
            )
            1.5:2.0       ; 位置 (x:y)
            "R0"          ; 旋转角度 (0度)
        )
        
        ; ===== 添加NMOS =====
        nmos = schCreateInst(
            sch
            "n18"         ; cell name (NMOS model)
            "I1"          ; instance name
            list(
                "W" 600n      ; 宽度 600纳米
                "L" 180n      ; 长度 180纳米
                "m" 1
            )
            1.5:0.5       ; 位置 (在PMOS下方)
            "R0"
        )
        
        ; ===== 添加电源端口 =====
        vdd = schCreateWire(
            sch
            list(1.0:2.75 2.0:2.75)  ; PMOS源极上方
            "vdd!"                    ; 网络名
            "fullWidth"               ; 宽线
        )
        
        ; ===== 添加地端口 =====
        vss = schCreateWire(
            sch
            list(1.0:0.0 2.0:0.0)    ; NMOS源极下方
            "vss!"                    ; 网络名
            "fullWidth"
        )
        
        ; ===== 连接栅极（输入A）=====
        schCreateWire(
            sch
            list(1.0:1.5 0.5:1.5 0.5:2.25)  ; 从两管栅极向左引出
            "A"
            "fullWidth"
        )
        schCreateWire(
            sch
            list(0.5:2.25 0.5:0.75 1.0:0.75)  ; 连接到NMOS栅极
            "A"
            "fullWidth"
        )
        
        ; ===== 连接漏极（输出Y）=====
        schCreateWire(
            sch
            list(2.25:2.0 2.25:0.75 3.0:0.75)  ; 从两管漏极向右引出
            "Y"
            "fullWidth"
        )
        
        ; ===== 添加端口 =====
        ; vdd端口
        schCreatePin(
            sch
            "vdd"           ; 端口名
            "inputOutput"   ; 类型
            "vdd!"          ; 连接的网络
        )
        
        ; vss端口
        schCreatePin(
            sch
            "vss"
            "inputOutput"
            "vss!"
        )
        
        ; 输入端口A
        schCreatePin(
            sch
            "A"
            "input"
            "A"
        )
        
        ; 输出端口Y
        schCreatePin(
            sch
            "Y"
            "output"
            "Y"
        )
        
        ; 保存并检查
        schCheck(sch)
        
        ; 显示完成信息
        println("========================================")
        println("  CMOS反相器原理图生成完成！")
        println("  库名: " libName)
        println("  单元: " cellName)
        println("  PMOS: W=1u, L=180n")
        println("  NMOS: W=600n, L=180n")
        println("========================================")
        
        ; 返回schematic句柄
        sch
    )
)

; 执行函数
CMOSInverterSchematic()
