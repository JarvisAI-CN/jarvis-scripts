#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贾维斯每日汇报脚本 v2.1 (美化版)
汇总 OKX 全账户资产 + 昨日工作回顾
"""

import os
import json
import time
import datetime
import hmac
import base64
import requests
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

# --- 配置区 ---
OKX_CONFIG = {
    "api_key": "73b8a24a-232a-4df4-82d1-77b12e8b8e37",
    "secret": "BBDA511D164D3C088BDCCE96D4D4340B",
    "passphrase": "Fs123456."
}

EMAIL_CONFIG = {
    "host": "smtp.email.cn",
    "port": 465,
    "user": "jarvis.openclaw@email.cn",
    "password": "wjhwJyeGudeCRk2e",
    "to": "mipjc@111.com"
}

# 强制使用 IPv4
old_getaddrinfo = socket.getaddrinfo
def new_getaddrinfo(*args, **kwargs):
    responses = old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = new_getaddrinfo

def call_okx(request_path):
    url = "https://www.okx.com" + request_path
    timestamp = datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = "GET"
    sign_string = timestamp + method + request_path
    signature = base64.b64encode(hmac.new(OKX_CONFIG["secret"].encode('utf-8'), sign_string.encode('utf-8'), digestmod='sha256').digest()).decode('utf-8')
    headers = {
        "OK-ACCESS-KEY": OKX_CONFIG["api_key"],
        "OK-ACCESS-SIGN": signature,
        "OK-ACCESS-TIMESTAMP": timestamp,
        "OK-ACCESS-PASSPHRASE": OKX_CONFIG["passphrase"],
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {"code": "-1", "msg": str(e)}

def get_ticker(ccy):
    if ccy in ["USDT", "USDC"]: return 1.0
    res = call_okx(f"/api/v5/market/ticker?instId={ccy}-USDT")
    if res and res.get("code") == "0":
        return float(res["data"][0]["last"])
    return 0

def get_okx_full_assets():
    assets_raw = {}
    # 1. 交易账户
    res = call_okx("/api/v5/account/balance")
    if res and res.get("code") == "0":
        for d in res["data"][0]["details"]:
            assets_raw[d["ccy"]] = assets_raw.get(d["ccy"], 0) + float(d["eq"])
    # 2. 资金账户
    res = call_okx("/api/v5/asset/balances")
    if res and res.get("code") == "0":
        for d in res["data"]:
            assets_raw[d["ccy"]] = assets_raw.get(d["ccy"], 0) + float(d["bal"])
    # 3. 赚币/金融账户
    res = call_okx("/api/v5/finance/savings/balance")
    if res and res.get("code") == "0":
        for d in res["data"]:
            assets_raw[d["ccy"]] = assets_raw.get(d["ccy"], 0) + float(d["amt"])

    total_usdt = 0
    asset_list = []
    for ccy, amt in assets_raw.items():
        if amt <= 0: continue
        price = get_ticker(ccy)
        value = amt * price
        if value < 0.01: continue
        total_usdt += value
        asset_list.append({"ccy": ccy, "amt": amt, "price": price, "value": value})
    
    asset_list.sort(key=lambda x: x['value'], reverse=True)
    return total_usdt, asset_list

def get_yesterday_summary():
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    memory_file = f"/home/ubuntu/.openclaw/workspace/memory/{yesterday}.md"
    if os.path.exists(memory_file):
        with open(memory_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            summary = [line.strip() for line in lines if line.strip().startswith('- [') or line.strip().startswith('##')]
            return "\n".join(summary) if summary else "昨日无核心进度记录。"
    return "未找到昨日的 memory 文件。"

def generate_report_html(total_usdt, asset_list, summary):
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    yesterday_str = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    asset_rows = ""
    for a in asset_list:
        amt_str = f"{a['amt']:.8f}".rstrip('0').rstrip('.') if a['amt'] < 1 else f"{a['amt']:,g}"
        asset_rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #eee;"><strong>{a['ccy']}</strong></td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">{amt_str}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right;">${a['price']:.4f}</td>
            <td style="padding: 12px; border-bottom: 1px solid #eee; text-align: right; color: #2ecc71;"><strong>${a['value']:.2f}</strong></td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background-color: #f4f7f6; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #2c3e50, #34495e); color: #fff; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
            .header p {{ margin: 5px 0 0; opacity: 0.8; font-size: 14px; }}
            .content {{ padding: 30px; }}
            .summary-card {{ background: #f8f9fa; border-left: 5px solid #3498db; padding: 20px; margin-bottom: 30px; border-radius: 4px; }}
            .summary-card h2 {{ margin: 0 0 10px; font-size: 16px; color: #7f8c8d; text-transform: uppercase; }}
            .total-value {{ font-size: 32px; font-weight: bold; color: #2c3e50; }}
            .section-title {{ font-size: 18px; font-weight: bold; margin: 20px 0 15px; padding-bottom: 10px; border-bottom: 2px solid #3498db; color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th {{ text-align: left; background: #f8f9fa; padding: 12px; font-size: 14px; color: #7f8c8d; }}
            .work-log {{ background: #fff; border: 1px solid #eee; padding: 15px; border-radius: 4px; white-space: pre-wrap; font-size: 14px; color: #555; }}
            .footer {{ background: #f8f9fa; color: #95a5a6; text-align: center; padding: 20px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>JARVIS DAILY REPORT</h1>
                <p>{now_str}</p>
            </div>
            <div class="content">
                <div class="summary-card">
                    <h2>OKX 账户总资产估值</h2>
                    <div class="total-value">${total_usdt:.2f} <span style="font-size: 16px; color: #7f8c8d;">USDT</span></div>
                </div>

                <div class="section-title">⚡ 资产明细</div>
                <table>
                    <thead>
                        <tr>
                            <th>币种</th>
                            <th style="text-align: right;">持有数量</th>
                            <th style="text-align: right;">实时单价</th>
                            <th style="text-align: right;">估值 (USDT)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {asset_rows}
                    </tbody>
                </table>

                <div class="section-title">📝 昨日工作回顾 ({yesterday_str})</div>
                <div class="work-log">{summary}</div>
            </div>
            <div class="footer">
                此邮件由贾维斯自动化系统生成<br>
                OpenClaw Workspace | Secure AI Operations
            </div>
        </div>
    </body>
    </html>
    """
    return html

def send_email(html_body):
    subject = f"贾维斯每日汇报 - {datetime.datetime.now().strftime('%Y-%m-%d')}"
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['user']
        msg['To'] = EMAIL_CONFIG['to']
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        server = smtplib.SMTP_SSL(EMAIL_CONFIG['host'], EMAIL_CONFIG['port'])
        server.login(EMAIL_CONFIG['user'], EMAIL_CONFIG['password'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Send Error: {e}")
        return False

if __name__ == "__main__":
    total_eq, assets = get_okx_full_assets()
    summary_text = get_yesterday_summary()
    report_html = generate_report_html(total_eq, assets, summary_text)
    if send_email(report_html):
        print("✅ 视觉美化版每日汇报已成功发送至 " + EMAIL_CONFIG['to'])
