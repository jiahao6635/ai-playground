"""
state.py — Agent 状态定义

学习内容：
  1. MessagesState — LangGraph 内置的消息状态
  2. add_messages reducer — 消息累加机制
  3. 自定义 Agent 状态

MessagesState 是 LangGraph 提供的内置状态，
包含一个 messages 字段，使用 add_messages reducer。

add_messages 的作用：
  - 新消息追加到消息列表（而非替换）
  - 如果新消息与已有消息 ID 相同，则更新而非追加
"""

from typing import TypedDict, Annotated

# 方式 1：直接使用 LangGraph 内置的 MessagesState
# from langgraph.graph import MessagesState
# MessagesState 内部定义如下：
# class MessagesState(TypedDict):
#     messages: Annotated[list, add_messages]

# 方式 2：自定义状态（扩展 MessagesState 添加额外字段）
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    自定义 Agent 状态。

    messages 字段使用 add_messages reducer：
    - 节点返回的消息会自动追加到列表
    - 而非替换整个列表

    这对 Agent 非常重要：
    Agent 节点返回 AIMessage（含 tool_calls）
    Tool 节点返回 ToolMessage（执行结果）
    这些消息需要不断追加到历史中
    """
    messages: Annotated[list, add_messages]
