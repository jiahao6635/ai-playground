"""
P5: 智能工具助手 — 工具调用主流程

学习内容：
  1. bind_tools() 将工具绑定到 LLM
  2. 检查 response.tool_calls 获取工具调用请求
  3. 手动实现工具调用循环：LLM → 工具 → LLM → 回复
  4. ToolMessage 回传工具执行结果

工具调用循环（核心模式）：
  while True:
      1. LLM 生成回复（可能包含 tool_calls）
      2. 如果没有 tool_calls → 返回最终回复
      3. 如果有 tool_calls → 执行工具 → 结果作为 ToolMessage 回传 → 回到 1

这个手动循环是理解 LangGraph Agent 的关键前置知识。
在 P7 中，LangGraph 用 StateGraph 优雅地实现了同样的循环。

运行：python main.py
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)

from tools import all_tools, print_tool_info


def run_agent(llm, tools, user_input: str) -> str:
    """
    手动实现工具调用循环。

    这是理解 Agent 核心机制的关键代码：
    LLM 决定是否调用工具 → 执行工具 → 结果回传 → LLM 再次决策

    Args:
        llm: 绑定了工具的 LLM 实例
        tools: 工具列表
        user_input: 用户输入

    Returns:
        最终回复文本
    """
    # 构建工具映射（名称 → 工具函数），方便快速查找
    tool_map = {t.name: t for t in tools}

    # 初始化消息历史
    messages = [
        SystemMessage(content=(
            "你是一个智能助手，可以使用工具来帮助用户。"
            "当需要查询天气、计算数学、搜索知识库或获取时间时，调用相应工具。"
            "工具执行后，基于工具结果给出简洁的回答。"
        )),
        HumanMessage(content=user_input),
    ]

    # ──────────────────────────────────────────────
    # 工具调用循环
    # 最多迭代 10 次，防止无限循环
    # ──────────────────────────────────────────────
    for iteration in range(10):
        # 1. 调用 LLM
        response: AIMessage = llm.invoke(messages)

        # 2. 检查是否有工具调用
        if not response.tool_calls:
            # 没有工具调用 → LLM 已经准备好最终回复
            return response.content

        # 3. 有工具调用 → 打印 LLM 的决策
        for tc in response.tool_calls:
            print(f"\n  🔧 LLM 决定调用工具: {tc['name']}({tc['args']})")

        # 将 AI 消息（含 tool_calls）加入历史
        messages.append(response)

        # 4. 执行每个工具调用
        for tc in response.tool_calls:
            tool_name = tc["name"]
            tool_args = tc["args"]
            tool_call_id = tc["id"]

            # 查找并执行工具
            if tool_name in tool_map:
                print(f"  ⚙️ 执行 {tool_name}...")
                result = tool_map[tool_name].invoke(tool_args)
                print(f"  ✅ 结果: {str(result)[:100]}")
            else:
                result = f"工具 {tool_name} 不存在"
                print(f"  ❌ {result}")

            # 5. 将工具结果作为 ToolMessage 回传给 LLM
            # ToolMessage 必须包含 tool_call_id 以关联到对应的工具调用
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call_id,
            ))

        # 循环回到步骤 1：LLM 会收到工具结果，决定是否继续调用工具

    return "⚠️ 工具调用次数超过限制"


def demo_single_tool():
    """演示 1：单次工具调用"""
    print_step("演示 1：单次工具调用")

    llm = get_llm(temperature=0.3)

    # bind_tools 将工具列表绑定到 LLM
    # LLM 会知道有哪些工具可用、每个工具的参数
    llm_with_tools = llm.bind_tools(all_tools)

    result = run_agent(llm_with_tools, all_tools, "北京今天天气怎么样？")
    print(f"\n  🤖 最终回复: {result}")


def demo_multi_tool():
    """演示 2：多次工具调用"""
    print_step("演示 2：多次工具调用（先查天气再计算）")

    llm = get_llm(temperature=0.3)
    llm_with_tools = llm.bind_tools(all_tools)

    # LLM 需要先查天气，再基于天气信息做其他推理
    result = run_agent(llm_with_tools, all_tools, "帮我查一下北京和上海的天气，然后对比两地的温度差是多少度。")
    print(f"\n  🤖 最终回复: {result}")


def demo_knowledge_search():
    """演示 3：知识库搜索工具"""
    print_step("演示 3：知识库搜索工具")

    llm = get_llm(temperature=0.3)
    llm_with_tools = llm.bind_tools(all_tools)

    result = run_agent(llm_with_tools, all_tools, "LangChain 的核心概念有哪些？请搜索知识库。")
    print(f"\n  🤖 最终回复: {result}")


def demo_interactive():
    """演示 4：交互式工具助手"""
    print_step("演示 4：交互式工具助手")

    llm = get_llm(temperature=0.3)
    llm_with_tools = llm.bind_tools(all_tools)

    print("\n  可用工具：天气查询、数学计算、知识库搜索、时间查询")
    print("  输入 'quit' 退出\n")

    while True:
        user_input = input("  🧑 你: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        try:
            result = run_agent(llm_with_tools, all_tools, user_input)
            print(f"\n  🤖 AI: {result}\n")
        except Exception as e:
            print(f"\n  ❌ 错误: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P5: 智能工具助手")
    print(f"模型: {config.model_name}\n")

    # 展示工具信息
    print_step("已注册的工具")
    print_tool_info()

    # 运行演示
    demo_single_tool()
    demo_multi_tool()
    demo_knowledge_search()
    demo_interactive()

    print("\n✅ P5 演示完成！")
    print("\n💡 下一步：P6 将进入 LangGraph，学习如何用 StateGraph 构建工作流。")
    print("   P7 将展示 LangGraph 如何优雅地实现同样的工具调用循环。")


if __name__ == "__main__":
    main()
