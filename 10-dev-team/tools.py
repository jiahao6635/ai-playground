"""
tools.py — 多智能体团队的工具集

Dev Agent 可以使用这些工具辅助开发。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool


@tool
def generate_code(spec: str) -> str:
    """根据技术规格生成 Python 代码。

    Args:
        spec: 技术规格描述

    Returns:
        生成的代码
    """
    # 实际代码生成由 LLM 在节点中完成
    # 这个工具作为 Dev Agent 可调用的工具
    return f"# 根据规格生成代码: {spec}"


@tool
def code_review(code: str) -> str:
    """审查代码的质量和安全性。

    Args:
        code: 要审查的代码

    Returns:
        审查结果
    """
    issues = []
    if "eval(" in code:
        issues.append("使用了 eval()，存在安全风险")
    if "exec(" in code:
        issues.append("使用了 exec()，存在安全风险")
    if "import os" in code:
        issues.append("导入了 os 模块")

    if issues:
        return "⚠️ 发现问题:\n" + "\n".join(issues)
    return "✅ 代码审查通过，无明显问题"


@tool
def test_code(code: str) -> str:
    """执行代码并返回结果。

    Args:
        code: 要测试的代码

    Returns:
        测试结果
    """
    try:
        dangerous = ["import os", "import subprocess", "exec(", "eval(", "open("]
        for d in dangerous:
            if d in code:
                return f"⚠️ 安全检查未通过：禁止使用 '{d}'"

        import io
        import contextlib

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            safe_builtins = {
                "print": print, "range": range, "len": len, "sum": sum,
                "min": min, "max": max, "abs": abs, "sorted": sorted,
                "list": list, "dict": dict, "set": set, "tuple": tuple,
                "str": str, "int": int, "float": float, "bool": bool,
                "enumerate": enumerate, "zip": zip,
            }
            exec(code, {"__builtins__": safe_builtins})

        result = output.getvalue().strip()
        return f"✅ 测试通过:\n{result}" if result else "✅ 测试通过（无输出）"
    except Exception as e:
        return f"❌ 测试失败: {e}"


dev_tools = [generate_code, code_review, test_code]
