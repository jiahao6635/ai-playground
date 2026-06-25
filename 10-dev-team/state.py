"""
state.py — 多智能体团队的状态定义

学习内容：
  1. 多字段状态设计
  2. 不同字段的更新策略
"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class TeamState(TypedDict):
    """
    多智能体开发团队的共享状态。

    所有智能体共享这个状态，通过更新不同字段来协作。

    字段说明：
      messages: 对话历史（所有智能体的消息共享）
      requirements: 用户需求（PM 细化后的技术规格）
      code: 开发者生成的代码
      test_results: 测试员的结果
      next_agent: Supervisor 决定的下一个智能体
      iteration: 当前迭代次数
    """
    # 消息历史（所有智能体共享）
    messages: Annotated[list, add_messages]

    # 用户原始需求
    user_request: str

    # PM 细化后的技术规格
    requirements: str

    # Dev 生成的代码
    code: str

    # Tester 的测试结果
    test_results: str

    # Supervisor 决定的下一个智能体
    next_agent: str

    # 迭代次数
    iteration: int
