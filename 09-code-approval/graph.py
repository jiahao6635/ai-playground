"""
graph.py — 代码审批工作流图定义

学习内容：
  1. interrupt() 暂停图执行
  2. 在节点中等待人工反馈
  3. 条件路由处理人工决策
  4. Command.resume() 恢复执行

工作流结构：
  START → generate → await_review(interrupt) → ┬─ approved → execute → END
                                                ├─ rejected → generate → ...
                                                └─ modified → execute → END

关键点：
  interrupt() 必须配合 checkpointer 使用
  暂停时图的状态被保存到检查点
  恢复时从检查点加载状态继续
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command

from state import ApprovalState


def generate_node(state: ApprovalState) -> dict:
    """
    生成节点：LLM 根据需求生成代码。
    """
    llm = get_llm(temperature=0.3)
    requirement = state["requirement"]
    iteration = state.get("iteration", 0)
    feedback = state.get("human_feedback", "")

    prompt = f"""你是一个 Python 开发者。请根据以下需求生成简洁的 Python 代码。

需求：{requirement}
"""

    if feedback:
        prompt += f"\n之前的代码被拒绝了，反馈：{feedback}\n请根据反馈改进代码。"

    prompt += "\n\n只输出 Python 代码，不要额外解释。用 print() 输出结果以便验证。"

    response = llm.invoke(prompt)

    return {
        "generated_code": response.content,
        "iteration": iteration + 1,
        "review_status": "pending",
        "messages": [response],
    }


def await_review_node(state: ApprovalState) -> dict:
    """
    等待审批节点：暂停图执行，等待人工反馈。

    ──────────────────────────────────────────────
    interrupt() 的核心机制：
    1. 调用 interrupt(value) 时，图执行暂停
    2. value 被传递给调用者（main.py 中的代码）
    3. 调用者处理完后，通过 Command.resume(result) 恢复
    4. result 成为 interrupt() 的返回值
    5. 图从暂停点继续执行
    ──────────────────────────────────────────────
    """
    code = state["generated_code"]
    iteration = state.get("iteration", 1)

    # interrupt 会暂停图执行
    # 传入的值会返回给调用者（main.py）
    # 当调用者调用 Command.resume(result) 时，result 成为这里的返回值
    review_result = interrupt({
        "code": code,
        "iteration": iteration,
        "message": f"请审查第 {iteration} 版代码",
    })

    # ──────────────────────────────────────────────
    # review_result 是 Command.resume(value) 传入的值
    # 格式：{"action": "approve"/"reject"/"modify", "feedback": "...", "code": "..."}
    # ──────────────────────────────────────────────
    action = review_result.get("action", "reject")
    feedback = review_result.get("feedback", "")
    modified_code = review_result.get("code", "")

    status_map = {
        "approve": "approved",
        "reject": "rejected",
        "modify": "modified",
    }

    return {
        "review_status": status_map.get(action, "rejected"),
        "human_feedback": feedback,
        "modified_code": modified_code,
    }


def execute_node(state: ApprovalState) -> dict:
    """
    执行节点：执行通过审批的代码。
    """
    # 如果人工修改了代码，使用修改后的版本
    code = state.get("modified_code") or state["generated_code"]

    # 安全检查
    dangerous = ["import os", "import subprocess", "import shutil", "open(", "exec(", "eval("]
    for d in dangerous:
        if d in code:
            return {"execution_result": f"⚠️ 安全检查未通过：禁止使用 '{d}'"}

    # 执行代码
    try:
        import io
        import contextlib

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            # 限制可用的内置函数
            safe_builtins = {
                "print": print,
                "range": range,
                "len": len,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "sorted": sorted,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
            }
            exec(code, {"__builtins__": safe_builtins})

        result = output.getvalue().strip()
        if result:
            return {"execution_result": f"✅ 执行成功:\n{result}"}
        else:
            return {"execution_result": "✅ 执行成功（无输出）"}
    except Exception as e:
        return {"execution_result": f"❌ 执行失败: {e}"}


def route_after_review(state: ApprovalState) -> str:
    """
    条件路由：根据审批结果决定下一步。
    """
    status = state.get("review_status", "rejected")

    if status == "approved" or status == "modified":
        return "execute"
    elif status == "rejected":
        # 防止无限循环
        if state.get("iteration", 0) >= 3:
            return END
        return "regenerate"
    return END


def build_approval_graph():
    """
    构建代码审批工作流图。

    Returns:
        编译好的 LangGraph 图（带 checkpointer）
    """
    workflow = StateGraph(ApprovalState)

    # 添加节点
    workflow.add_node("generate", generate_node)
    workflow.add_node("await_review", await_review_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("regenerate", generate_node)

    # 边
    workflow.add_edge(START, "generate")
    workflow.add_edge("generate", "await_review")

    # 条件路由：审批后决定下一步
    workflow.add_conditional_edges(
        "await_review",
        route_after_review,
        {
            "execute": "execute",
            "regenerate": "regenerate",
            END: END,
        },
    )

    # 重新生成后再次等待审批
    workflow.add_edge("regenerate", "await_review")

    # 执行后结束
    workflow.add_edge("execute", END)

    # ──────────────────────────────────────────────
    # 关键：必须配置 checkpointer
    # interrupt() 依赖检查点保存暂停状态
    # 没有 checkpointer，interrupt() 会报错
    # ──────────────────────────────────────────────
    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph
