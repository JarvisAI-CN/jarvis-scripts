#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网址导航网站自动维护脚本
http://dh.dhmip.cn
功能：定期检查导航链接有效性，生成维护报告
"""

import requests
from datetime import datetime
import json
import os

# 配置
SITE_URL = "http://dh.dhmip.cn"
CHECK_TIMEOUT = 10  # 10秒超时
USER_AGENT = "Mozilla/5.0 (compatible; JarvisBot/1.0; +https://jarvis.ai)"

# 维护日志
LOG_DIR = os.path.join(os.path.dirname(__file__), "日志")
LOG_FILE = os.path.join(LOG_DIR, "maintenance_log.json")

def check_url(url):
    """检查URL是否可访问"""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=CHECK_TIMEOUT, allow_redirects=True)
        return {
            'url': url,
            'status': 'ok' if response.status_code == 200 else f'http_{response.status_code}',
            'response_time': response.elapsed.total_seconds(),
            'status_code': response.status_code
        }
    except requests.Timeout:
        return {'url': url, 'status': 'timeout', 'error': 'Request timeout'}
    except requests.RequestException as e:
        return {'url': url, 'status': 'error', 'error': str(e)}

def load_links_to_check():
    """加载需要检查的链接列表（示例）"""
    # 实际使用时应该从 WordPress 数据库或 API 获取
    # 这里提供一个示例列表
    return [
        "https://www.notion.so",
        "https://khanmigo.ai",  # Khanmigo
        "https://www.perplexity.ai",  # Perplexity AI
        "https://chatgpt.com",
        "https://www claude.ai",
    ]

def generate_report(results):
    """生成维护报告"""
    total = len(results)
    ok = sum(1 for r in results if r['status'] == 'ok')
    errors = total - ok

    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total': total,
            'ok': ok,
            'errors': errors,
            'success_rate': f"{(ok/total*100):.1f}%" if total > 0 else "N/A"
        },
        'details': results
    }
    return report

def save_report(report):
    """保存报告到日志文件"""
    os.makedirs(LOG_DIR, exist_ok=True)

    # 读取历史记录
    history = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)

    # 添加新报告
    history.append(report)

    # 保留最近30次记录
    history = history[-30:]

    # 保存
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"✅ 报告已保存: {LOG_FILE}")

def print_report(report):
    """打印报告摘要"""
    print(f"\n{'='*50}")
    print(f"网址导航网站维护报告")
    print(f"时间: {report['timestamp']}")
    print(f"{'='*50}")
    print(f"总链接数: {report['summary']['total']}")
    print(f"正常: {report['summary']['ok']}")
    print(f"异常: {report['summary']['errors']}")
    print(f"可用率: {report['summary']['success_rate']}")
    print(f"{'='*50}\n")

    # 显示异常链接
    errors = [r for r in report['details'] if r['status'] != 'ok']
    if errors:
        print("⚠️ 异常链接:")
        for e in errors:
            print(f"  - {e['url']}: {e['status']}")
            if 'error' in e:
                print(f"    错误: {e['error']}")
    else:
        print("✅ 所有链接正常")

def main():
    print(f"开始检查链接: {datetime.now()}")

    # 1. 加载链接列表
    links = load_links_to_check()
    print(f"共 {len(links)} 个链接待检查")

    # 2. 检查每个链接
    results = []
    for link in links:
        print(f"检查: {link}...", end=" ")
        result = check_url(link)
        results.append(result)
        print(f"{'✅' if result['status'] == 'ok' else '❌'} {result['status']}")

    # 3. 生成报告
    report = generate_report(results)

    # 4. 打印报告
    print_report(report)

    # 5. 保存报告
    save_report(report)

    return 0 if report['summary']['errors'] == 0 else 1

if __name__ == "__main__":
    exit(main())
