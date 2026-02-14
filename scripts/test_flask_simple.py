#!/usr/bin/env python3
"""简单的Flask测试应用"""
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return "Test Index - GET works"

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        return jsonify({"message": "POST works", "method": "POST"})
    else:
        return jsonify({"message": "GET works", "method": "GET"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=False)
