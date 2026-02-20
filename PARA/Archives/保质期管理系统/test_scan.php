<?php
// 扫码测试页面 - PHP版本
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>扫码测试工具</title>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        h1 { color: #333; }
        #reader {
            width: 100%;
            max-width: 400px;
            margin: 20px auto;
            border: 2px solid #ccc;
            border-radius: 10px;
            overflow: hidden;
        }
        #result {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 5px;
            font-size: 14px;
            line-height: 1.6;
        }
        .button-group {
            margin: 20px 0;
            text-align: center;
        }
        button {
            padding: 10px 20px;
            margin: 0 10px;
            font-size: 16px;
            cursor: pointer;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .success {
            background: #d4edda !important;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background: #f8d7da !important;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
    </style>
</head>
<body>
    <h1>📱 二维码扫码测试工具</h1>
    <p>使用此工具测试您的二维码是否能被正确识别</p>

    <div class="button-group">
        <button id="startBtn" onclick="startScan()">🎥 开始扫码</button>
        <button id="stopBtn" onclick="stopScan()" disabled>⏹️ 停止扫码</button>
    </div>

    <div id="reader"></div>

    <div id="result">
        <strong>等待扫码...</strong>
    </div>

    <script>
        let html5QrCode = null;

        function startScan() {
            const resultDiv = document.getElementById('result');
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');

            resultDiv.innerHTML = '<strong>正在启动摄像头...</strong>';
            resultDiv.className = '';

            html5QrCode = new Html5Qrcode("reader");

            html5QrCode.start(
                {facingMode: "environment"},
                {
                    fps: 10,
                    qrbox: {width: 250, height: 250}
                },
                (decodedText, decodedResult) => {
                    // 扫码成功
                    stopScan();

                    // 分析扫码内容
                    const isStarbucksURL = decodedText.includes('artwork.starbucks.com.cn');
                    const hasHash = decodedText.includes('#');
                    const length = decodedText.length;

                    let analysis = '<strong>✅ 扫码成功！</strong><br><br>';
                    analysis += '<strong>扫码内容:</strong><br>';
                    analysis += '<code style="word-break: break-all;">' + decodedText + '</code><br><br>';
                    analysis += '<strong>格式分析:</strong><br>';
                    analysis += '- 内容长度: ' + length + ' 字符<br>';
                    analysis += '- 包含星巴克URL: ' + (isStarbucksURL ? '✅ 是' : '❌ 否') + '<br>';
                    analysis += '- 包含 #: ' + (hasHash ? '✅ 是' : '❌ 否') + '<br><br>';

                    // 测试解析
                    if (isStarbucksURL) {
                        analysis += '<strong>识别格式:</strong> 🌟 星巴克官方URL格式<br>';
                    } else if (hasHash) {
                        analysis += '<strong>识别格式:</strong> 🔢 纯数字+日期格式<br>';
                    } else if (length === 8 && /^\d+$/.test(decodedText)) {
                        analysis += '<strong>识别格式:</strong> 📦 纯SKU格式（8位）<br>';
                    } else {
                        analysis += '<strong>识别格式:</strong> ❓ 未知格式<br>';
                    }

                    resultDiv.innerHTML = analysis;
                    resultDiv.className = 'success';
                },
                (errorMessage) => {
                    // 扫描中，忽略错误
                }
            ).then(() => {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            }).catch(err => {
                resultDiv.innerHTML = '<strong>❌ 启动失败:</strong><br>' + err;
                resultDiv.className = 'error';
            });
        }

        function stopScan() {
            if (html5QrCode) {
                html5QrCode.stop().then(() => {
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                }).catch(err => {
                    console.error('停止失败:', err);
                });
            }
        }
    </script>
</body>
</html>
