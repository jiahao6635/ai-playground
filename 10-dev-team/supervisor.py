"""
supervisor.py — Supervisor 主管路由逻辑

学习内容：
  1. Supervisor 作为 LLM 节点决策路由
  2. 根据当前状态决定下一个执行的智能体
  3. 条件边路由到对应子图

Supervisor 的工作方式：
  1. 查看当前状态（需求是否就绪、代码是否生成、测试是否完成）
  2. LLM 分析当前进度，决定下一步交给谁
  3. 返回 {"next_agent": "pm" | "dev" | "tester" | "FINISH"}
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.config import get_llm_config

from langchain_core.messages import AIMessage
from langgraph.graph import END


# 可选的智能体
AGENTS = ["pm", "dev", "tester"]


def supervisor_node(state: dict) -> dict:
    """
    Supervisor 节点：分析状态，决定下一个智能体。

    返回 {"next_agent": "pm" | "dev" | "tester" | "FINISH"}
    """
    llm = get_llm(temperature=0.3)
    iteration = state.get("iteration", 0)

    # 防止无限循环
    if iteration >= 4:
        return {
            "next_agent": "FINISH",
            "messages": [AIMessage(content="[Supervisor] 达到最大迭代次数，流程结束。")],
        }

    # 收集当前各阶段的产出
    requirements = state.get("requirements", "")
    code = state.get("code", "")
    test_results = state.get("test_results", "")

    # ──────────────────────────────────────────────
    # 规则引擎 + LLM 混合决策
    # 先用简单规则判断（快速、可靠），再用 LLM 补充
    # ──────────────────────────────────────────────

    # 简单规则路由
    if not requirements:
        # 需求还没细化 → 交给 PM
        next_agent = "pm"
        reason = "需求尚未分析，交给 PM"
    elif not code:
        # 需求有了但还没代码 → 交给 Dev
        next_agent = "dev"
        reason = "需求已就绪，交给 Dev 生成代码"
    elif not test_results:
        # 代码有了但还没测试 → 交给 Tester
        next_agent = "tester"
        reason = "代码已生成，交给 Tester 测试"
    else:
        # 所有阶段都完成了 → 用 LLM 判断是否需要重做
        prompt = f"""你是开发团队的主管。请根据当前进度判断是否需要继续迭代。

当前状态：
- 迭代次数：{iteration}
- 需求：{'已就绪' if requirements else '未就绪'}
- 代码：{'已生成' if code else '未生成'}
- 测试结果：{'已完成' if test_results else '未完成'}

测试结果摘要：
{test_results[:300] if test_results else '无'}

如果测试通过，没有明显问题，请回复 "FINISH"。
如果需要修复代码，请回复 "dev"。
如果需要重新分析需求，请回复 "pm"。
如果需要重新测试，请回复 "tester"。

只回复一个词。"""

        response = llm.invoke(prompt)
        next_agent = response.content.strip().lower()

        # 验证返回值
        if next_agent not in AGENTS and next_agent != "finish":
            next_agent = "FINISH"  # 默认结束

        if next_agent == "finish":
            next_agent = "FINISH"

        reason = f"LLM 决策: {next_agent}"

    return {
        "next_agent": next_agent,
        "iteration": iteration + 1,
        "messages": [AIMessage(content=f"[Supervisor] {reason}")],
    }


def route_from_supervisor(state: dict) -> str:
    """
    条件路由函数：根据 Supervisor 的决策路由到对应智能体。

    返回值对应 add_conditional_edges 中的映射键。
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH":
        return END
    return next_agent
