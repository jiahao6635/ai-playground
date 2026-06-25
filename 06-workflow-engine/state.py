"""
state.py — 工作流状态定义

学习内容：
  1. TypedDict 定义图状态
  2. 状态在节点间传递和更新
  3. Annotated + reducer 控制状态合并行为

LangGraph 的核心概念：
  State 是在图执行过程中传递的数据容器。
  每个节点接收当前状态，返回状态更新（部分字段）。
  LangGraph 负责将更新合并到状态中。
"""

from typing import TypedDict, Annotated
from operator import add


class WorkflowState(TypedDict):
    """
    文档审批工作流的状态。

    每个字段都会在节点间传递。节点函数接收这个状态，
    返回一个字典（部分字段），LangGraph 自动合并。

    状态合并规则：
      - 默认：新值覆盖旧值
      - Annotated[list, add]：新列表追加到旧列表（而非替换）
    """
    # 文档主题（用户输入，不改变）
    topic: str

    # 当前文档内容（节点更新）
    document: str

    # 草稿版本号（每次修改 +1）
    draft_count: int

    # 审查评分（0-100）
    review_score: int

    # 审查反馈
    review_feedback: str

    # 工作流状态：draft | reviewing | approved | needs_revision | rejected | published
    status: str

    # 修改历史（使用 add reducer 追加而非替换）
    # Annotated[list[str], add] 表示：节点返回的列表会被追加到现有列表
    revision_history: Annotated[list[str], add]
