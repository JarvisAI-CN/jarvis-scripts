#!/usr/bin/env python3
"""
API健康监控脚本
预防OpenClaw多模型同时失败的问题

功能：
1. 定期测试所有API可用性
2. 检测额度使用情况
3. 提前预警
4. 自动恢复机制
"""

import os
import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# 配置
MODELS = [
    "google-antigravity/gemini-3-flash",
    "google-antigravity/claude-opus-4-5-thinking",
    "nvidia/moonshotai/kimi-k2.5",
    "zhipu/glm-4.7"
]

STATE_FILE = "/home/ubuntu/.openclaw/workspace/.api_health_state.json"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/logs/api_health.log"
ALERT_FILE = "/home/ubuntu/.openclaw/workspace/.api_health_alert.json"

def log(message, level="INFO"):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} [{level}] {message}\n"
    print(log_line.strip())

    with open(LOG_FILE, "a") as f:
        f.write(log_line)

def test_model_availability(model):
    """
    测试模型是否可用
    发送一个简单的测试请求
    """
    try:
        # 设置环境变量，确保openclaw命令可找到
        env = os.environ.copy()
        env["PATH"] = "/home/ubuntu/.nvm/versions/node/v24.13.0/bin:" + env.get("PATH", "")

        # 使用OpenClaw命令行测试
        cmd = [
            "openclaw",
            "agents",
            "call",
            "main",
            "--model",
            model,
            "--message",
            "测试：回复OK"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        # 检查是否成功
        if result.returncode == 0 and "OK" in result.stdout:
            return {"available": True, "response_time": 0}
        else:
            return {
                "available": False,
                "error": result.stderr[:200] if result.stderr else "Unknown error"
            }

    except subprocess.TimeoutExpired:
        return {"available": False, "error": "Timeout"}
    except Exception as e:
        return {"available": False, "error": str(e)}

def load_state():
    """加载状态文件"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_state(state):
    """保存状态文件"""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def check_alert_thresholds(state):
    """检查是否需要发送预警"""
    alerts = []

    for model, data in state.get("models", {}).items():
        # 检查连续失败次数
        consecutive_failures = data.get("consecutive_failures", 0)

        if consecutive_failures >= 3:
            alerts.append({
                "model": model,
                "severity": "HIGH",
                "message": f"模型 {model} 连续失败 {consecutive_failures} 次"
            })

        # 检查最后可用时间
        last_available = data.get("last_available")
        if last_available:
            last_time = datetime.fromisoformat(last_available)
            if datetime.now() - last_time > timedelta(hours=1):
                alerts.append({
                    "model": model,
                    "severity": "MEDIUM",
                    "message": f"模型 {model} 超过1小时不可用"
                })

    return alerts

def send_alert(alerts):
    """发送预警（写入文件，由心跳任务读取）"""
    if alerts:
        with open(ALERT_FILE, "w") as f:
            json.dump(alerts, f, indent=2, default=str)
        log(f"已生成 {len(alerts)} 个预警", "ALERT")

def trigger_auto_recovery():
    """
    触发自动恢复
    当所有模型都不可用时，重启Gateway服务
    """
    log("所有模型不可用，尝试自动恢复...", "WARN")

    try:
        # 设置环境变量
        env = os.environ.copy()
        env["PATH"] = "/home/ubuntu/.nvm/versions/node/v24.13.0/bin:" + env.get("PATH", "")

        # 重启Gateway服务
        subprocess.run(
            ["openclaw", "gateway", "restart"],
            capture_output=True,
            timeout=60,
            env=env
        )
        log("Gateway服务已重启", "INFO")
        return True
    except Exception as e:
        log(f"重启失败: {e}", "ERROR")
        return False

def main():
    """主函数"""
    log("=== API健康监控开始 ===")

    # 加载状态
    state = load_state()

    if "models" not in state:
        state["models"] = {}
        state["last_check"] = None

    # 测试所有模型
    available_count = 0

    for model in MODELS:
        log(f"测试模型: {model}")

        result = test_model_availability(model)

        if model not in state["models"]:
            state["models"][model] = {
                "consecutive_failures": 0,
                "last_available": None
            }

        if result["available"]:
            state["models"][model]["consecutive_failures"] = 0
            state["models"][model]["last_available"] = datetime.now().isoformat()
            state["models"][model]["last_error"] = None
            available_count += 1
            log(f"  ✅ 可用")
        else:
            state["models"][model]["consecutive_failures"] += 1
            state["models"][model]["last_error"] = result.get("error", "Unknown")
            failures = state["models"][model]["consecutive_failures"]
            log(f"  ❌ 不可用 (连续失败{failures}次): {result.get('error', '')}")

    # 保存状态
    state["last_check"] = datetime.now().isoformat()
    save_state(state)

    # 检查预警条件
    alerts = check_alert_thresholds(state)
    if alerts:
        send_alert(alerts)

    # 如果所有模型都不可用，触发自动恢复
    if available_count == 0:
        log("⚠️ 所有模型都不可用！", "CRITICAL")
        trigger_auto_recovery()
    else:
        log(f"✅ {available_count}/{len(MODELS)} 模型可用")

    log("=== API健康监控完成 ===")

if __name__ == "__main__":
    main()
