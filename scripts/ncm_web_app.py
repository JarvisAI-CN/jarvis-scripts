#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NCM转换器Web界面 - Flask应用 v2.1 (极速稳定版)
"""

from flask import Flask, render_template, request, send_from_directory, jsonify, make_response
import os
import sys
import uuid
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 环境配置
WORKSPACE = '/home/ubuntu/.openclaw/workspace'
UPLOAD_FOLDER = '/tmp/ncm_web_uploads'
OUTPUT_FOLDER = '/tmp/ncm_web_output'
LOG_DIR = os.path.join(WORKSPACE, 'logs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 导入转换器
sys.path.insert(0, os.path.join(WORKSPACE, 'scripts'))
from ncm_converter_v3_1 import NCMDumpConverter

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# 日志配置
handler = RotatingFileHandler(os.path.join(LOG_DIR, 'ncm_web_v2.log'), maxBytes=2000000, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

converter = NCMDumpConverter()
# 全局映射（简单内存存储）
name_cache = {}

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NCM 无损转换器</title>
    <style>
        body { font-family: system-ui; background: #f0f2f5; display: flex; justify-content: center; padding-top: 50px; }
        .card { background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 450px; text-align: center; }
        .drop-zone { border: 2px dashed #007bff; padding: 40px; border-radius: 12px; cursor: pointer; background: #f8fbff; }
        .drop-zone:hover { background: #eef6ff; }
        #file-info { margin: 20px 0; display: none; text-align: left; background: #f8f9fa; padding: 10px; border-radius: 8px; }
        .btn { background: #007bff; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; }
        .btn:disabled { background: #ccc; }
        #result { margin-top: 20px; display: none; }
        .download-link { display: block; background: #28a745; color: white; padding: 12px; border-radius: 8px; text-decoration: none; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎵 NCM 无损解密</h2>
        <p style="color: #666; font-size: 14px;">将网易云音乐加密格式转换为标准无损</p>
        <div class="drop-zone" id="drop-zone">点击上传 .ncm 文件</div>
        <input type="file" id="file-input" style="display:none" accept=".ncm">
        <div id="file-info">
            <div id="fn" style="font-weight: bold;"></div>
            <div id="fs" style="font-size: 12px; color: #888;"></div>
        </div>
        <button class="btn" id="start-btn" style="display:none">开始转换</button>
        <div id="result">
            <p>✅ 转换成功</p>
            <a id="dl-btn" class="download-link" href="#">立即下载</a>
        </div>
    </div>
    <script>
        const dz = document.getElementById('drop-zone');
        const fi = document.getElementById('file-input');
        const sb = document.getElementById('start-btn');
        let file = null;

        dz.onclick = () => fi.click();
        fi.onchange = (e) => {
            if(e.target.files.length) {
                file = e.target.files[0];
                document.getElementById('fn').innerText = file.name;
                document.getElementById('fs').innerText = (file.size/1024/1024).toFixed(2) + ' MB';
                document.getElementById('file-info').style.display = 'block';
                sb.style.display = 'block';
                document.getElementById('result').style.display = 'none';
            }
        };

        sb.onclick = async () => {
            sb.disabled = true;
            sb.innerText = '转换中...';
            const fd = new FormData();
            fd.append('file', file);
            try {
                const res = await fetch('/convert', { method: 'POST', body: fd });
                const data = await res.json();
                if(data.success) {
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('dl-btn').href = '/download/' + data.id;
                    sb.style.display = 'none';
                } else { alert('失败: ' + data.error); }
            } catch(e) { alert('网络错误'); }
            finally { sb.disabled = false; sb.innerText = '开始转换'; }
        };
    </script>
</body>
</html>
    '''

@app.route('/convert', methods=['POST'])
def convert():
    try:
        file = request.files.get('file')
        if not file: return jsonify({'success': False, 'error': 'No file'}), 400
        
        file_id = str(uuid.uuid4())
        name_cache[file_id] = file.filename
        
        input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.ncm")
        file.save(input_path)
        
        out_dir = os.path.join(OUTPUT_FOLDER, file_id)
        os.makedirs(out_dir, exist_ok=True)
        
        # 执行转换
        res_file = converter.convert_file(input_path, out_dir)
        
        if res_file and os.path.exists(res_file):
            app.logger.info(f"Success: {file_id} | {file.filename}")
            return jsonify({'success': True, 'id': file_id})
        else:
            return jsonify({'success': False, 'error': 'Convert failed'}), 500
            
    except Exception as e:
        app.logger.exception("Convert Error")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<file_id>')
def download(file_id):
    try:
        path_dir = os.path.join(OUTPUT_FOLDER, file_id)
        if not os.path.exists(path_dir):
            return "Not Found", 404
            
        files = [f for f in os.listdir(path_dir) if not f.endswith('.ncm')]
        if not files: return "Empty", 404
        
        filename = files[0]
        full_path = os.path.join(path_dir, filename)
        
        orig_name = name_cache.get(file_id, "music")
        # 确保下载文件名正确且安全
        dl_name = os.path.splitext(orig_name)[0] + os.path.splitext(filename)[1]
        
        app.logger.info(f"Downloading: {file_id} -> {dl_name} ({os.path.getsize(full_path)} bytes)")
        
        response = make_response(send_from_directory(path_dir, filename))
        # 强力下载头
        response.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{uuid.uuid4().hex[:8]}_{dl_name}"
        response.headers["Content-Type"] = "application/octet-stream"
        # 禁用缓存
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response

    except Exception as e:
        app.logger.exception("Download Error")
        return "Internal Error", 500

if __name__ == '__main__':
    # 改为 5001 端口
    app.run(host='0.0.0.0', port=5001)
