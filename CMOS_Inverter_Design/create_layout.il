/*
 * Cadence SKILL脚本 - 自动生成CMOS反相器版图
 * 工艺: 180nm
 * 学号: 20232107111
 * 姓名: 李文馨
 */

procedure( CMOSInverterLayout()
    let((libName cellName cv tech)
        
        ; 设置库名和单元名
        libName = "20232107111李文馨"
        cellName = "inv"
        
        ; 获取工艺文件
        tech = ddGetObj(libName "tech")
        
        ; 创建或打开版图
        when(!ddGetObj(libName cellName "layout")
            ddCreateObj(libName "cell" cellName)
        )
        cv = ddGetObj(libName cellName "layout")
        lay = rodOpenCellViewByType(libName cellName "layout" "maskLayout" "w")
        
        ; ===== 技术参数 =====
        minGrid = 0.005           ; 最小栅格 (单位: 微米)
        gateLength = 0.18         ; 栅长 (180nm)
        gateWidthPMOS = 1.0       ; PMOS栅宽
        gateWidthNMOS = 0.6       ; NMOS栅宽
        minMetalWidth = 0.3       ; 最小金属宽度
        contactSize = 0.22        ; 接触孔尺寸
        
        ; ===== PMOS部分 (上方) =====
        ; 1. nwell (PMOS阱)
        rodCreateRect(
            lay
            list("nwell" "drawing")           ; 层:用途
            list(0.0:1.0)                      ; 左下角
            list(3.0:3.0)                      ; 右上角
        )
        
        ; 2. active (有源区) - PMOS
        rodCreateRect(
            lay
            list("active" "drawing")
            list(0.5:1.5)
            list(2.5:2.5)
        )
        
        ; 3. pselect (P+注入)
        rodCreateRect(
            lay
            list("pselect" "drawing")
            list(0.2:1.2)
            list(2.8:2.8)
        )
        
        ; 4. poly (栅极) - PMOS
        rodCreateRect(
            lay
            list("poly" "drawing")
            list(1.41:1.3)                     ; x=1.5-0.18/2
            list(1.59:2.7)                     ; x=1.5+0.18/2
        )
        
        ; 5. cc (接触孔) - PMOS源极
        rodCreateRect(
            lay
            list("cc" "drawing")
            list(1.0 - contactSize/2:2.0 - contactSize/2)
            list(1.0 + contactSize/2:2.0 + contactSize/2)
        )
        
        ; 6. cc (接触孔) - PMOS漏极
        rodCreateRect(
            lay
            list("cc" "drawing")
            list(2.0 - contactSize/2:2.0 - contactSize/2)
            list(2.0 + contactSize/2:2.0 + contactSize/2)
        )
        
        ; ===== NMOS部分 (下方) =====
        ; 1. active (有源区) - NMOS
        rodCreateRect(
            lay
            list("active" "drawing")
            list(0.5:0.0)
            list(2.0:1.0)
        )
        
        ; 2. nselect (N+注入)
        rodCreateRect(
            lay
            list("nselect" "drawing")
            list(0.2:-0.3)
            list(2.3:1.3)
        )
        
        ; 3. poly (栅极) - NMOS (与PMOS对齐)
        rodCreateRect(
            lay
            list("poly" "drawing")
            list(1.41:-0.2)
            list(1.59:1.2)
        )
        
        ; 4. cc (接触孔) - NMOS源极
        rodCreateRect(
            lay
            list("cc" "drawing")
            list(1.0 - contactSize/2:0.5 - contactSize/2)
            list(1.0 + contactSize/2:0.5 + contactSize/2)
        )
        
        ; 5. cc (接触孔) - NMOS漏极
        rodCreateRect(
            lay
            list("cc" "drawing")
            list(2.0 - contactSize/2:0.5 - contactSize/2)
            list(2.0 + contactSize/2:0.5 + contactSize/2)
        )
        
        ; ===== 金属1互连 =====
        ; 1. metal1 - vdd连接
        rodCreateRect(
            lay
            list("metal1" "drawing")
            list(0.5:2.5)
            list(2.5:2.8)
        )
        
        ; 2. metal1 - vss连接
        rodCreateRect(
            lay
            list("metal1" "drawing")
            list(0.5:-0.3)
            list(2.0:0.0)
        )
        
        ; 3. metal1 - 输出Y连接
        rodCreateRect(
            lay
            list("metal1" "drawing")
            list(1.8:0.5)
            list(2.5:2.0)
        )
        
        ; ===== via1 (通孔1) =====
        ; vdd via
        rodCreateRect(
            lay
            list("via1" "drawing")
            list(1.0 - 0.1:2.65 - 0.1)
            list(1.0 + 0.1:2.65 + 0.1)
        )
        
        ; vss via
        rodCreateRect(
            lay
            list("via1" "drawing")
            list(1.0 - 0.1:-0.15 - 0.1)
            list(1.0 + 0.1:-0.15 + 0.1)
        )
        
        ; ===== 金属2 (电源和地) =====
        ; 1. metal2 - vdd
        rodCreateRect(
            lay
            list("metal2" "drawing")
            list(0.0:2.8)
            list(3.0:3.2)
        )
        
        ; 2. metal2 - vss
        rodCreateRect(
            lay
            list("metal2" "drawing")
            list(0.0:-0.5)
            list(3.0:-0.1)
        )
        
        ; 3. metal2 - 输出Y
        rodCreateRect(
            lay
            list("metal2" "drawing")
            list(2.5:0.5)
            list(3.2:2.0)
        )
        
        ; ===== 添加引脚 =====
        ; vdd pin
        rodCreateRect(
            lay
            list("metal2" "pin")
            list(0.0:2.8)
            list(3.0:3.2)
        )
        schCreatePin(lay "vdd" "inputOutput")
        
        ; vss pin
        rodCreateRect(
            lay
            list("metal2" "pin")
            list(0.0:-0.5)
            list(3.0:-0.1)
        )
        schCreatePin(lay "vss" "inputOutput")
        
        ; A pin (输入)
        rodCreateRect(
            lay
            list("poly" "pin")
            list(0.0:1.0)
            list(0.3:2.0)
        )
        schCreatePin(lay "A" "input")
        
        ; Y pin (输出)
        rodCreateRect(
            lay
            list("metal2" "pin")
            list(2.5:0.5)
            list(3.2:2.0)
        )
        schCreatePin(lay "Y" "output")
        
        ; 设置显示标题
        lay~>title = strcat(libName "/inv/layout")
        
        ; 保存版图
        rodCloseCellView(lay)
        
        ; 显示完成信息
        println("========================================")
        println("  CMOS反相器版图生成完成！")
        println("  库名: " libName)
        println("  单元: " cellName)
        println("  工艺: 180nm CMOS")
        println("  PMOS: 1.0um / 0.18um")
        println("  NMOS: 0.6um / 0.18um")
        println("========================================")
        
        ; 返回layout句柄
        lay
    )
)

; 执行函数
CMOSInverterLayout()
