#!/usr/bin/env python3
"""
保质期管理系统 - 核心功能模块
优化版本 v2.0 - 代码质量提升
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
import mysql.connector
from mysql.connector import Error


class ExpiryManager:
    """保质期管理核心类"""

    def __init__(self, config: Dict[str, str]):
        """初始化管理器

        Args:
            config: 数据库配置字典
        """
        self.config = config
        self.connection: Optional[mysql.connector.MySQLConnection] = None

    def connect(self) -> bool:
        """连接数据库"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            return True
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def check_expiry(self, days_threshold: int = 30) -> List[Dict]:
        """检查即将过期的物品

        Args:
            days_threshold: 提前预警天数

        Returns:
            过期物品列表
        """
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []

        cursor = self.connection.cursor(dictionary=True)
        threshold_date = (datetime.now() + timedelta(days=days_threshold)).strftime(
            "%Y-%m-%d"
        )

        query = """
            SELECT id, name, expiry_date, category, quantity, location
            FROM items
            WHERE expiry_date <= %s
            ORDER BY expiry_date ASC
        """

        cursor.execute(query, (threshold_date,))
        items = cursor.fetchall()
        cursor.close()

        return items

    def generate_alert(self, item: Dict) -> Dict[str, str]:
        """生成过期预警

        Args:
            item: 物品信息

        Returns:
            预警信息字典
        """
        expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d").date()
        today = datetime.now().date()
        days_left = (expiry_date - today).days

        if days_left < 0:
            status = "🔴 已过期"
            urgency = "critical"
        elif days_left <= 7:
            status = "🔴 即将过期"
            urgency = "high"
        elif days_left <= 30:
            status = "🟠 需要关注"
            urgency = "medium"
        else:
            status = "🟢 状态良好"
            urgency = "low"

        return {
            "status": status,
            "urgency": urgency,
            "days_left": days_left,
            "item": item,
        }

    def get_inventory_summary(self) -> Dict:
        """获取库存摘要"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return {}

        cursor = self.connection.cursor(dictionary=True)

        # 总物品数
        cursor.execute("SELECT COUNT(*) as total FROM items")
        total = cursor.fetchone()["total"]

        # 按分类统计
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM items
            GROUP BY category
        """)
        by_category = cursor.fetchall()

        cursor.close()

        return {"total_items": total, "by_category": by_category}


def format_expiry_html(alerts: List[Dict]) -> str:
    """格式化为HTML表格

    Args:
        alerts: 预警列表

    Returns:
        HTML字符串
    """
    if not alerts:
        return "<p>✅ 没有即将过期的物品</p>"

    html = """
    <style>
        .expiry-table { width: 100%; border-collapse: collapse; }
        .expiry-table th, .expiry-table td { 
            padding: 12px; 
            text-align: left; 
            border-bottom: 1px solid #ddd; 
        }
        .expiry-table th { background-color: #4299e1; color: white; }
        .critical { background-color: #fff5f5; color: #c53030; font-weight: bold; }
        .high { background-color: #fffaf0; color: #c05621; }
        .medium { background-color: #fffff0; color: #d69e2e; }
        .low { background-color: #f0fff4; color: #38a169; }
    </style>
    <table class="expiry-table">
        <tr>
            <th>状态</th>
            <th>名称</th>
            <th>过期日期</th>
            <th>剩余天数</th>
            <th>分类</th>
            <th>数量</th>
            <th>位置</th>
        </tr>
    """

    for alert in alerts:
        item = alert["item"]
        urgency = alert["urgency"]
        days_left = alert["days_left"]

        row_style = {
            "critical": "background-color: #fff5f5; color: #c53030; font-weight: bold;",
            "high": "background-color: #fffaf0; color: #c05621;",
            "medium": "background-color: #fffff0; color: #d69e2e;",
            "low": "background-color: #f0fff4; color: #38a169;",
        }.get(urgency, "")

        html += f"""
        <tr style="{row_style}">
            <td>{alert['status']}</td>
            <td>{item.get('name', 'N/A')}</td>
            <td>{item.get('expiry_date', 'N/A')}</td>
            <td>{days_left}天</td>
            <td>{item.get('category', 'N/A')}</td>
            <td>{item.get('quantity', 'N/A')}</td>
            <td>{item.get('location', 'N/A')}</td>
        </tr>
        """

    html += "</table>"
    return html


def send_expiry_alert(alerts: List[Dict]) -> bool:
    """发送过期预警邮件

    Args:
        alerts: 预警列表

    Returns:
        是否发送成功
    """
    if not alerts:
        return True

    try:
        # 生成邮件内容
        html_content = format_expiry_html(alerts)

        # 使用邮件工具发送
        import subprocess

        result = subprocess.run(
            [
                "python3",
                "/home/ubuntu/.openclaw/workspace/scripts/email_tool.py",
                "send",
            ],
            input=f"过期预警 - {len(alerts)}个物品需要关注\n\n{html_content}",
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
    except Exception as e:
        print(f"❌ 发送邮件失败: {e}")
        return False


def main():
    """主函数"""
    # 数据库配置（应该从环境变量或配置文件读取）
    config = {
        "host": "localhost",
        "user": "expiry_user",
        "password": "Expiry2024!",  # TODO: 从环境变量读取
        "database": "expiry_system",
    }

    # 创建管理器
    manager = ExpiryManager(config)

    try:
        # 检查过期物品
        items = manager.check_expiry(days_threshold=30)

        if not items:
            print("✅ 没有即将过期的物品")
            return

        # 生成预警
        alerts = [manager.generate_alert(item) for item in items]

        # 过滤高优先级预警
        urgent_alerts = [
            alert for alert in alerts if alert["urgency"] in ["critical", "high"]
        ]

        # 输出报告
        print(f"\n📊 过期预警报告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"总计: {len(alerts)}个物品需要关注")
        print(f"紧急: {len(urgent_alerts)}个")
        print("\n" + "=" * 60)

        for alert in urgent_alerts[:10]:  # 只显示前10个
            item = alert["item"]
            print(f"{alert['status']} {item.get('name', 'N/A')}")
            print(f"   过期日期: {item.get('expiry_date', 'N/A')}")
            print(f"   剩余天数: {alert['days_left']}天")
            print(f"   位置: {item.get('location', 'N/A')}")
            print()

        # 发送邮件预警
        if urgent_alerts:
            send_expiry_alert(urgent_alerts)

    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()
