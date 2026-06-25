"""
nodes.py — 工作流节点函数

学习内容：
  1. 节点函数的签名：接收 state，返回更新字典
  2. 节点只返回需要更新的字段（部分更新）
  3. 在节点中使用 LLM 处理逻辑

节点函数规则：
  - 输入：当前完整 state（WorkflowState）
  - 输出：一个字典，只包含需要更新的字段
  - LangGraph 自动将输出合并到 state 中
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm

from state import WorkflowState


def draft_node(state: WorkflowState) -> dict:
    """
    起草节点：根据主题生成文档草稿。

    返回的字典会被合并到 state 中。
    """
    llm = get_llm(temperature=0.7)
    topic = state["topic"]

    response = llm.invoke(
        f"你是一个技术文档撰写者。请为以下主题写一份简短的技术文档（200字以内）：\n\n主题：{topic}"
    )

    return {
        "document": response.content,
        "draft_count": state.get("draft_count", 0) + 1,
        "status": "drafting",
    }


def review_node(state: WorkflowState) -> dict:
    """
    审查节点：LLM 作为审查员评估文档质量。

    返回评分、反馈和状态更新。
    """
    llm = get_llm(temperature=0.3)
    document = state["document"]
    draft_count = state.get("draft_count", 1)

    prompt = f"""你是技术文档审查专家。请审查以下文档并给出评分和反馈。

文档（第{draft_count}版）：
{document}

请按以下格式回答：
评分：[0-100的数字]
反馈：[一句话评价]
决策：[approved 或 needs_revision 或 rejected]

评分标准：
- 90+：优秀，直接通过
- 70-89：合格但需小改，需修改
- 低于70：不合格，需大幅修改或拒绝"""

    response = llm.invoke(prompt)
    content = response.content

    # 解析 LLM 输出（简化版，实际可用结构化输出）
    score = 70  # 默认值
    feedback = "审查完成"
    decision = "needs_revision"

    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("评分"):
            # 提取数字
            import re
            numbers = re.findall(r'\d+', line)
            if numbers:
                score = int(numbers[0])
        elif line.startswith("反馈"):
            feedback = line.split("：", 1)[-1].strip() if "：" in line else line.split(":", 1)[-1].strip()
        elif line.startswith("决策"):
            decision = line.split("：", 1)[-1].strip() if "：" in line else line.split(":", 1)[-1].strip()
            decision = decision.lower()

    # 根据评分确定决策（LLM 的决策可能不完全可靠，用评分做主判断）
    if score >= 85:
        decision = "approved"
    elif score >= 60:
        decision = "needs_revision"
    else:
        decision = "rejected"

    # 记录审查历史
    history_entry = f"第{draft_count}版审查: 评分={score}, 决策={decision}, 反馈={feedback}"

    return {
        "review_score": score,
        "review_feedback": feedback,
        "status": decision,
        "revision_history": [history_entry],
    }


def revise_node(state: WorkflowState) -> dict:
    """
    修改节点：根据审查反馈修改文档。
    """
    llm = get_llm(temperature=0.5)
    document = state["document"]
    feedback = state["review_feedback"]
    draft_count = state.get("draft_count", 1)

    prompt = f"""你是技术文档撰写者。请根据审查反馈修改以下文档。

当前文档（第{draft_count}版）：
{document}

审查反馈：{feedback}

请输出修改后的完整文档（200字以内）。"""

    response = llm.invoke(prompt)

    return {
        "document": response.content,
        "draft_count": draft_count + 1,
        "status": "revising",
    }


def publish_node(state: WorkflowState) -> dict:
    """
    发布节点：文档通过审查，最终发布。
    """
    return {
        "status": "published",
        "revision_history": [f"✅ 第{state.get('draft_count', 1)}版文档已发布！最终评分: {state.get('review_score', 'N/A')}"],
    }
