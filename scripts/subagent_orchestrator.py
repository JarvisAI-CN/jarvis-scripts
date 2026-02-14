#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subagent Orchestrator - 自主编程的子代理协调器

实现三轮协作模式:
1. zhipu/glm-4.7 → 编程/写代码
2. kimi-k2.5 → Debug/测试
3. zhipu/glm-4.7 → 修复/优化
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SubtaskResult:
    """子任务执行结果"""
    success: bool
    output: str
    code: Optional[str] = None
    error: Optional[str] = None
    commit_hash: Optional[str] = None


class SubagentOrchestrator:
    """子代理协调器"""

    def __init__(self, workspace: Path, logger=None):
        self.workspace = workspace
        self.logger = logger

        # 模型配置
        self.models = {
            "coder": "zhipu/glm-4.7",      # 编程主力
            "tester": "nvidia/moonshotai/kimi-k2.5",  # 测试主力
            "fixer": "zhipu/glm-4.7"       # 修复主力
        }

    def log(self, level: str, module: str, message: str):
        """日志记录"""
        if self.logger:
            if level == "INFO":
                self.logger.info(module, message)
            elif level == "SUCCESS":
                self.logger.success(module, message)
            elif level == "ERROR":
                self.logger.error(module, message)
            elif level == "WARNING":
                self.logger.warning(module, message)

    def _call_subagent(
        self,
        model: str,
        task_context: Dict,
        prompt_template: str,
        timeout: int = 300
    ) -> SubtaskResult:
        """调用子代理执行任务"""

        # 构建完整提示
        prompt = prompt_template.format(**task_context)

        self.log("INFO", "ORCHESTRATOR", f"调用模型 {model} 执行任务")

        # 使用 openclaw agent --local 执行
        try:
            # 创建临时文件保存任务描述
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            ) as f:
                json.dump({
                    "model": model,
                    "task": task_context,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
                task_file = f.name

            # 构建命令
            cmd = [
                "openclaw",
                "agent",
                "--local",
                "--message", prompt,
                "--thinking", "medium",
                "--timeout", str(timeout)
            ]

            # 执行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.workspace
            )

            # 清理临时文件
            os.unlink(task_file)

            if result.returncode == 0:
                output = result.stdout

                # 尝试提取代码块
                code = self._extract_code(output)

                return SubtaskResult(
                    success=True,
                    output=output,
                    code=code
                )
            else:
                error_msg = result.stderr or "未知错误"
                self.log("ERROR", "ORCHESTRATOR", f"子代理执行失败: {error_msg}")

                return SubtaskResult(
                    success=False,
                    output="",
                    error=error_msg
                )

        except subprocess.TimeoutExpired:
            self.log("ERROR", "ORCHESTRATOR", f"子代理执行超时 ({timeout}秒)")
            return SubtaskResult(
                success=False,
                output="",
                error="执行超时"
            )
        except Exception as e:
            self.log("ERROR", "ORCHESTRATOR", f"子代理调用异常: {str(e)}")
            return SubtaskResult(
                success=False,
                output="",
                error=str(e)
            )

    def _extract_code(self, text: str) -> Optional[str]:
        """从文本中提取代码块"""

        # 尝试提取 ```python 代码块
        if "```python" in text:
            start = text.find("```python") + 9
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # 尝试提取 ``` 代码块
        if "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        return None

    def execute_bugfix_task(self, task: Dict) -> SubtaskResult:
        """执行 Bug 修复任务（三轮协作）"""

        task_id = task.get("id")
        task_title = task.get("title")
        task_desc = task.get("description", "")

        self.log("INFO", "ORCHESTRATOR", f"开始 Bug 修复任务: {task_id}")

        # 准备任务上下文
        context = {
            "task_id": task_id,
            "title": task_title,
            "description": task_desc,
            "workspace": str(self.workspace)
        }

        # 第一轮: zhipu/glm-4.7 分析并生成修复代码
        self.log("INFO", "ORCHESTRATOR", "第一轮: zhipu/glm-4.7 分析 Bug 并生成修复代码")

        round1_prompt = """你是一个资深的 Bug 修复专家。请完成以下任务:

## 任务信息
- 任务ID: {task_id}
- 标题: {title}
- 描述: {description}

## 工作区
- 路径: {workspace}

## 第一步: Bug 诊断
1. 分析任务描述，理解 Bug 的根本原因
2. 搜索相关的代码文件（使用 find 和 grep）
3. 检查日志文件，查找错误信息

## 第二步: 生成修复代码
1. 基于诊断结果，设计修复方案
2. 编写完整的修复代码
3. 添加必要的注释和错误处理

## 第三步: 输出结果
请按以下格式输出:
```
DIAGNOSIS: [Bug原因分析]
AFFECTED_FILES: [受影响的文件列表]
FIX_CODE:
```python
[你的修复代码]
```
TEST_STEPS: [测试步骤]
```

开始执行。
"""

        round1_result = self._call_subagent(
            model=self.models["coder"],
            task_context=context,
            prompt_template=round1_prompt,
            timeout=300
        )

        if not round1_result.success:
            return round1_result

        # 保存第一轮代码
        round1_code = round1_result.code
        if not round1_code:
            self.log("WARNING", "ORCHESTRATOR", "第一轮未生成代码，跳过后续测试")
            return round1_result

        # 第二轮: kimi-k2.5 测试和 Debug
        self.log("INFO", "ORCHESTRATOR", "第二轮: kimi-k2.5 测试修复代码")

        # 临时保存代码到文件
        temp_code_file = self.workspace / f".temp_fix_{task_id}.py"
        with open(temp_code_file, 'w') as f:
            f.write(round1_code)

        round2_prompt = """你是一个专业的测试工程师。请对以下 Bug 修复代码进行测试:

## 任务信息
- 任务ID: {task_id}
- 标题: {title}

## 修复代码
文件: {workspace}/.temp_fix_{task_id}.py

## 你的任务
1. 代码审查: 检查代码质量、潜在问题
2. 语法检查: 使用 compile() 验证语法
3. 逻辑分析: 识别可能的逻辑错误
4. 边界条件: 检查边界情况处理
5. 性能问题: 识别性能瓶颈

## 输出格式
```
REVIEW_RESULT: [通过/需要修复/失败]
ISSUES_FOUND: [发现的问题列表，编号]
SUGGESTIONS: [改进建议]
VERDICT: [可以通过第二轮/需要返回第一轮修复]
```

开始测试。
"""

        round2_result = self._call_subagent(
            model=self.models["tester"],
            task_context=context,
            prompt_template=round2_prompt,
            timeout=180
        )

        # 清理临时文件
        if temp_code_file.exists():
            temp_code_file.unlink()

        # 第三轮: zhipu/glm-4.7 根据 KIMI 反馈修复
        self.log("INFO", "ORCHESTRATOR", "第三轮: zhipu/glm-4.7 根据反馈优化代码")

        round3_prompt = """你是一个资深的 Bug 修复专家。请根据测试反馈优化代码:

## 原始任务
- 任务ID: {task_id}
- 标题: {title}
- 描述: {description}

## 第一轮代码
{round1_code}

## 第二轮测试反馈
{round2_output}

## 你的任务
根据测试反馈，优化你的修复代码:
1. 如果测试通过，输出最终代码
2. 如果发现问题，修复这些问题
3. 如果有改进建议，考虑是否采纳

## 输出格式
```
FINAL_CODE:
```python
[最终修复代码]
```
CHANGES_MADE: [相对于第一轮的改动说明]
TEST_PLAN: [如何验证修复]
```

开始优化。
"""

        round3_context = {
            **context,
            "round1_code": round1_code,
            "round2_output": round2_result.output
        }

        round3_result = self._call_subagent(
            model=self.models["fixer"],
            task_context=round3_context,
            prompt_template=round3_prompt,
            timeout=240
        )

        if round3_result.success and round3_result.code:
            self.log("SUCCESS", "ORCHESTRATOR", f"Bug 修复任务完成: {task_id}")
            return round3_result
        else:
            # 如果第三轮失败，返回第一轮结果
            self.log("WARNING", "ORCHESTRATOR", f"第三轮未改进，使用第一轮结果")
            return round1_result

    def execute_feature_task(self, task: Dict) -> SubtaskResult:
        """执行功能开发任务（三轮协作）"""

        task_id = task.get("id")
        task_title = task.get("title")
        task_desc = task.get("description", "")

        self.log("INFO", "ORCHESTRATOR", f"开始功能开发任务: {task_id}")

        # 准备任务上下文
        context = {
            "task_id": task_id,
            "title": task_title,
            "description": task_desc,
            "workspace": str(self.workspace)
        }

        # 第一轮: zhipu/glm-4.7 设计并实现功能
        self.log("INFO", "ORCHESTRATOR", "第一轮: zhipu/glm-4.7 设计并实现功能")

        round1_prompt = """你是一个资深的软件工程师。请完成以下功能开发任务:

## 任务信息
- 任务ID: {task_id}
- 标题: {title}
- 描述: {description}

## 工作区
- 路径: {workspace}

## 第一步: 需求分析
1. 理解功能需求
2. 设计技术方案
3. 识别依赖和风险

## 第二步: 代码实现
1. 设计模块结构
2. 实现核心功能
3. 添加错误处理
4. 编写文档注释

## 第三步: 测试用例
1. 设计单元测试
2. 考虑边界情况
3. 准备集成测试

## 输出格式
```
ANALYSIS: [需求分析和技术方案]
IMPLEMENTATION:
```python
[完整的功能实现代码]
```
TEST_PLAN: [测试计划]
DEPENDENCIES: [依赖的外部模块或库]
```

开始实现。
"""

        round1_result = self._call_subagent(
            model=self.models["coder"],
            task_context=context,
            prompt_template=round1_prompt,
            timeout=360
        )

        if not round1_result.success:
            return round1_result

        # 保存第一轮代码
        round1_code = round1_result.code
        if not round1_code:
            self.log("WARNING", "ORCHESTRATOR", "第一轮未生成代码，跳过后续测试")
            return round1_result

        # 第二轮: kimi-k2.5 测试和代码审查
        self.log("INFO", "ORCHESTRATOR", "第二轮: kimi-k2.5 代码审查和测试")

        # 临时保存代码到文件
        temp_code_file = self.workspace / f".temp_feature_{task_id}.py"
        with open(temp_code_file, 'w') as f:
            f.write(round1_code)

        round2_prompt = """你是一个专业的代码审查专家。请审查以下功能代码:

## 任务信息
- 任务ID: {task_id}
- 标题: {title}

## 实现代码
文件: {workspace}/.temp_feature_{task_id}.py

## 你的任务
1. **代码质量**: 检查代码风格、可读性
2. **功能完整性**: 验证是否满足需求
3. **错误处理**: 检查异常处理是否完善
4. **性能考虑**: 识别性能问题
5. **安全考虑**: 识别安全漏洞
6. **测试覆盖**: 评估测试用例的完整性

## 输出格式
```
REVIEW_RESULT: [优秀/良好/需要改进/不合格]
QUALITY_SCORE: [1-10分]
ISSUES: [问题列表，按优先级排序]
SUGGESTIONS: [改进建议]
OPTIMIZATIONS: [性能优化建议]
VERDICT: [可以通过第二轮/需要返回第一轮修改]
```

开始审查。
"""

        round2_result = self._call_subagent(
            model=self.models["tester"],
            task_context=context,
            prompt_template=round2_prompt,
            timeout=240
        )

        # 清理临时文件
        if temp_code_file.exists():
            temp_code_file.unlink()

        # 第三轮: zhipu/glm-4.7 根据审查反馈优化
        self.log("INFO", "ORCHESTRATOR", "第三轮: zhipu/glm-4.7 根据反馈优化功能")

        round3_prompt = """你是一个资深的软件工程师。请根据代码审查反馈优化你的功能:

## 原始任务
- 任务ID: {task_id}
- 标题: {title}
- 描述: {description}

## 第一轮实现
{round1_code}

## 第二轮审查反馈
{round2_output}

## 你的任务
根据审查反馈，优化你的功能实现:
1. 修复识别出的问题
2. 考虑改进建议
3. 优化性能（如果有建议）
4. 完善错误处理
5. 增强测试用例

## 输出格式
```
FINAL_CODE:
```python
[最终优化后的代码]
```
CHANGES_MADE: [改动说明]
IMPROVEMENTS: [改进点]
FINAL_TEST_PLAN: [最终测试方案]
```

开始优化。
"""

        round3_context = {
            **context,
            "round1_code": round1_code,
            "round2_output": round2_result.output
        }

        round3_result = self._call_subagent(
            model=self.models["fixer"],
            task_context=round3_context,
            prompt_template=round3_prompt,
            timeout=300
        )

        if round3_result.success and round3_result.code:
            self.log("SUCCESS", "ORCHESTRATOR", f"功能开发任务完成: {task_id}")
            return round3_result
        else:
            # 如果第三轮失败，返回第一轮结果
            self.log("WARNING", "ORCHESTRATOR", f"第三轮未改进，使用第一轮结果")
            return round1_result


def main():
    """主函数（用于测试）"""
    import sys

    workspace = Path("/home/ubuntu/.openclaw/workspace")

    # 创建协调器
    orchestrator = SubagentOrchestrator(workspace)

    # 测试 Bug 修复任务
    test_task = {
        "id": "TASK-TEST-001",
        "title": "修复 WebDAV 写权限问题",
        "description": "WebDAV 挂载点出现写权限错误，需要诊断并修复"
    }

    print("=== 测试 Bug 修复任务 ===")
    result = orchestrator.execute_bugfix_task(test_task)

    print(f"\n结果: {'成功' if result.success else '失败'}")
    if result.code:
        print(f"\n生成的代码:\n{result.code}")


if __name__ == "__main__":
    main()
