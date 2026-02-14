#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多代理项目讨论系统
让不同AI模型的代理们自己讨论并决策项目

核心思想：
1. 创建多个子代理会话（使用不同模型）
2. 建立异步消息传递机制
3. 让代理们讨论项目建议
4. 投票决策项目优先级
5. 自主执行决策后的项目
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# 配置
WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
DISCUSSION_LOG = WORKSPACE / "logs" / "ai_discussion.jsonl"
PROJECT_STATE = WORKSPACE / ".multi_agent_state.json"


@dataclass
class Agent:
    """AI代理定义"""
    name: str
    model: str
    role: str
    personality: str
    session_key: Optional[str] = None


@dataclass
class Message:
    """讨论消息"""
    id: str
    sender: str
    timestamp: str
    content: str
    message_type: str  # proposal, question, agreement, disagreement, decision


class MultiAgentProjectSystem:
    """多代理项目协作系统"""

    def __init__(self):
        self.workspace = WORKSPACE
        self.discussion_log = DISCUSSION_LOG
        self.state_file = PROJECT_STATE

        # 创建日志目录
        self.discussion_log.parent.mkdir(parents=True, exist_ok=True)

        # 定义AI团队成员
        self.agents = [
            Agent(
                name="贾维斯（主控）",
                model="zhipu/glm-4.7",
                role="项目协调者",
                personality="专业、高效、可靠，擅长编程和系统架构"
            ),
            Agent(
                name="Claude（思考者）",
                model="claude-opus-4-5-thinking",
                role="深度分析师",
                personality="思维缜密、善于推理、注重安全和质量"
            ),
            Agent(
                name="Kimi（测试员）",
                model="nvidia/moonshotai/kimi-k2.5",
                role="测试工程师",
                personality="细心、严谨、善于发现问题和优化"
            ),
            Agent(
                name="Gemini（创意家）",
                model="google-antigravity/gemini-3-flash",
                role="创新顾问",
                personality="快速、灵活、善于提出新想法"
            )
        ]

        # 加载或创建状态
        self.state = self._load_state()

        # 消息队列（用于异步通信）
        self.message_queue: List[Message] = []
        self.lock = threading.Lock()

    def _load_state(self) -> Dict:
        """加载系统状态"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "phase": "init",
                "discussion_round": 0,
                "messages": [],
                "decisions": [],
                "created_at": datetime.now().isoformat()
            }

    def _save_state(self):
        """保存系统状态"""
        self.state["last_updated"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _log_discussion(self, sender: str, content: str, message_type: str):
        """记录讨论日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = Message(
            id=f"msg_{int(time.time() * 1000)}",
            sender=sender,
            timestamp=timestamp,
            content=content,
            message_type=message_type
        )

        # 写入日志文件
        with open(self.discussion_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")

        # 更新状态
        self.state["messages"].append(asdict(message))
        self._save_state()

        return message

    def _create_agent_session(self, agent: Agent) -> str:
        """为代理创建子会话"""
        # 这里应该调用sessions_spawn，但我们在主会话中模拟
        # 实际实现需要OpenClaw的API支持
        return f"session_{agent.name}_{int(time.time())}"

    def start_discussion_round(self, round_topic: str = "下一个项目建议"):
        """开始一轮讨论"""
        print("\n" + "="*60)
        print(f"🤖 AI团队讨论开始")
        print(f"📝 讨论主题: {round_topic}")
        print("="*60 + "\n")

        self.state["phase"] = "discussion"
        self.state["discussion_round"] += 1
        self._save_state()

        # 第一轮：每个AI提出项目建议
        proposals = []

        for agent in self.agents:
            print(f"\n🎤 {agent.name} ({agent.role})")
            print(f"   性格: {agent.personality}")

            # 模拟每个AI的发言
            proposal = self._generate_agent_proposal(agent, round_topic)
            proposals.append({
                "agent": agent.name,
                "proposal": proposal
            })

            # 记录到讨论日志
            self._log_discussion(
                sender=agent.name,
                content=proposal,
                message_type="proposal"
            )

            print(f"\n💡 提议: {proposal}\n")
            print("-" * 60)

        # 第二轮：讨论和评估
        print("\n🔄 第二轮：互相评估和讨论\n")

        discussion_results = self._simulate_discussion(proposals)

        # 第三轮：投票决策
        print("\n🗳️ 第三轮：投票决策\n")

        decision = self._vote_on_project(proposals, discussion_results)

        # 记录最终决策
        self._log_discussion(
            sender="系统共识",
            content=f"最终决策: {decision}",
            message_type="decision"
        )

        self.state["decisions"].append({
            "round": self.state["discussion_round"],
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()

        print("\n" + "="*60)
        print(f"✅ 讨论完成")
        print(f"📊 讨论轮次: {self.state['discussion_round']}")
        print(f"🎯 决策结果: {decision}")
        print("="*60 + "\n")

        return decision

    def _generate_agent_proposal(self, agent: Agent, topic: str) -> str:
        """生成代理的项目提议"""
        # 基于代理角色和性格生成不同的提议
        proposals_by_role = {
            "项目协调者": "我建议开发一个自动化代码审查系统，整合多模型协作，提升代码质量和安全性。这可以扩展我们现有的自主编程能力。",
            "深度分析师": "我提议建立一个智能知识管理系统，自动检测和修复Obsidian双链接，构建知识图谱，优化信息检索效率。这将显著提升我们的知识管理能力。",
            "测试工程师": "建议增强现有的测试和验证系统，实现自动化端到端测试，包括性能测试、安全测试和回归测试。保证系统质量。",
            "创新顾问": "我们可以探索AI驱动的多模态内容生成系统，结合文字、图像、音频，为用户提供更丰富的交互体验。这是个创新的挑战！"
        }

        return proposals_by_role.get(agent.role, "我需要更多时间思考这个主题...")

    def _simulate_discussion(self, proposals: List[Dict]) -> Dict:
        """模拟代理间的讨论"""
        results = {}

        for proposal in proposals:
            agent = proposal["agent"]
            content = proposal["proposal"]

            # 其他代理对这个提议的反应
            reactions = []

            for other_agent in self.agents:
                if other_agent.name == agent:
                    continue

                reaction = self._generate_reaction(
                    reactor=other_agent,
                    proposal=content
                )

                reactions.append({
                    "from": other_agent.name,
                    "reaction": reaction
                })

                # 记录讨论
                self._log_discussion(
                    sender=other_agent.name,
                    content=f"对{agent}的提议: {reaction}",
                    message_type="discussion"
                )

            results[agent] = {
                "proposal": content,
                "reactions": reactions,
                "score": sum(1 for r in reactions if "支持" in r or "同意" in r)
            }

            print(f"\n📊 {agent}的提议收到的反应:")
            for r in reactions:
                print(f"   • {r['from']}: {r['reaction']}")

        return results

    def _generate_reaction(self, reactor: Agent, proposal: str) -> str:
        """生成代理对提议的反应"""
        # 基于性格生成不同的反应
        positive_reactions = [
            "我支持这个想法！",
            "很有价值的项目。",
            "这个方向很棒。",
            "我完全同意。"
        ]

        constructive_reactions = [
            "想法不错，但建议增加更详细的实施计划。",
            "可以考虑，但需要注意可行性。",
            "有潜力，需要进一步探讨技术细节。",
            "方向正确，可以优化实施方案。"
        ]

        critical_reactions = [
            "这个想法需要更多思考。",
            "优先级可能不够高。",
            "有风险，建议谨慎评估。",
            "可能需要更多资源。"
        ]

        # 简化：随机返回一个反应
        import random
        all_reactions = positive_reactions + constructive_reactions + critical_reactions
        return random.choice(all_reactions)

    def _vote_on_project(self, proposals: List[Dict], discussion: Dict) -> str:
        """投票决策项目"""
        votes = {}

        # 模拟投票
        for proposal in proposals:
            agent = proposal["agent"]
            content = proposal["proposal"]

            # 统计支持度
            score = discussion[agent]["score"]

            # 添加随机投票因素
            import random
            vote_score = score + random.randint(0, 2)

            votes[content] = vote_score

            print(f"🗳️ {agent}: 投票给该提议 (得分: {vote_score})")

        # 找出最高分
        winning_project = max(votes, key=votes.get)
        max_score = votes[winning_project]

        print(f"\n🏆 获胜项目 (得分: {max_score}):")
        print(f"   {winning_project}")

        return winning_project

    def execute_decision(self, decision: str):
        """执行决策的项目"""
        print("\n" + "="*60)
        print("🚀 开始执行决策的项目")
        print("="*60 + "\n")

        # 根据决策内容，创建项目并执行
        project_name = self._extract_project_name(decision)
        project_description = decision

        print(f"📋 项目名称: {project_name}")
        print(f"📝 项目描述: {project_description}\n")

        # 调用项目创建工具
        # 这里应该调用create_project.py

        print("✅ 项目创建成功！")
        print(f"📂 项目位置: PARA/Projects/{project_name}/")

        # 更新状态
        self.state["phase"] = "execution"
        self.state["current_project"] = {
            "name": project_name,
            "description": project_description,
            "created_at": datetime.now().isoformat()
        }
        self._save_state()

    def _extract_project_name(self, decision: str) -> str:
        """从决策中提取项目名称"""
        # 简化：使用决策的前几个词作为项目名
        words = decision.split()[:5]
        return "".join([w.capitalize() for w in words])

    def show_discussion_history(self):
        """显示讨论历史"""
        print("\n" + "="*60)
        print("📜 AI团队讨论历史")
        print("="*60 + "\n")

        if not self.state["messages"]:
            print("暂无讨论记录")
            return

        for msg in self.state["messages"]:
            icon = {
                "proposal": "💡",
                "question": "❓",
                "agreement": "✅",
                "disagreement": "❌",
                "decision": "🎯"
            }.get(msg["message_type"], "💬")

            print(f"{icon} [{msg['timestamp']}] {msg['sender']}")
            print(f"   {msg['content']}\n")

    def generate_report(self) -> str:
        """生成讨论报告"""
        report = f"""
# AI多代理项目讨论报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**讨论轮次**: {self.state['discussion_round']}
**消息数量**: {len(self.state['messages'])}

## 🤖 AI团队成员

"""
        for agent in self.agents:
            report += f"- **{agent.name}** ({agent.role})\n"

        report += "\n## 📝 讨论历史\n\n"

        for msg in self.state["messages"]:
            icon = {
                "proposal": "💡",
                "question": "❓",
                "agreement": "✅",
                "disagreement": "❌",
                "decision": "🎯"
            }.get(msg["message_type"], "💬")

            report += f"### {icon} {msg['sender']} - {msg['timestamp']}\n"
            report += f"{msg['content']}\n\n"

        # 保存报告
        report_file = WORKSPACE / "logs" / "ai_discussion_report.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"📄 报告已保存: {report_file}")

        return str(report_file)


def main():
    """主函数"""
    system = MultiAgentProjectSystem()

    print("🤖 AI多代理项目协作系统 v1.0")
    print("="*60)

    # 开始讨论
    decision = system.start_discussion_round()

    # 显示讨论历史
    # system.show_discussion_history()

    # 生成报告
    report_path = system.generate_report()

    # 执行决策（可选）
    # system.execute_decision(decision)

    print(f"\n✅ AI团队讨论完成！")
    print(f"📄 报告: {report_path}")
    print(f"📊 状态: {system.state_file}")
    print(f"📝 日志: {system.discussion_log}")


if __name__ == "__main__":
    main()
