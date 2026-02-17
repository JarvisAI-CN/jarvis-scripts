#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API健康监控脚本 v2.0
针对OpenClaw多模型容错机制的增强监控

功能：
1. 通过 'openclaw models status --json' 检查模型供应方健康度
2. 记录认证过期时间
3. 检测额度风险
4. 自动尝试修复 (重启Gateway)
5. 生成预警文件供心跳任务读取
"""

import os
import json
import subprocess
from datetime import datetime

# 配置
OPENCLAW_PATH = "/home/ubuntu/.nvm/versions/node/v24.13.0/bin/openclaw"
NODE_BIN_DIR = "/home/ubuntu/.nvm/versions/node/v24.13.0/bin"
STATE_FILE = "/home/ubuntu/.openclaw/workspace/.api_health_state.json"

# 确保 node 在 PATH 中，否则 openclaw 脚本无法运行 (它依赖 #!/usr/bin/env node)
os.environ["PATH"] = f"{NODE_BIN_DIR}:{os.environ.get('PATH', '')}"
LOG_FILE = "/home/ubuntu/.openclaw/workspace/logs/api_health.log"
ALERT_FILE = "/home/ubuntu/.openclaw/workspace/.api_health_alert.json"


def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} [{level}] {message}\n"
    print(log_line.strip())
    with open(LOG_FILE, "a") as f:
        f.write(log_line)


def get_models_status():
    """使用命令行获取模型状态"""
    try:
        result = subprocess.run(
            [OPENCLAW_PATH, "models", "status", "--json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            # 过滤掉 [plugins] 等非JSON行
            output = result.stdout
            if "{" in output:
                json_str = output[output.find("{") :]
                return json.loads(json_str)
            else:
                log("输出中未找到有效的JSON结构", "ERROR")
                return None
        else:
            log(f"获取模型状态失败: {result.stderr}", "ERROR")
            return None
    except Exception as e:
        log(f"获取模型状态异常: {e}", "ERROR")
        return None


def analyze_status(status_data):
    """分析状态数据"""
    if not status_data:
        return {"healthy": False, "alerts": ["无法获取模型状态数据"]}

    alerts = []
    auth_data = status_data.get("auth", {})
    providers = auth_data.get("oauth", {}).get("providers", [])

    # 检查主模型供应方 (google-antigravity)
    google_found = False
    for p in providers:
        if p.get("provider") == "google-antigravity":
            google_found = True
            if p.get("status") != "ok":
                alerts.append(f"Google API 状态异常: {p.get('status')}")

            # 检查过期时间
            remaining_ms = p.get("remainingMs", 0)
            if remaining_ms < 1800000:  # 少于30分钟
                alerts.append(f"Google API 认证即将过期: {remaining_ms//60000}分钟")

    if not google_found:
        # 检查非OAuth供应商 (zhipu, nvidia)
        # 这些通常在 auth.providers 列表里
        all_providers = auth_data.get("providers", [])
        zhipu_ok = any(
            p.get("provider") == "zhipu"
            and p.get("effective", {}).get("kind") == "models.json"
            for p in all_providers
        )
        if not zhipu_ok:
            alerts.append("智谱 (Zhipu) 配置未生效")

    return {"healthy": len(alerts) == 0, "alerts": alerts}


def trigger_restart():
    """尝试重启Gateway"""
    log("尝试重启Gateway服务以刷新认证...", "WARN")
    try:
        subprocess.run([OPENCLAW_PATH, "gateway", "restart"], timeout=60)
        log("Gateway重启指令已下达", "INFO")
    except Exception as e:
        log(f"重启指令下达失败: {e}", "ERROR")


def main():
    log("=== API健康监控 V2.0 开始 ===")

    status_data = get_models_status()
    analysis = analyze_status(status_data)

    # 加载旧状态
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            old_state = json.load(f)
    else:
        old_state = {"failures": 0}

    if not analysis["healthy"]:
        old_state["failures"] = old_state.get("failures", 0) + 1
        log(f"检测到异常: {', '.join(analysis['alerts'])}", "WARN")

        # 写入预警文件供心跳读取
        with open(ALERT_FILE, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "alerts": analysis["alerts"],
                    "failures": old_state["failures"],
                },
                f,
                indent=2,
            )

        # 如果连续失败多次，尝试重启
        if old_state["failures"] >= 2:
            trigger_restart()
            old_state["failures"] = 0  # 重置计数
    else:
        log("✅ 所有核心API状态正常", "INFO")
        old_state["failures"] = 0
        if os.path.exists(ALERT_FILE):
            os.remove(ALERT_FILE)

    # 保存新状态
    old_state["last_check"] = datetime.now().isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(old_state, f, indent=2)

    log("=== API健康监控 V2.0 完成 ===")


if __name__ == "__main__":
    main()
