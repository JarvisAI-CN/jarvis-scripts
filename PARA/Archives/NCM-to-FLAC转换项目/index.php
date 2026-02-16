<?php
/**
 * NCM 转 FLAC 转换器 - 主页面
 * 现代化 UI 设计
 */
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCM 转 FLAC 无损转换器</title>
    <meta name="description" content="在线将网易云 NCM 格式转换为 FLAC 无损音频格式">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #333;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 480px;
            padding: 40px;
            animation: fadeIn 0.6s ease-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
        }

        h1 {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        .subtitle {
            color: #666;
            font-size: 0.95rem;
        }

        .upload-area {
            border: 3px dashed #d1d5db;
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f9fafb;
            position: relative;
            overflow: hidden;
        }

        .upload-area:hover {
            border-color: #667eea;
            background: #f3f4f6;
        }

        .upload-area.dragover {
            border-color: #667eea;
            background: #eef2ff;
            transform: scale(1.02);
        }

        .upload-icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #667eea;
        }

        .upload-text {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 8px;
        }

        .upload-hint {
            color: #9ca3af;
            font-size: 0.85rem;
        }

        input[type="file"] {
            display: none;
        }

        .file-info {
            margin-top: 20px;
            padding: 15px;
            background: #f0fdf4;
            border-radius: 12px;
            border: 1px solid #bbf7d0;
            display: none;
        }

        .file-info.active {
            display: block;
            animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .file-name {
            font-weight: 600;
            color: #166534;
            margin-bottom: 5px;
            word-break: break-all;
        }

        .file-size {
            color: #15803d;
            font-size: 0.9rem;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 32px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            margin-top: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px rgba(102, 126, 234, 0.4);
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn:disabled {
            background: #d1d5db;
            cursor: not-allowed;
            box-shadow: none;
            transform: none;
        }

        .btn-loading {
            position: relative;
            color: transparent;
        }

        .btn-loading::after {
            content: "";
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 12px;
            display: none;
            font-size: 0.95rem;
        }

        .message.active {
            display: block;
            animation: slideDown 0.3s ease-out;
        }

        .message.success {
            background: #f0fdf4;
            color: #166534;
            border: 1px solid #bbf7d0;
        }

        .message.error {
            background: #fef2f2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }

        .footer {
            margin-top: 30px;
            text-align: center;
            color: #9ca3af;
            font-size: 0.85rem;
            padding-top: 20px;
            border-top: 1px solid #f3f4f6;
        }

        .footer a {
            color: #667eea;
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        .features {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }

        .feature {
            background: #f3f4f6;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #6b7280;
        }

        .feature-icon {
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">🎵</div>
            <h1>NCM 转 FLAC</h1>
            <p class="subtitle">无损音频格式转换工具</p>
        </div>

        <form action="upload.php" method="post" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">☁️</div>
                <p class="upload-text" id="uploadText">点击选择或拖拽文件</p>
                <p class="upload-hint">支持 .ncm 格式，最大 50MB</p>
                <input type="file" name="ncm_file" id="fileInput" accept=".ncm" required>
            </div>

            <div class="file-info" id="fileInfo">
                <div class="file-name" id="fileName"></div>
                <div class="file-size" id="fileSize"></div>
            </div>

            <div class="message" id="message"></div>

            <button type="submit" class="btn" id="submitBtn">
                开始转换
            </button>
        </form>

        <div class="features">
            <div class="feature"><span class="feature-icon">✓</span>无损转换</div>
            <div class="feature"><span class="feature-icon">✓</span>保留元数据</div>
            <div class="feature"><span class="feature-icon">✓</span>完全本地</div>
        </div>

        <div class="footer">
            由 <a href="https://github.com/JarvisAI-CN" target="_blank">Jarvis AI</a> 驱动 ·
            仅限个人学习使用
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const submitBtn = document.getElementById('submitBtn');
        const message = document.getElementById('message');
        const uploadText = document.getElementById('uploadText');

        // 格式化文件大小
        function formatSize(bytes) {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        // 显示消息
        function showMessage(text, type) {
            message.textContent = text;
            message.className = 'message ' + type + ' active';
            setTimeout(() => {
                message.classList.remove('active');
            }, 5000);
        }

        // 文件选择处理
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                fileName.textContent = file.name;
                fileSize.textContent = formatSize(file.size);
                fileInfo.classList.add('active');
                uploadText.textContent = '点击更换文件';
            }
        });

        // 点击上传区域
        uploadArea.addEventListener('click', function() {
            fileInput.click();
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (!file.name.toLowerCase().endsWith('.ncm')) {
                    showMessage('仅支持 .ncm 格式文件', 'error');
                    return;
                }
                fileInput.files = files;
                fileName.textContent = file.name;
                fileSize.textContent = formatSize(file.size);
                fileInfo.classList.add('active');
                uploadText.textContent = '点击更换文件';
            }
        });

        // 表单提交
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (fileInput.files.length === 0) {
                showMessage('请先选择一个文件', 'error');
                return;
            }

            const formData = new FormData(this);
            submitBtn.classList.add('btn-loading');
            submitBtn.disabled = true;
            message.classList.remove('active');

            fetch('upload.php', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                
                if (data.success) {
                    showMessage('转换成功！正在下载...', 'success');
                    // 触发下载
                    window.location.href = data.downloadUrl;
                } else {
                    showMessage(data.message || '转换失败，请重试', 'error');
                }
            })
            .catch(error => {
                submitBtn.classList.remove('btn-loading');
                submitBtn.disabled = false;
                showMessage('服务器连接失败，请稍后重试', 'error');
                console.error('Error:', error);
            });
        });

        // 文件大小验证
        fileInput.addEventListener('change', function() {
            const maxSize = 50 * 1024 * 1024; // 50MB
            if (this.files.length > 0 && this.files[0].size > maxSize) {
                showMessage('文件大小超过 50MB 限制', 'error');
                fileInput.value = '';
                fileInfo.classList.remove('active');
            }
        });
    </script>
</body>
</html>
