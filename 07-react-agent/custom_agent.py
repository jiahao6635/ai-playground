"""
P7: ReAct 研究助手 — 手动构建 Agent 循环

学习内容：
  1. 手动构建 Agent 节点（bind_tools + 调用 LLM）
  2. 使用 ToolNode 批量执行工具
  3. 条件边实现 Agent 循环
  4. 对比 create_react_agent 和手动构建

这个文件展示了 create_react_agent 内部的实现原理。
理解这个手动构建版本，才能灵活定制 Agent。

Agent 图结构：
  START → agent → ┬─ (有 tool_calls) → tools → agent → ...
                  └─ (无 tool_calls) → END

运行：python custom_agent.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from state import AgentState
from tools import all_tools


def build_custom_agent():
    """
    手动构建 ReAct Agent 图。

    这是 create_react_agent 内部做的事情，只是手动写出来。
    好处是你可以完全自定义每个环节。
    """
    llm = get_llm(temperature=0.3)

    # ──────────────────────────────────────────────
    # 1. 创建 agent 节点函数
    #    agent 节点：调用 LLM（绑定了工具），返回 AIMessage
    # ──────────────────────────────────────────────

    # 将工具绑定到 LLM
    llm_with_tools = llm.bind_tools(all_tools)

    def agent_node(state: AgentState) -> dict:
        """
        Agent 节点：调用 LLM 生成回复。

        LLM 可能返回：
        1. 普通文本回复（无 tool_calls）→ 直接结束
        2. 工具调用请求（有 tool_calls）→ 进入 tools 节点
        """
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        # 返回的消息会被 add_messages reducer 追加到 messages 列表
        return {"messages": [response]}

    # ──────────────────────────────────────────────
    # 2. 创建 tools 节点
    #    ToolNode 是 LangGraph 预构建的工具执行节点
    #    它会自动解析 AIMessage 中的 tool_calls，
    #    执行对应的工具，返回 ToolMessage
    # ──────────────────────────────────────────────
    tool_node = ToolNode(all_tools)

    # ──────────────────────────────────────────────
    # 3. 创建条件路由函数
    #    判断 LLM 是否要调用工具
    # ──────────────────────────────────────────────
    def should_continue(state: AgentState) -> str:
        """
        条件路由：检查最后一条消息是否有工具调用。

        返回 "tools" 或 END：
        - "tools"：LLM 请求调用工具 → 进入 tools 节点
        - END：LLM 返回了最终回复 → 结束
        """
        last_message = state["messages"][-1]

        # 检查 AIMessage 是否包含 tool_calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # ──────────────────────────────────────────────
    # 4. 构建图
    # ──────────────────────────────────────────────
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # 入口：START → agent
    workflow.add_edge(START, "agent")

    # 条件边：agent → (有工具调用?) → tools 或 END
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # 需要调用工具 → tools 节点
            END: END,          # 不需要 → 结束
        },
    )

    # 工具执行后回到 agent（形成循环）
    workflow.add_edge("tools", "agent")

    # ──────────────────────────────────────────────
    # 5. 编译
    # ──────────────────────────────────────────────
    graph = workflow.compile()

    return graph


def demo_manual_agent():
    """演示手动构建的 Agent"""
    print_step("手动构建的 ReAct Agent")

    agent = build_custom_agent()

    query = "搜索知识库告诉我 Python 的数据类型有哪些？"
    print(f"\n  🧑 问题: {query}")

    # 流式查看执行过程
    print(f"\n  🔄 执行过程:\n")

    for event in agent.stream(
        {"messages": [HumanMessage(content=query)]},
        stream_mode="updates",
    ):
        for node_name, state_update in event.items():
            if "messages" in state_update:
                for msg in state_update["messages"]:
                    role = type(msg).__name__.replace("Message", "")

                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tools = [tc["name"] for tc in msg.tool_calls]
                        print(f"  📍 [{node_name}] → 决定调用工具: {tools}")
                    elif role == "Tool":
                        content = str(msg.content)[:80]
                        print(f"  📍 [{node_name}] → 工具结果: {content}...")
                    else:
                        content = str(msg.content)[:100]
                        print(f"  📍 [{node_name}] → 最终回复: {content}...")

    # 获取最终结果
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    print(f"\n  🤖 最终回答: {result['messages'][-1].content[:200]}...")


def demo_compare():
    """对比：手动构建 vs create_react_agent"""
    print_step("对比：手动构建 vs create_react_agent")

    from langgraph.prebuilt import create_react_agent

    llm = get_llm(temperature=0.3)
    query = "计算 25 * 4 + 10 的结果"

    # 手动构建
    manual_agent = build_custom_agent()
    manual_result = manual_agent.invoke({"messages": [HumanMessage(content=query)]})
    manual_msg_count = len(manual_result["messages"])

    # 预构建
    prebuilt_agent = create_react_agent(llm, all_tools)
    prebuilt_result = prebuilt_agent.invoke({"messages": [HumanMessage(content=query)]})
    prebuilt_msg_count = len(prebuilt_result["messages"])

    print(f"\n  问题: {query}")
    print(f"\n  手动构建 Agent:")
    print(f"    消息数: {manual_msg_count}")
    print(f"    回答: {manual_result['messages'][-1].content[:100]}...")
    print(f"\n  create_react_agent:")
    print(f"    消息数: {prebuilt_msg_count}")
    print(f"    回答: {prebuilt_result['messages'][-1].content[:100]}...")

    print(f"\n  💡 两种方式功能相同，但手动构建能完全自定义：")
    print(f"     - 自定义状态字段（添加非 messages 的字段）")
    print(f"     - 自定义路由逻辑（在 should_continue 中添加额外判断）")
    print(f"     - 自定义节点（在 agent_node 中添加预处理/后处理逻辑）")


def demo_interactive():
    """交互式"""
    print_step("交互式研究助手（手动构建版）")

    agent = build_custom_agent()

    print("\n  输入 'quit' 退出\n")

    while True:
        user_input = input("  🧑 你: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        try:
            result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
            print(f"\n  🤖 AI: {result['messages'][-1].content}\n")
        except Exception as e:
            print(f"\n  ❌ 错误: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P7: 手动构建 ReAct Agent")
    print(f"模型: {config.model_name}\n")

    print("  Agent 图结构:")
    print("  START → agent → ┬─ (有 tool_calls) → tools → agent → ...")
    print("                  └─ (无 tool_calls) → END\n")

    demo_manual_agent()
    demo_compare()
    demo_interactive()

    print("\n✅ 手动构建演示完成！")
    print("\n💡 理解了手动构建后，你可以灵活定制 Agent 的每个环节。")
    print("   在 P8-P10 中，我们将基于这种图结构添加持久化、人工审批和多智能体。")


if __name__ == "__main__":
    main()
