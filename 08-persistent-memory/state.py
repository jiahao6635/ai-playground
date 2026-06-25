"""
state.py — 持久化记忆助手的状态定义

学习内容：
  1. 带额外字段的 Agent 状态
  2. 对话摘要作为长期记忆
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class MemoryState(TypedDict):
    """
    持久化记忆助手的状态。

    在标准 messages 基础上添加：
      - summary: 对话摘要（压缩历史，节省上下文）
    """
    # 消息历史（add_messages reducer 自动追加）
    messages: Annotated[list, add_messages]

    # 对话摘要（当消息过多时，LLM 自动生成摘要压缩历史）
    summary: str
