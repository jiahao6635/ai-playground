"""
state.py — 代码审批系统的状态定义
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class ApprovalState(TypedDict):
    """
    代码审批工作流的状态。

    字段说明：
      messages: 对话历史
      requirement: 用户的代码需求描述
      generated_code: LLM 生成的代码
      review_status: 审查状态 — pending | approved | rejected | modified
      human_feedback: 人工审查反馈
      modified_code: 人工修改后的代码（如果有）
      execution_result: 代码执行结果
      iteration: 迭代次数（防止无限循环）
    """
    messages: Annotated[list, add_messages]
    requirement: str
    generated_code: str
    review_status: str        # pending | approved | rejected | modified
    human_feedback: str
    modified_code: str
    execution_result: str
    iteration: int
