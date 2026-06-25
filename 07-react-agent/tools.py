"""
tools.py — 研究助手工具集

复用 P5 的工具定义，加上一些研究场景的工具。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool

# 尝试引入 P4 的知识库检索器
try:
    p4_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "04-knowledge-base")
    sys.path.insert(0, p4_dir)
    from retriever import get_retriever as _get_kb_retriever
    _HAS_KB = True
except Exception:
    _HAS_KB = False


@tool
def web_search(query: str) -> str:
    """搜索网络获取信息。

    可以搜索最新资讯、技术文档、百科知识等。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要
    """
    # 模拟网络搜索（实际项目中接入搜索 API，如 Tavily、SerpAPI）
    mock_results = {
        "langchain": "LangChain 是一个用于构建 LLM 应用的开源框架，支持 Python 和 JS。最新版本 1.x 引入了多项改进。",
        "python": "Python 3.12 已发布，引入了更快的启动速度和改进的错误提示。Python 是最流行的编程语言之一。",
        "ai": "2024年 AI 领域快速发展，大语言模型在多模态、推理和 Agent 方向取得重大进展。",
    }

    # 简单关键词匹配
    for key, value in mock_results.items():
        if key in query.lower():
            return f"🔍 搜索 '{query}' 的结果：\n{value}"

    return f"🔍 搜索 '{query}' 的结果：\n未找到完全匹配的结果。请尝试更具体的关键词。"


@tool
def knowledge_search(query: str) -> str:
    """搜索本地知识库获取技术信息。

    可以查询关于 Python、LangChain、LangGraph 等技术主题的详细知识。

    Args:
        query: 搜索问题

    Returns:
        知识库中检索到的内容
    """
    if not _HAS_KB:
        return "⚠️ 知识库未初始化。请先在 04-knowledge-base/ 目录运行 python ingest.py"

    try:
        retriever = _get_kb_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return f"未找到与 '{query}' 相关的内容。"

        result = f"📚 检索到 {len(docs)} 条相关内容：\n\n"
        for i, doc in enumerate(docs):
            preview = doc.page_content[:200].replace("\n", " ")
            result += f"[{i+1}] {preview}...\n\n"
        return result
    except Exception as e:
        return f"⚠️ 知识库搜索失败: {e}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    支持基本运算：加(+)、减(-)、乘(*)、除(/)、括号()、幂(**)。

    Args:
        expression: 数学表达式，如 "2 + 3 * 4"

    Returns:
        计算结果
    """
    try:
        allowed = set("0123456789+-*/().** ")
        if not all(c in allowed for c in expression):
            return f"⚠️ 表达式包含不允许的字符: {expression}"
        result = eval(expression)
        return f"🧮 {expression} = {result}"
    except Exception as e:
        return f"⚠️ 计算失败: {e}"


# 导出所有工具
all_tools = [web_search, knowledge_search, calculate]
