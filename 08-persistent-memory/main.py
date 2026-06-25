"""
P8: 持久化记忆助手 — 检查点 + 对话记忆

学习内容：
  1. compile(checkpointer=...) 为图添加检查点
  2. thread_id 实现多用户会话隔离
  3. 对话摘要压缩长对话历史
  4. get_state() 查看检查点状态
  5. 断点恢复：重启后继续之前的对话

核心演示：
  1. 同一 thread_id 的多次调用，LLM 能记住之前的对话
  2. 不同 thread_id 的对话互相隔离
  3. 消息过多时自动生成摘要

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from state import MemoryState


# 消息超过此数量时触发摘要压缩
SUMMARY_THRESHOLD = 6


def build_memory_agent():
    """构建带记忆的助手图"""
    llm = get_llm(temperature=0.7)

    def chat_node(state: MemoryState) -> dict:
        """
        对话节点：调用 LLM 生成回复。

        如果有摘要，将摘要作为 system 消息加入上下文。
        """
        messages = list(state["messages"])
        summary = state.get("summary", "")

        # 如果有摘要，在消息前插入摘要作为上下文
        if summary:
            # 用摘要替换 system 消息的位置
            system_msg = SystemMessage(
                content=f"之前的对话摘要：{summary}\n\n请基于这个上下文继续对话。"
            )
            # 确保消息以 system 开头
            if messages and isinstance(messages[0], SystemMessage):
                messages[0] = system_msg
            else:
                messages.insert(0, system_msg)

        # 调用 LLM
        response = llm.invoke(messages)
        return {"messages": [response]}

    def summarize_node(state: MemoryState) -> dict:
        """
        摘要节点：当消息过多时，压缩历史对话。

        策略：
        1. LLM 生成之前所有对话的摘要
        2. 用 RemoveMessage 删除旧消息（只保留最近几条）
        3. 摘要保存在 state.summary 中
        """
        messages = state["messages"]
        existing_summary = state.get("summary", "")

        # 构造摘要请求
        summary_prompt = f"请将以下对话总结为简洁的摘要，保留关键信息：\n\n"
        if existing_summary:
            summary_prompt += f"已有摘要：{existing_summary}\n\n新对话：\n"
        for msg in messages[:-2]:  # 不总结最后两条（最近的上下文）
            if not isinstance(msg, SystemMessage):
                summary_prompt += f"{msg.content}\n"

        # 生成摘要
        response = llm.invoke(summary_prompt)
        new_summary = response.content

        # ──────────────────────────────────────────────
        # 使用 RemoveMessage 删除旧消息
        # RemoveMessage(id=msg.id) 会从消息列表中删除指定 ID 的消息
        # 这不是替换，而是告诉 reducer "删除这条消息"
        # ──────────────────────────────────────────────
        delete_messages = [
            RemoveMessage(id=msg.id)
            for msg in messages[:-2]  # 保留最后 2 条消息
            if hasattr(msg, "id") and msg.id
        ]

        return {
            "summary": new_summary,
            "messages": delete_messages,
        }

    def should_summarize(state: MemoryState) -> str:
        """
        条件路由：判断是否需要生成摘要。

        消息超过阈值 → 生成摘要
        否则 → 直接结束
        """
        messages = state["messages"]
        # 只计算 Human 和 AI 消息（不算 system）
        conversation_msgs = [
            m for m in messages
            if not isinstance(m, SystemMessage)
        ]
        if len(conversation_msgs) > SUMMARY_THRESHOLD:
            return "summarize"
        return END

    # ──────────────────────────────────────────────
    # 构建图
    # ──────────────────────────────────────────────
    workflow = StateGraph(MemoryState)

    workflow.add_node("chat", chat_node)
    workflow.add_node("summarize", summarize_node)

    workflow.add_edge(START, "chat")
    workflow.add_conditional_edges(
        "chat",
        should_summarize,
        {
            "summarize": "summarize",
            END: END,
        },
    )
    workflow.add_edge("summarize", END)

    # ──────────────────────────────────────────────
    # 关键：编译时添加 checkpointer
    # 这让图拥有了持久化能力
    # ──────────────────────────────────────────────
    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph


def demo_memory():
    """演示 1：同一会话内的记忆"""
    print_step("演示 1：会话记忆（同一 thread_id）")

    agent = build_memory_agent()

    # ──────────────────────────────────────────────
    # thread_id 是会话的唯一标识
    # 同一 thread_id 的多次调用共享同一个状态
    # 不同 thread_id 的状态互相隔离
    # ──────────────────────────────────────────────
    config = {"configurable": {"thread_id": "session_001"}}

    # 第一轮对话
    print(f"\n  🧑 [第1轮] 我叫张三，是一名 Python 开发者。")
    result = agent.invoke(
        {"messages": [HumanMessage(content="我叫张三，是一名 Python 开发者。")]},
        config=config,
    )
    print(f"  🤖 [第1轮] {result['messages'][-1].content}")

    # 第二轮对话（测试记忆）
    print(f"\n  🧑 [第2轮] 我叫什么名字？做什么工作？")
    result = agent.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？做什么工作？")]},
        config=config,
    )
    print(f"  🤖 [第2轮] {result['messages'][-1].content}")

    print(f"\n  💡 Agent 记住了之前的对话！")
    print(f"     这是因为 checkpointer 自动保存了每次对话后的状态。")


def demo_multi_session():
    """演示 2：多会话隔离"""
    print_step("演示 2：多会话隔离（不同 thread_id）")

    agent = build_memory_agent()

    # 会话 A
    config_a = {"configurable": {"thread_id": "user_alice"}}
    agent.invoke(
        {"messages": [HumanMessage(content="我是 Alice，我喜欢喝咖啡。")]},
        config=config_a,
    )

    # 会话 B
    config_b = {"configurable": {"thread_id": "user_bob"}}
    agent.invoke(
        {"messages": [HumanMessage(content="我是 Bob，我喜欢喝茶。")]},
        config=config_b,
    )

    # 会话 A 继续对话
    result_a = agent.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？喜欢喝什么？")]},
        config=config_a,
    )
    print(f"\n  🧑 Alice 的会话:")
    print(f"  🤖 {result_a['messages'][-1].content}")

    # 会话 B 继续对话
    result_b = agent.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？喜欢喝什么？")]},
        config=config_b,
    )
    print(f"\n  🧑 Bob 的会话:")
    print(f"  🤖 {result_b['messages'][-1].content}")

    print(f"\n  💡 两个会话互不干扰，各自记住各自的对话！")


def demo_get_state():
    """演示 3：查看检查点状态"""
    print_step("演示 3：查看检查点状态")

    agent = build_memory_agent()
    config = {"configurable": {"thread_id": "state_demo"}}

    agent.invoke(
        {"messages": [HumanMessage(content="你好！请介绍一下你自己。")]},
        config=config,
    )

    # ──────────────────────────────────────────────
    # get_state() 返回当前检查点的完整状态
    # 包含 messages 列表和 summary
    # ──────────────────────────────────────────────
    state = agent.get_state(config)

    print(f"\n  📊 当前会话状态:")
    print(f"     消息数量: {len(state.values.get('messages', []))}")
    print(f"     摘要: {state.values.get('summary', '（无）')[:80]}")
    print(f"     下一步: {state.next}")

    print(f"\n  💡 get_state() 让你随时查看当前检查点保存的状态，")
    print(f"     这在调试和监控中非常有用。")


def demo_interactive():
    """演示 4：交互式持久化对话"""
    print_step("演示 4：交互式对话（带记忆）")

    agent = build_memory_agent()
    config = {"configurable": {"thread_id": "interactive"}}

    print("\n  输入 'quit' 退出，输入 'state' 查看当前状态\n")

    while True:
        user_input = input("  🧑 你: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if user_input.lower() == "state":
            state = agent.get_state(config)
            print(f"\n  📊 状态: {len(state.values.get('messages', []))} 条消息")
            summary = state.values.get("summary", "")
            if summary:
                print(f"     摘要: {summary[:80]}...\n")
            else:
                print(f"     摘要: （无）\n")
            continue
        if not user_input:
            continue

        try:
            result = agent.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
            )
            print(f"\n  🤖 AI: {result['messages'][-1].content}\n")
        except Exception as e:
            print(f"\n  ❌ 错误: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P8: 持久化记忆助手")
    print(f"模型: {config.model_name}\n")

    demo_memory()
    demo_multi_session()
    demo_get_state()
    demo_interactive()

    print("\n✅ P8 演示完成！")
    print("\n💡 关键收获：")
    print("   - checkpointer 让图有了持久化能力")
    print("   - thread_id 实现多会话隔离")
    print("   - 对话摘要压缩长对话历史")
    print("   - get_state() 随时查看检查点状态")


if __name__ == "__main__":
    main()
