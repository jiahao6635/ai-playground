"""
pm_agent.py — 产品经理智能体

学习内容：
  1. 智能体作为图的一个节点
  2. 智能体内部的 LLM 逻辑
  3. 智能体更新共享状态

PM 智能体职责：
  接收用户原始需求 → 细化为技术规格 → 更新 state.requirements
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.llm import get_llm

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END


def pm_node(state: dict) -> dict:
    """
    产品经理节点：将用户需求细化为技术规格。

    输入：state.user_request（用户原始需求）
    输出：state.requirements（技术规格）+ state.messages（PM 的回复）
    """
    llm = get_llm(temperature=0.3)
    user_request = state.get("user_request", "")
    iteration = state.get("iteration", 0)

    # 如果有测试反馈，PM 需要根据反馈调整需求
    test_results = state.get("test_results", "")
    feedback_context = ""
    if test_results and iteration > 0:
        feedback_context = f"\n\n上一轮测试结果：\n{test_results}\n请根据测试结果调整需求。"

    prompt = f"""你是产品经理。请将以下用户需求转化为清晰的技术规格文档。

用户需求：{user_request}{feedback_context}

请输出技术规格，包括：
1. 功能描述（简洁说明要实现什么）
2. 输入输出规格
3. 实现要求（语言、限制等）

保持简洁，200字以内。"""

    response = llm.invoke(prompt)

    return {
        "requirements": response.content,
        "messages": [AIMessage(content=f"[PM] 需求分析完成：\n{response.content[:200]}...")],
    }


def build_pm_subgraph():
    """
    构建 PM 智能体子图。

    这里 PM 智能体很简单（单节点），但子图结构允许未来扩展
    （例如 PM 内部也可以有多步骤流程）。
    """
    workflow = StateGraph(dict)
    workflow.add_node("pm", pm_node)
    workflow.add_edge(START, "pm")
    workflow.add_edge("pm", END)
    return workflow.compile()
