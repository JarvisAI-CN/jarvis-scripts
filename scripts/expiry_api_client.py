#!/usr/bin/env python3
"""
保质期管理系统 - API客户端
让贾维斯可以通过API密钥访问站点数据
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class ExpiryAPI:
    """保质期系统API客户端"""

    def __init__(self, base_url: str, api_key: str):
        """
        初始化API客户端

        Args:
            base_url: 站点基础URL (例如: http://ceshi.dhmip.cn)
            api_key: API密钥
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """
        发送API请求

        Args:
            endpoint: API端点
            params: 查询参数

        Returns:
            响应数据字典
        """
        url = f"{self.base_url}/api.php"
        params = params or {}
        params['endpoint'] = endpoint

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'请求失败: {str(e)}'
            }

    def get_products(self) -> dict:
        """获取所有产品数据"""
        return self._request('products')

    def get_batches(self) -> dict:
        """获取所有批次数据"""
        return self._request('batches')

    def get_expiring(self, days: int = 30) -> dict:
        """
        获取即将过期的产品

        Args:
            days: 天数阈值（默认30天）
        """
        return self._request('expiring', {'days': days})

    def get_summary(self) -> dict:
        """获取汇总统计"""
        return self._request('summary')

    def get_categories(self) -> dict:
        """获取分类数据"""
        return self._request('categories')

    def get_all(self) -> dict:
        """获取所有数据（完整导出）"""
        return self._request('all')

    def generate_report(self) -> str:
        """
        生成汇总报告（AI友好格式）

        Returns:
            格式化的报告文本
        """
        summary = self.get_summary()
        expiring = self.get_expiring()

        if not summary.get('success'):
            return "❌ 无法获取数据"

        stats = summary.get('statistics', {})
        expiring_data = expiring.get('data', [])

        report = f"""
# 保质期管理系统 - 数据报告
生成时间: {summary.get('generated_at', 'N/A')}

## 📊 总体统计
- 总商品数: {stats.get('total_products', 0)}
- 总批次数: {stats.get('total_batches', 0)}
- 总库存: {stats.get('total_stock', 0)}

## ⚠️ 预警统计
- 已过期: {stats.get('expired', 0)}
- 7天内过期: {stats.get('critical', 0)}
- 30天内过期: {stats.get('warning', 0)}

## 📋 即将过期详情 (30天内)
"""

        if expiring_data:
            for item in expiring_data[:20]:  # 只显示前20个
                status_emoji = {
                    'expired': '❌',
                    'critical': '🔴',
                    'warning': '🟡',
                    'attention': '🟠'
                }.get(item.get('status'), '⚪')

                report += f"\n{status_emoji} **{item.get('product_name')}**\n"
                report += f"   - SKU: {item.get('sku')}\n"
                report += f"   - 到期日: {item.get('expiry_date')}\n"
                report += f"   - 剩余天数: {item.get('days_remaining')}\n"
                report += f"   - 数量: {item.get('quantity')}\n"
                report += f"   - 分类: {item.get('category_name', 'N/A')}\n"

            if len(expiring_data) > 20:
                report += f"\n... 还有 {len(expiring_data) - 20} 个项目未显示\n"
        else:
            report += "\n✅ 没有即将过期的商品\n"

        return report

    def get_critical_items(self) -> List[dict]:
        """
        获取需要立即处理的项目（7天内过期或已过期）

        Returns:
            需要关注的项目列表
        """
        expiring = self.get_expiring(days=7)

        if not expiring.get('success'):
            return []

        data = expiring.get('data', [])

        # 分类整理
        critical = {
            'expired': [],
            'critical': []  # 7天内
        }

        for item in data:
            if item.get('status') == 'expired':
                critical['expired'].append(item)
            elif item.get('status') == 'critical':
                critical['critical'].append(item)

        return critical

    def get_category_distribution(self) -> dict:
        """
        获取分类分布统计

        Returns:
            分类统计字典
        """
        summary = self.get_summary()

        if not summary.get('success'):
            return {}

        categories = summary.get('category_stats', [])

        result = {}
        for cat in categories:
            result[cat['name']] = cat['product_count']

        return result


# 便捷函数（供贾维斯直接调用）
def create_api_client(base_url: str, api_key: str) -> ExpiryAPI:
    """
    创建API客户端实例

    Args:
        base_url: 站点URL
        api_key: API密钥

    Returns:
        ExpiryAPI实例
    """
    return ExpiryAPI(base_url, api_key)


# 测试函数
def test_api_connection(base_url: str, api_key: str) -> bool:
    """
    测试API连接是否正常

    Args:
        base_url: 站点URL
        api_key: API密钥

    Returns:
        连接是否成功
    """
    try:
        client = ExpiryAPI(base_url, api_key)
        result = client.get_summary()
        return result.get('success', False)
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False


if __name__ == '__main__':
    # 使用示例
    import sys

    if len(sys.argv) < 3:
        print("用法: python3 expiry_api_client.py <BASE_URL> <API_KEY>")
        print("示例: python3 expiry_api_client.py http://ceshi.dhmip.cn your_api_key_here")
        sys.exit(1)

    base_url = sys.argv[1]
    api_key = sys.argv[2]

    # 创建客户端
    client = ExpiryAPI(base_url, api_key)

    # 生成报告
    report = client.generate_report()
    print(report)

    # 获取需要处理的项目
    critical = client.get_critical_items()
    print(f"\n需要立即处理: {len(critical['expired'])} 个已过期 + {len(critical['critical'])} 个7天内过期")
