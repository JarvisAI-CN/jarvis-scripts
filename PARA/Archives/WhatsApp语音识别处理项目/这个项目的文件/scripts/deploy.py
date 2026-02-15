#!/usr/bin/env python3
"""
WhatsApp语音处理系统部署脚本
功能：自动化部署、配置、测试
版本: v1.0
创建: 2026-02-14
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime


class Deployer:
    """WhatsApp语音处理系统部署器"""

    def __init__(self, workspace: str = "/home/ubuntu/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.project_dir = self.workspace / "PARA/Projects/WhatsApp语音识别处理项目"
        self.scripts_dir = self.project_dir / "这个项目的文件/scripts"
        self.state_dir = Path("/tmp/whatsapp_voice_state")
        self.temp_dir = Path("/tmp/whatsapp_voices")
        self.log_file = self.project_dir / "这个项目的文件/logs/deploy.log"

    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        print(log_entry.strip())
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

    def check_dependencies(self) -> bool:
        """检查依赖项"""
        self.log("🔍 检查依赖项...")

        dependencies = {
            "Python 3.10+": lambda: sys.version_info >= (3, 10),
            "requests": lambda: self._check_package("requests"),
            "ffmpeg": lambda: self._check_command("ffmpeg"),
            "openclaw": lambda: self._check_command("openclaw")
        }

        all_ok = True
        for name, check_func in dependencies.items():
            try:
                if check_func():
                    self.log(f"  ✅ {name}")
                else:
                    self.log(f"  ❌ {name} - 未找到")
                    all_ok = False
            except Exception as e:
                self.log(f"  ⚠️  {name} - 检查失败: {e}")
                all_ok = False

        return all_ok

    def _check_package(self, package: str) -> bool:
        """检查Python包"""
        try:
            __import__(package)
            return True
        except ImportError:
            return False

    def _check_command(self, command: str) -> bool:
        """检查命令是否存在"""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def install_dependencies(self) -> bool:
        """安装依赖项"""
        self.log("📦 安装依赖项...")

        try:
            # 安装Python包
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "requests", "--quiet"],
                check=True,
                timeout=120
            )
            self.log("  ✅ Python包安装完成")
            return True
        except Exception as e:
            self.log(f"  ❌ 安装失败: {e}")
            return False

    def create_directories(self) -> bool:
        """创建必要的目录"""
        self.log("📁 创建目录结构...")

        directories = [
            self.state_dir,
            self.temp_dir,
            self.project_dir / "这个项目的文件/logs",
            self.project_dir / "这个项目的文件/config"
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.log(f"  ✅ {directory}")
            except Exception as e:
                self.log(f"  ❌ 创建失败 {directory}: {e}")
                return False

        return True

    def verify_scripts(self) -> bool:
        """验证脚本文件"""
        self.log("🔍 验证脚本文件...")

        required_scripts = [
            "whatsapp_voice_handler.py",
            "openclaw_integration.py",
            "test_whatsapp_voice.py"
        ]

        all_ok = True
        for script in required_scripts:
            script_path = self.scripts_dir / script
            if script_path.exists():
                size = script_path.stat().st_size
                self.log(f"  ✅ {script} ({size} bytes)")
            else:
                self.log(f"  ❌ {script} - 未找到")
                all_ok = False

        return all_ok

    def run_tests(self) -> bool:
        """运行测试套件"""
        self.log("🧪 运行测试套件...")

        test_script = self.scripts_dir / "test_whatsapp_voice.py"

        if not test_script.exists():
            self.log("  ❌ 测试脚本未找到")
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(test_script)],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(self.scripts_dir)
            )

            # 输出测试结果
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

            if result.returncode == 0:
                self.log("  ✅ 所有测试通过")
                return True
            else:
                self.log(f"  ❌ 测试失败 (exit code: {result.returncode})")
                return False
        except Exception as e:
            self.log(f"  ❌ 测试运行失败: {e}")
            return False

    def create_config_template(self) -> bool:
        """创建配置模板"""
        self.log("📝 创建配置模板...")

        config_file = self.project_dir / "这个项目的文件/config/config.json"

        try:
            config_template = {
                "zhipu_api_key": "YOUR_ZHIPU_API_KEY_HERE",
                "openclaw_bin": "openclaw",
                "state_file": "/tmp/whatsapp_voice_state/state.json",
                "temp_dir": "/tmp/whatsapp_voices",
                "log_level": "INFO",
                "timeout": {
                    "download": 30,
                    "transcribe": 60,
                    "convert": 60
                }
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_template, f, indent=2, ensure_ascii=False)

            self.log(f"  ✅ 配置模板创建完成: {config_file}")
            return True
        except Exception as e:
            self.log(f"  ❌ 创建配置失败: {e}")
            return False

    def create_systemd_service(self) -> bool:
        """创建systemd服务（可选）"""
        self.log("🔧 创建systemd服务（可选）...")

        service_file = Path("/tmp/whatsapp-voice-handler.service")

        try:
            service_content = f"""[Unit]
Description=WhatsApp Voice Message Handler
After=network.target

[Service]
Type=simple
User={os.environ.get('USER', 'ubuntu')}
WorkingDirectory={self.scripts_dir}
ExecStart={sys.executable} {self.scripts_dir}/whatsapp_voice_handler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

            with open(service_file, 'w', encoding='utf-8') as f:
                f.write(service_content)

            self.log(f"  ✅ 服务文件创建完成: {service_file}")
            self.log("  💡 安装命令: sudo cp {service_file} /etc/systemd/system/")
            self.log("  💡 启用命令: sudo systemctl enable whatsapp-voice-handler")
            self.log("  💡 启动命令: sudo systemctl start whatsapp-voice-handler")
            return True
        except Exception as e:
            self.log(f"  ❌ 创建服务失败: {e}")
            return False

    def deploy(self, run_tests: bool = True) -> bool:
        """执行完整部署流程"""
        self.log("=" * 70)
        self.log("🚀 WhatsApp语音处理系统部署开始")
        self.log("=" * 70)

        steps = [
            ("检查依赖项", self.check_dependencies),
            ("创建目录", self.create_directories),
            ("验证脚本", self.verify_scripts),
            ("创建配置", self.create_config_template),
            ("创建服务", self.create_systemd_service),
        ]

        if run_tests:
            steps.append(("运行测试", self.run_tests))

        for step_name, step_func in steps:
            self.log(f"\n📍 {step_name}...")
            if not step_func():
                self.log(f"\n❌ 部署失败: {step_name}")
                return False

        self.log("\n" + "=" * 70)
        self.log("✅ 部署完成！")
        self.log("=" * 70)
        self.log("\n📋 下一步:")
        self.log("1. 编辑配置文件: nano 这个项目的文件/config/config.json")
        self.log("2. 测试语音处理: python3 这个项目的文件/scripts/whatsapp_voice_handler.py --audio-url <URL> --message-id test123")
        self.log("3. 配置OpenClaw WhatsApp通道")
        self.log("4. 启动自动处理（可选）")

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="WhatsApp语音处理系统部署工具")
    parser.add_argument("--workspace", default="/home/ubuntu/.openclaw/workspace", help="工作区路径")
    parser.add_argument("--skip-tests", action="store_true", help="跳过测试")
    parser.add_argument("--install-deps", action="store_true", help="安装依赖项")

    args = parser.parse_args()

    deployer = Deployer(workspace=args.workspace)

    # 如果指定了安装依赖
    if args.install_deps:
        if not deployer.install_dependencies():
            sys.exit(1)

    # 执行部署
    success = deployer.deploy(run_tests=not args.skip_tests)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
