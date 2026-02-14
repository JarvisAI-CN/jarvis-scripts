#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM转换器Web界面 - Flask应用
部署到宝塔面板

v1.0 功能:
- ✅ 文件上传
- ✅ NCM转FLAC转换
- ✅ 文件下载
- ✅ 进度显示
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
import tempfile
import uuid
from pathlib import Path

# 添加脚本路径
SCRIPT_DIR = '/home/ubuntu/.openclaw/workspace/scripts'
sys.path.insert(0, SCRIPT_DIR)

from ncm_converter_v3_1 import NCMDumpConverter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
app.config['UPLOAD_FOLDER'] = '/tmp/ncm_web_uploads'
app.config['OUTPUT_FOLDER'] = '/tmp/ncm_web_output'

# 确保目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

converter = NCMDumpConverter()

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NCM转FLAC转换器 v3.1</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            transition: all 0.3s;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
        }
        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
        }
        .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .upload-text {
            color: #555;
            font-size: 16px;
            margin-bottom: 10px;
        }
        .upload-hint {
            color: #999;
            font-size: 12px;
        }
        #fileInput {
            display: none;
        }
        .file-info {
            background: #f0f2ff;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: none;
        }
        .file-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .file-size {
            color: #666;
            font-size: 14px;
        }
        .convert-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: none;
        }
        .convert-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }
        .convert-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .progress {
            display: none;
            margin-top: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 4px;
            transition: width 0.3s;
            width: 0%;
        }
        .status {
            color: #666;
            font-size: 14px;
            text-align: center;
        }
        .result {
            display: none;
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            background: #f0f8ff;
            border: 2px solid #667eea;
        }
        .result.success {
            background: #f0fff4;
            border-color: #28a745;
        }
        .result.error {
            background: #fff5f5;
            border-color: #dc3545;
        }
        .result-title {
            font-weight: 600;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .download-btn {
            display: inline-block;
            padding: 12px 24px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            margin-top: 10px;
            transition: all 0.3s;
        }
        .download-btn:hover {
            background: #218838;
        }
        .info-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }
        .badge-success {
            background: #28a745;
            color: white;
        }
        .badge-error {
            background: #dc3545;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 NCM转FLAC转换器</h1>
        <p class="subtitle">v3.1 - 支持CTEN/CTCN格式，无损转换</p>

        <div class="upload-area" id="uploadArea">
            <div class="icon">📁</div>
            <div class="upload-text">点击或拖拽NCM文件到此处</div>
            <div class="upload-hint">支持最大500MB的文件</div>
        </div>

        <input type="file" id="fileInput" accept=".ncm">

        <div class="file-info" id="fileInfo">
            <div class="file-name" id="fileName"></div>
            <div class="file-size" id="fileSize"></div>
        </div>

        <button class="convert-btn" id="convertBtn">开始转换</button>

        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="status" id="status">准备转换...</div>
        </div>

        <div class="result" id="result">
            <div class="result-title" id="resultTitle"></div>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const convertBtn = document.getElementById('convertBtn');
        const progress = document.getElementById('progress');
        const progressFill = document.getElementById('progressFill');
        const status = document.getElementById('status');
        const result = document.getElementById('result');
        const resultTitle = document.getElementById('resultTitle');
        const resultContent = document.getElementById('resultContent');

        let selectedFile = null;

        // 点击上传
        uploadArea.addEventListener('click', () => fileInput.click());

        // 文件选择
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.toLowerCase().endsWith('.ncm')) {
                alert('请选择NCM文件！');
                return;
            }

            selectedFile = file;
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            fileInfo.style.display = 'block';
            convertBtn.style.display = 'block';
            result.style.display = 'none';
        }

        function formatFileSize(bytes) {
            if (bytes < 1024 * 1024) {
                return (bytes / 1024).toFixed(2) + ' KB';
            } else {
                return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
            }
        }

        // 转换按钮
        convertBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            const formData = new FormData();
            formData.append('file', selectedFile);

            progress.style.display = 'block';
            convertBtn.disabled = true;
            status.textContent = '上传中...';
            progressFill.style.width = '20%';

            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (data.success) {
                    progressFill.style.width = '100%';
                    status.textContent = '转换成功！';

                    result.classList.add('success');
                    result.classList.remove('error');
                    resultTitle.textContent = '✅ 转换成功';

                    resultContent.innerHTML = `
                        <p><strong>输出文件:</strong> ${data.filename}</p>
                        <p><strong>文件大小:</strong> ${formatFileSize(data.size)}</p>
                        <p><strong>格式:</strong> ${data.format}</p>
                        <a href="/download/${data.id}" class="download-btn">下载FLAC文件</a>
                    `;
                } else {
                    throw new Error(data.error || '转换失败');
                }
            } catch (error) {
                progressFill.style.width = '0%';
                status.textContent = '转换失败';

                result.classList.add('error');
                result.classList.remove('success');
                resultTitle.textContent = '❌ 转换失败';

                resultContent.innerHTML = `
                    <p>${error.message}</p>
                `;
            } finally {
                result.style.display = 'block';
                convertBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    """处理NCM文件转换"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未上传文件'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'success': False, 'error': '未选择文件'}), 400

        if not file.filename.lower().endswith('.ncm'):
            return jsonify({'success': False, 'error': '只支持NCM文件'}), 400

        # 生成唯一ID
        file_id = str(uuid.uuid4())

        # 保存上传文件
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}.ncm')
        file.save(upload_path)

        # 转换文件
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], file_id)
        os.makedirs(output_path, exist_ok=True)

        result_file = converter.convert_file(upload_path, output_path)

        if result_file:
            # 获取文件信息
            filename = os.path.basename(result_file)
            file_size = os.path.getsize(result_file)
            file_format = os.path.splitext(filename)[1][1:].upper()

            # 移动到输出目录
            final_path = os.path.join(output_path, filename)
            os.rename(result_file, final_path)

            return jsonify({
                'success': True,
                'id': file_id,
                'filename': filename,
                'size': file_size,
                'format': file_format
            })
        else:
            return jsonify({'success': False, 'error': '转换失败'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<file_id>')
def download(file_id):
    """下载转换后的文件"""
    try:
        output_dir = os.path.join(app.config['OUTPUT_FOLDER'], file_id)

        # 查找输出文件
        files = [f for f in os.listdir(output_dir) if not f.endswith('.ncm')]

        if files:
            file_path = os.path.join(output_dir, files[0])
            return send_file(file_path, as_attachment=True)
        else:
            return '文件不存在', 404

    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
