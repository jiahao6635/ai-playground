"""
tools.py — 工具定义集合

学习内容：
  1. @tool 装饰器将 Python 函数转为 LangChain 工具
  2. 函数 docstring 自动成为工具描述
  3. 类型注解自动生成参数 schema
  4. 工具内部可以包含任意逻辑
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.tools import tool

# 引入 P4 的知识库检索器作为工具
# 这样 Agent 可以搜索知识库回答问题
try:
    # 将 P4 的目录加入路径
    p4_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "04-knowledge-base")
    sys.path.insert(0, p4_dir)
    from retriever import get_retriever as _get_kb_retriever
    _HAS_KB = True
except Exception:
    _HAS_KB = False


@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气信息。

    Args:
        city: 城市名称，如 "北京"、"上海"、"深圳"

    Returns:
        天气信息字符串
    """
    # 模拟天气 API（实际项目中替换为真实 API 调用）
    weather_data = {
        "北京": "晴，气温 25°C，湿度 40%，风力 3 级",
        "上海": "多云，气温 28°C，湿度 65%，风力 2 级",
        "深圳": "阵雨，气温 30°C，湿度 80%，风力 4 级",
        "广州": "阴，气温 29°C，湿度 70%，风力 2 级",
    }

    result = weather_data.get(city)
    if result:
        return f"📍 {city}天气：{result}"
    else:
        return f"⚠️ 暂无 {city} 的天气数据。支持查询的城市：{', '.join(weather_data.keys())}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式。

    支持基本运算：加(+)、减(-)、乘(*)、除(/)、括号()、幂(**)。

    Args:
        expression: 数学表达式，如 "2 + 3 * 4" 或 "(100 + 50) / 3"

    Returns:
        计算结果字符串
    """
    try:
        # 注意：实际项目中应使用安全的表达式求值方式
        # 这里仅作演示，不要在生产环境中直接 eval 用户输入
        # 安全措施：只允许数字和运算符
        allowed_chars = set("0123456789+-*/().** ")
        if not all(c in allowed_chars for c in expression):
            return f"⚠️ 表达式包含不允许的字符: {expression}"

        result = eval(expression)
        return f"🧮 {expression} = {result}"
    except Exception as e:
        return f"⚠️ 计算失败: {expression}，错误: {e}"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库获取信息。

    可以查询关于 Python、LangChain、LangGraph 等技术主题的知识。

    Args:
        query: 搜索关键词或问题

    Returns:
        检索到的知识内容
    """
    if not _HAS_KB:
        return "⚠️ 知识库未初始化。请先在 04-knowledge-base/ 目录运行 python ingest.py"

    try:
        retriever = _get_kb_retriever()
        docs = retriever.invoke(query)
        if not docs:
            return f"未找到与 '{query}' 相关的内容。"

        # 格式化检索结果
        result = f"📚 检索到 {len(docs)} 条相关内容：\n\n"
        for i, doc in enumerate(docs):
            preview = doc.page_content[:150].replace("\n", " ")
            result += f"[{i+1}] {preview}...\n\n"
        return result
    except Exception as e:
        return f"⚠️ 知识库搜索失败: {e}"


@tool
def get_current_time() -> str:
    """获取当前日期和时间。

    Returns:
        当前时间的格式化字符串
    """
    from datetime import datetime
    now = datetime.now()
    return f"🕐 当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"


# 导出所有工具
all_tools = [get_weather, calculate, search_knowledge, get_current_time]


def print_tool_info():
    """打印工具信息，展示自动生成的 schema"""
    print("  📦 已注册工具：\n")
    for t in all_tools:
        print(f"  🔧 {t.name}")
        print(f"     描述: {t.description}")
        # 打印参数 schema
        if hasattr(t, "args_schema") and t.args_schema:
            schema = t.args_schema.model_json_schema()
            props = schema.get("properties", {})
            required = schema.get("required", [])
            if props:
                print(f"     参数:")
                for name, prop in props.items():
                    req = " (必填)" if name in required else ""
                    print(f"       - {name}: {prop.get('type', 'any')}{req} — {prop.get('description', '')}")
        print()
