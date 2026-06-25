"""
P7: ReAct 研究助手 — 使用 create_react_agent 预构建

学习内容：
  1. create_react_agent() 一行创建 Agent
  2. Agent 自动进行多轮工具调用
  3. stream_mode 查看执行过程

create_react_agent 是 LangGraph 提供的预构建 Agent：
  - 内部自动创建 agent 节点和 tools 节点
  - 自动设置条件边实现 Agent 循环
  - 自动管理消息历史

对比 P5 的手动 while 循环和 P7 custom_agent.py 的手动构建，
create_react_agent 大幅简化了代码。

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

from tools import all_tools


def demo_simple_query():
    """演示 1：简单查询（单次工具调用）"""
    print_step("演示 1：简单查询（单次工具调用）")

    llm = get_llm(temperature=0.3)

    # ──────────────────────────────────────────────
    # create_react_agent — 一行创建 Agent
    # 这行代码等价于 custom_agent.py 中手动构建的整个图！
    #
    # 内部自动完成：
    #   1. 创建 agent 节点（调用 LLM with tools）
    #   2. 创建 tools 节点（ToolNode）
    #   3. 设置条件边（有 tool_calls → tools，无 → END）
    #   4. 设置 tools → agent 循环
    # ──────────────────────────────────────────────
    agent = create_react_agent(llm, all_tools)

    # 调用 Agent
    result = agent.invoke({
        "messages": [HumanMessage(content="搜索一下 LangChain 是什么？")]
    })

    # 获取最后一条 AI 消息
    last_msg = result["messages"][-1]
    print(f"\n  🤖 回答: {last_msg.content}")

    # 展示工具调用过程
    print(f"\n  📊 消息历史（共 {len(result['messages'])} 条）:")
    for msg in result["messages"]:
        role = type(msg).__name__.replace("Message", "")
        content = str(msg.content)[:60]
        print(f"     [{role}] {content}...")


def demo_multi_tool_query():
    """演示 2：多轮工具调用"""
    print_step("演示 2：多轮工具调用（Agent 自动决定调用顺序）")

    llm = get_llm(temperature=0.3)
    agent = create_react_agent(llm, all_tools)

    query = "先搜索一下 Python 的最新版本信息，然后搜索知识库了解 Python 的基本数据类型，最后告诉我 Python 有哪些数据类型。"
    print(f"\n  🧑 问题: {query}")

    result = agent.invoke({"messages": [HumanMessage(content=query)]})

    last_msg = result["messages"][-1]
    print(f"\n  🤖 回答: {last_msg.content}")

    # 统计工具调用次数
    tool_calls = sum(
        1 for msg in result["messages"]
        if hasattr(msg, "tool_calls") and msg.tool_calls
    )
    print(f"\n  📊 Agent 共调用了 {tool_calls} 次工具")


def demo_stream():
    """演示 3：流式查看 Agent 执行过程"""
    print_step("演示 3：流式执行（查看每一步）")

    llm = get_llm(temperature=0.3)
    agent = create_react_agent(llm, all_tools)

    query = "帮我计算 (15 + 27) * 3 的结果，然后搜索知识库告诉我 Python 的安装方法。"
    print(f"\n  🧑 问题: {query}\n")

    # ──────────────────────────────────────────────
    # stream() 逐步返回状态更新
    # stream_mode="values" 每步返回完整状态（含所有消息）
    # stream_mode="updates" 每步只返回增量更新
    # ──────────────────────────────────────────────
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
                        print(f"  📍 [{node_name}] {role} → 调用工具: {tools}")
                    elif role == "Tool":
                        content = str(msg.content)[:80]
                        print(f"  📍 [{node_name}] {role} → 结果: {content}...")
                    else:
                        content = str(msg.content)[:80]
                        print(f"  📍 [{node_name}] {role} → {content}...")

    # 获取最终结果
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    print(f"\n  🤖 最终回答: {result['messages'][-1].content[:200]}...")


def demo_interactive():
    """演示 4：交互式 Agent"""
    print_step("演示 4：交互式研究助手")

    llm = get_llm(temperature=0.3)
    agent = create_react_agent(llm, all_tools)

    print("\n  可用工具：网络搜索、知识库搜索、数学计算")
    print("  输入 'quit' 退出\n")

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
    print_separator("P7: ReAct 研究助手（create_react_agent）")
    print(f"模型: {config.model_name}\n")

    demo_simple_query()
    demo_multi_tool_query()
    demo_stream()
    demo_interactive()

    print("\n✅ P7 演示完成！")
    print("\n💡 create_react_agent 一行代码创建了完整的 Agent，")
    print("   对比 P5 的手动 while 循环，代码量大幅减少。")
    print("\n   运行 python custom_agent.py 查看手动构建版本，理解底层原理。")


if __name__ == "__main__":
    main()
