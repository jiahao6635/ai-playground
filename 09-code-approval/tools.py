"""
tools.py — 代码生成与执行工具

学习内容：
  1. 代码生成工具（LLM 生成 Python 代码）
  2. 代码执行工具（安全的代码执行模拟）
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool


@tool
def generate_code(requirement: str) -> str:
    """根据需求描述生成 Python 代码。

    Args:
        requirement: 代码需求描述，如 "写一个快速排序函数"

    Returns:
        生成的 Python 代码字符串
    """
    # 这个工具实际由 LLM 调用
    # 这里返回占位符，实际代码生成在 graph.py 的节点中完成
    return f"# 将根据需求生成代码: {requirement}"


@tool
def execute_code(code: str) -> str:
    """安全地执行 Python 代码并返回结果。

    Args:
        code: 要执行的 Python 代码

    Returns:
        执行结果或错误信息
    """
    # 模拟代码执行（实际项目中应使用沙箱环境）
    try:
        # 安全检查：禁止危险操作
        dangerous = ["import os", "import subprocess", "import shutil", "rm ", "open("]
        for d in dangerous:
            if d in code:
                return f"⚠️ 安全检查未通过：禁止使用 '{d}'"

        # 尝试执行（捕获输出）
        import io
        import contextlib

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, {"__builtins__": {}})  # 限制内置函数

        result = output.getvalue().strip()
        if result:
            return f"✅ 执行成功:\n{result}"
        else:
            return "✅ 执行成功（无输出）"
    except Exception as e:
        return f"❌ 执行失败: {e}"
