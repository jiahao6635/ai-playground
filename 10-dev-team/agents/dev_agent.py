"""
dev_agent.py — 开发者智能体

学习内容：
  1. 智能体内部使用工具（ReAct 模式）
  2. 智能体作为子图嵌入主图
  3. 复用 create_react_agent 或手动构建

Dev 智能体职责：
  接收技术规格 → 生成代码 → 更新 state.code
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.llm import get_llm

from langchain_core.messages import AIMessage, HumanMessage

# 导入本项目的工具和状态
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools import dev_tools


def dev_node(state: dict) -> dict:
    """
    开发者节点：根据技术规格生成代码。

    输入：state.requirements（技术规格）
    输出：state.code（生成的代码）+ state.messages（Dev 的回复）
    """
    llm = get_llm(temperature=0.3)
    requirements = state.get("requirements", "")
    iteration = state.get("iteration", 0)

    # 如果有测试反馈，Dev 需要修复代码
    test_results = state.get("test_results", "")
    fix_context = ""
    if test_results and iteration > 0:
        fix_context = f"\n\n之前的测试结果：\n{test_results}\n请修复代码中的问题。"

    prompt = f"""你是 Python 开发者。请根据以下技术规格生成代码。

技术规格：
{requirements}{fix_context}

要求：
1. 只输出 Python 代码，不要额外解释
2. 代码要简洁、可运行
3. 用 print() 输出结果以便验证
4. 不要使用 os、subprocess 等危险模块"""

    response = llm.invoke(prompt)

    # 提取代码（去掉 markdown 代码块标记）
    code = response.content
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()

    return {
        "code": code,
        "messages": [AIMessage(content=f"[Dev] 代码已生成（{len(code)}字符）:\n{code[:200]}...")],
    }


def build_dev_subgraph():
    """
    构建 Dev 智能体子图。

    Dev 智能体目前是单节点（直接 LLM 调用）。
    如果需要更复杂的行为，可以在这里构建 ReAct Agent 子图。

    扩展示例（使用 create_react_agent）：
        from langgraph.prebuilt import create_react_agent
        dev_agent = create_react_agent(get_llm(), dev_tools)
        # 但需要注意状态映射
    """
    from langgraph.graph import StateGraph, START, END

    workflow = StateGraph(dict)
    workflow.add_node("dev", dev_node)
    workflow.add_edge(START, "dev")
    workflow.add_edge("dev", END)
    return workflow.compile()
