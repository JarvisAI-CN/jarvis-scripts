#!/bin/bash
# NCM转换测试脚本 - 使用nc-dump

echo "============================================================"
echo "🎵 NCM音乐格式转换测试（使用nc-dump）"
echo "============================================================"
echo ""

# 检查nc-dump是否已安装
if ! command -v ncm-dump &> /dev/null
then
    echo "⚠️  nc-dump 未安装"
    echo "📥 正在安装..."
    
    # 尝试使用pipx安装（推荐的系统级Python包安装方式）
    if command -v pipx &> /dev/null
    then
        echo "📦 使用pipx安装..."
        pipx install ncm-dump
    else
        echo "📦 使用pip3 --user安装..."
        pip3 install --user ncm-dump
        
        # 添加到PATH（如果需要）
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    echo ""
fi

# 再次检查
if command -v ncm-dump &> /dev/null
then
    echo "✅ nc-dump 已安装"
    echo ""
    
    # 设置文件路径
    NCM_FILE="/home/ubuntu/music_test/梓渝 - 萤火星球.ncm"
    OUTPUT_DIR="/home/ubuntu/music_test/converted"
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR"
    
    # 检查NCM文件
    if [ -f "$NCM_FILE" ]; then
        echo "📂 找到NCM文件: $NCM_FILE"
        echo ""
        
        # 执行转换
        echo "🔄 开始转换..."
        ncm-dump -i "$NCM_FILE" -o "$OUTPUT_DIR"
        
        # 检查转换结果
        if [ $? -eq 0 ]; then
            echo ""
            echo "============================================================"
            echo "✅ 转换成功！"
            echo "============================================================"
            echo ""
            
            # 列出输出文件
            echo "📂 转换后的文件:"
            ls -lh "$OUTPUT_DIR"
            echo ""
            
            # 检测输出格式
            OUTPUT_FILE=$(find "$OUTPUT_DIR" -type f \( -name "*.mp3" -o -name "*.flac" \) | head -1)
            if [ -n "$OUTPUT_FILE" ]; then
                echo "🎵 主输出文件: $OUTPUT_FILE"
                echo "📊 文件信息:"
                file "$OUTPUT_FILE"
                echo ""
                
                # 播放测试（如果有vlc）
                if command -v vlc &> /dev/null; then
                    echo "💡 可以使用以下命令播放:"
                    echo "   vlc \"$OUTPUT_FILE\""
                fi
            else
                echo "⚠️  未找到输出文件（mp3/flac）"
            fi
        else
            echo ""
            echo "============================================================"
            echo "❌ 转换失败"
            echo "============================================================"
            echo ""
            echo "💡 可能的原因:"
            echo "   - NCM文件格式已更新（加密算法变化）"
            echo "   - nc-dump版本过旧"
            echo "   - 文件损坏"
            echo ""
            echo "🔧 解决方案:"
            echo "   1. 更新nc-dump: pipx upgrade ncm-dump"
            echo "   2. 使用在线工具: https://ncm.kwasu.cc/"
            echo "   3. 尝试其他工具: ncm-dump (pip install ncm-dump)"
        fi
    else
        echo "❌ NCM文件不存在: $NCM_FILE"
        echo ""
        echo "💡 请检查文件路径:"
        ls -lh /home/ubuntu/music_test/
    fi
else
    echo "❌ nc-dump 安装失败"
    echo ""
    echo "🔧 尝试其他方案:"
    echo ""
    echo "方案1: 在线转换工具（推荐）"
    echo "   访问: https://ncm.kwasu.cc/"
    echo "   上传NCM文件并等待转换"
    echo ""
    echo "方案2: 在浏览器中测试"
    echo "   启动Chrome并访问转换网站"
    echo ""
    echo "方案3: 使用ncm-dump（注意拼写不同）"
    echo "   pip3 install --break-system-packages pycryptodome"
    echo "   pip3 install --break-system-packages ncmdump"
    echo ""
fi

echo ""
echo "============================================================"
echo "📊 转换测试结束"
echo "============================================================"
