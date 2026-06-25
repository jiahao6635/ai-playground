"""
tester_agent.py — 测试员智能体

学习内容：
  1. 智能体执行代码测试
  2. 输出测试结果和反馈
  3. 测试反馈驱动下一轮迭代

Tester 智能体职责：
  接收代码 → 执行测试 → 输出结果 → 更新 state.test_results
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.llm import get_llm

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END


def tester_node(state: dict) -> dict:
    """
    测试员节点：执行代码并评估结果。

    输入：state.code（待测试的代码）
    输出：state.test_results（测试结果）
    """
    llm = get_llm(temperature=0.3)
    code = state.get("code", "")

    # 安全检查
    dangerous = ["import os", "import subprocess", "exec(", "eval(", "open("]
    for d in dangerous:
        if d in code:
            result = f"⚠️ 安全检查未通过：禁止使用 '{d}'"
            return {
                "test_results": result,
                "messages": [AIMessage(content=f"[Tester] {result}")],
            }

    # 尝试执行代码
    try:
        import io
        import contextlib

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            safe_builtins = {
                "print": print, "range": range, "len": len, "sum": sum,
                "min": min, "max": max, "abs": abs, "sorted": sorted,
                "list": list, "dict": dict, "set": set, "tuple": tuple,
                "str": str, "int": int, "float": float, "bool": bool,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
            }
            exec(code, {"__builtins__": safe_builtins})

        execution_output = output.getvalue().strip()

        # 让 LLM 评估测试结果
        eval_prompt = f"""你是测试工程师。代码已执行，请评估测试结果。

代码：
{code}

执行输出：
{execution_output if execution_output else "（无输出）"}

请评估：
1. 代码是否正常执行？
2. 输出是否符合预期？
3. 有无明显 bug？

用简短中文回答。"""

        eval_response = llm.invoke(eval_prompt)
        result = f"执行输出:\n{execution_output}\n\n评估: {eval_response.content}"

        return {
            "test_results": result,
            "messages": [AIMessage(content=f"[Tester] 测试完成:\n{eval_response.content[:200]}...")],
        }

    except Exception as e:
        result = f"❌ 执行失败: {e}"
        return {
            "test_results": result,
            "messages": [AIMessage(content=f"[Tester] {result}")],
        }


def build_tester_subgraph():
    """构建 Tester 智能体子图"""
    workflow = StateGraph(dict)
    workflow.add_node("tester", tester_node)
    workflow.add_edge(START, "tester")
    workflow.add_edge("tester", END)
    return workflow.compile()
