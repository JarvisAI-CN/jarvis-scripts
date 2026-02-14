#!/usr/bin/env python3
"""
WhatsApp语音处理系统部署脚本
版本: v1.0
创建: 2026-02-14

功能:
1. 检查系统依赖
2. 安装Python包
3. 验证配置
4. 运行测试
5. 创建systemd服务（可选）
"""

from __future__ import annotations
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentManager:
    """部署管理器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "这个项目的文件/脚本"
        self.docs_dir = project_root / "这个项目的文件/文档"

    def check_dependencies(self) -> bool:
        """检查系统依赖"""
        logger.info("🔍 检查系统依赖...")

        dependencies = {
            "python3": "Python 3",
            "pip3": "Pip package manager",
            "ffmpeg": "FFmpeg audio processor"
        }

        missing = []

        for cmd, name in dependencies.items():
            try:
                subprocess.run(
                    ["which", cmd],
                    check=True,
                    capture_output=True
                )
                logger.info(f"  ✅ {name} 已安装")
            except subprocess.CalledProcessError:
                logger.warning(f"  ❌ {name} 未找到")
                missing.append((cmd, name))

        if missing:
            logger.warning(f"\n缺少 {len(missing)} 个依赖:")
            for cmd, name in missing:
                install_cmd = self._get_install_command(cmd)
                logger.info(f"  - {name}: {install_cmd}")

            response = input("\n是否自动安装? (y/N): ").strip().lower()
            if response == 'y':
                return self._install_dependencies(missing)
            else:
                logger.error("请手动安装缺少的依赖后重试")
                return False

        return True

    def _get_install_command(self, cmd: str) -> str:
        """获取安装命令"""
        if cmd == "ffmpeg":
            return "sudo apt install -y ffmpeg"
        elif cmd in ["python3", "pip3"]:
            return "sudo apt install -y python3 python3-pip"
        return f"sudo apt install -y {cmd}"

    def _install_dependencies(self, missing: list) -> bool:
        """安装缺少的依赖"""
        logger.info("📦 安装依赖...")

        install_commands = set()
        for cmd, name in missing:
            install_commands.add(self._get_install_command(cmd))

        for cmd in install_commands:
            try:
                logger.info(f"执行: {cmd}")
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"安装失败: {e}")
                return False

        return True

    def install_python_packages(self) -> bool:
        """安装Python包"""
        logger.info("🐍 安装Python包...")

        packages = ["requests"]
        missing = []

        for package in packages:
            try:
                __import__(package)
                logger.info(f"  ✅ {package} 已安装")
            except ImportError:
                logger.warning(f"  ❌ {package} 未安装")
                missing.append(package)

        if missing:
            logger.info(f"安装 {len(missing)} 个Python包...")
            try:
                subprocess.run(
                    ["pip3", "install"] + missing,
                    check=True
                )
                logger.info("✅ Python包安装完成")
            except subprocess.CalledProcessError as e:
                logger.error(f"安装失败: {e}")
                return False

        return True

    def verify_configuration(self) -> bool:
        """验证配置"""
        logger.info("⚙️ 验证配置...")

        # 检查API密钥
        api_key = os.environ.get("ZHIPU_API_KEY")
        if not api_key:
            logger.warning("⚠️ 未设置 ZHIPU_API_KEY 环境变量")
            logger.info("提示: export ZHIPU_API_KEY='your_api_key'")
            return False

        logger.info("✅ API密钥已配置")

        # 检查目录权限
        temp_dir = Path("/tmp/whatsapp_voices")
        try:
            temp_dir.mkdir(parents=True, exist_ok=True)
            test_file = temp_dir / "test_write"
            test_file.write_text("test")
            test_file.unlink()
            logger.info("✅ 临时目录权限正常")
        except Exception as e:
            logger.error(f"❌ 临时目录权限错误: {e}")
            return False

        return True

    def run_tests(self) -> bool:
        """运行测试套件"""
        logger.info("🧪 运行测试套件...")

        test_script = self.scripts_dir / "test_voice_handler.py"

        if not test_script.exists():
            logger.error(f"测试脚本不存在: {test_script}")
            return False

        try:
            result = subprocess.run(
                ["python3", str(test_script)],
                capture_output=True,
                text=True,
                timeout=60
            )

            logger.info(result.stdout)

            if result.returncode == 0:
                logger.info("✅ 所有测试通过")
                return True
            else:
                logger.error(f"❌ 测试失败 (退出码: {result.returncode})")
                logger.error(result.stderr)
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ 测试超时")
            return False
        except Exception as e:
            logger.error(f"❌ 测试执行失败: {e}")
            return False

    def create_systemd_service(self) -> bool:
        """创建systemd服务（可选）"""
        logger.info("🔧 创建systemd服务...")

        service_file = Path("/etc/systemd/system/whatsapp-voice-handler.service")

        if service_file.exists():
            logger.warning("⚠️ 服务文件已存在")
            return True

        service_content = f"""[Unit]
Description=WhatsApp Voice Message Handler
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={self.scripts_dir}
Environment="ZHIPU_API_KEY={{ZHIPU_API_KEY}}"
ExecStart=/usr/bin/python3 {self.scripts_dir}/openclaw_integration.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        try:
            # 需要root权限
            result = subprocess.run(
                ["sudo", "tee", str(service_file)],
                input=service_content,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ 服务文件创建: {service_file}")
                logger.info("启动服务:")
                logger.info(f"  sudo systemctl daemon-reload")
                logger.info(f"  sudo systemctl enable whatsapp-voice-handler")
                logger.info(f"  sudo systemctl start whatsapp-voice-handler")
                return True
            else:
                logger.error("❌ 创建服务文件失败（需要sudo权限）")
                return False

        except Exception as e:
            logger.error(f"❌ 创建服务失败: {e}")
            return False

    def deploy(self, create_service: bool = False) -> bool:
        """执行完整部署流程"""
        logger.info("🚀 开始部署WhatsApp语音处理系统...\n")

        steps = [
            ("检查依赖", self.check_dependencies),
            ("安装Python包", self.install_python_packages),
            ("验证配置", self.verify_configuration),
            ("运行测试", self.run_tests)
        ]

        for step_name, step_func in steps:
            logger.info(f"\n{'='*60}")
            logger.info(f"步骤: {step_name}")
            logger.info('='*60)

            if not step_func():
                logger.error(f"\n❌ 部署失败: {step_name}")
                return False

        # 可选：创建systemd服务
        if create_service:
            logger.info(f"\n{'='*60}")
            logger.info("步骤: 创建systemd服务")
            logger.info('='*60)
            self.create_systemd_service()

        logger.info(f"\n{'='*60}")
        logger.info("🎉 部署成功！")
        logger.info('='*60)
        logger.info("\n📖 使用指南:")
        logger.info(f"  1. 设置API密钥: export ZHIPU_API_KEY='your_api_key'")
        logger.info(f"  2. 运行服务: python3 {self.scripts_dir}/openclaw_integration.py")
        logger.info(f"  3. 查看文档: {self.docs_dir}/使用指南.md")
        logger.info(f"  4. 运行测试: python3 {self.scripts_dir}/test_voice_handler.py")

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="WhatsApp语音处理系统部署脚本")
    parser.add_argument(
        "--with-service",
        action="store_true",
        help="创建systemd服务（需要sudo权限）"
    )

    args = parser.parse_args()

    # 项目根目录
    project_root = Path(__file__).parent.parent.parent

    # 执行部署
    manager = DeploymentManager(project_root)
    success = manager.deploy(create_service=args.with_service)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
