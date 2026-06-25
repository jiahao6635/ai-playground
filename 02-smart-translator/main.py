"""
P2: 智能翻译器 — Prompt 模板 + 结构化输出

学习内容：
  1. ChatPromptTemplate 构建聊天提示模板
  2. with_structured_output() 让 LLM 返回 Pydantic 对象
  3. LCEL 管道操作符 | 组合链
  4. StrOutputParser 字符串解析器

运行：python main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 导入本项目定义的 Pydantic 模型
from models import TranslationResult


def demo_string_output():
    """演示 1：基本翻译（字符串输出）"""
    print_step("演示 1：基本翻译（字符串输出）")

    llm = get_llm(temperature=0.3)  # 翻译用低温度，更准确

    # ──────────────────────────────────────────────
    # 构建聊天提示模板
    # ChatPromptTemplate.from_messages() 接收消息元组列表
    # 每个元组格式：(role, content)
    # {variable} 是模板变量，调用时传入
    # ──────────────────────────────────────────────
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个专业翻译。请将用户输入的文本翻译为{target_language}。只输出翻译结果，不要额外解释。"),
        ("human", "{text}"),
    ])

    # LCEL 管道：prompt → llm → parser
    # | 操作符将前一步的输出作为后一步的输入
    # prompt 生成消息 → llm 调用模型 → StrOutputParser 提取字符串
    chain = prompt | llm | StrOutputParser()

    # 调用链：传入模板变量
    result = chain.invoke({
        "text": "人工智能正在改变世界",
        "target_language": "English",
    })

    print(f"\n  原文: 人工智能正在改变世界")
    print(f"  译文: {result}")


def demo_structured_output():
    """演示 2：结构化输出（Pydantic 对象）"""
    print_step("演示 2：结构化输出（Pydantic 对象）")

    llm = get_llm(temperature=0.3)

    # ──────────────────────────────────────────────
    # with_structured_output() 是 LangChain 的核心特性
    # 它让 LLM 直接返回 Pydantic 对象，而非原始字符串
    # 原理：LangChain 会将 Pydantic 模型转为 JSON Schema，
    #       通过 function calling 或 JSON mode 让 LLM 按格式输出
    # ──────────────────────────────────────────────
    structured_llm = llm.with_structured_output(TranslationResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业翻译和语言分析专家。"
            "请将用户的文本翻译为{target_language}，"
            "并分析源语言和翻译置信度。"
            "如有歧义词或多义词，在 notes 中说明你的选择。"
        )),
        ("human", "请翻译以下文本：\n\n{text}"),
    ])

    # 注意：这里不需要 StrOutputParser
    # 因为 with_structured_output 已经让 llm 返回 Pydantic 对象
    chain = prompt | structured_llm

    # 调用链
    result: TranslationResult = chain.invoke({
        "text": "这个苹果很好吃，但那个不行。你是什么意思？",
        "target_language": "English",
    })

    # result 是 TranslationResult 对象，可以直接访问字段
    print(f"\n  源语言:   {result.source_language}")
    print(f"  目标语言: {result.target_language}")
    print(f"  原文:     {result.original_text}")
    print(f"  译文:     {result.translated_text}")
    print(f"  置信度:   {result.confidence:.0%}")
    print(f"  说明:     {result.notes}")

    print("\n  💡 结构化输出的优势：")
    print("     - 返回的是 Pydantic 对象，可直接访问字段")
    print("     - 类型安全，避免手动解析 JSON 字符串")
    print("     - 字段有验证（如 confidence 在 0-1 之间）")


def demo_interactive():
    """演示 3：交互式翻译器"""
    print_step("演示 3：交互式翻译器（结构化输出）")

    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(TranslationResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个专业翻译和语言分析专家。"
            "请将用户的文本翻译为{target_language}，"
            "并分析源语言和翻译置信度。"
            "如有歧义词或多义词，在 notes 中说明你的选择。"
        )),
        ("human", "请翻译以下文本：\n\n{text}"),
    ])

    chain = prompt | structured_llm

    print("\n  输入 'quit' 退出")
    print("  格式：文本 | 目标语言（默认 English）")
    print("  示例：你好世界 | Japanese\n")

    while True:
        user_input = input("  📝 输入: ").strip()
        if user_input.lower() in ("quit", "exit"):
            break
        if not user_input:
            continue

        # 解析输入：文本 | 目标语言
        parts = user_input.split("|")
        text = parts[0].strip()
        target = parts[1].strip() if len(parts) > 1 else "English"

        try:
            result: TranslationResult = chain.invoke({
                "text": text,
                "target_language": target,
            })
            print(f"\n  🌐 {result.source_language} → {result.target_language}")
            print(f"  📖 原文: {result.original_text}")
            print(f"  ✅ 译文: {result.translated_text}")
            print(f"  📊 置信度: {result.confidence:.0%}")
            if result.notes:
                print(f"  💡 说明: {result.notes}")
            print()
        except Exception as e:
            print(f"\n  ❌ 翻译失败: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P2: 智能翻译器")
    print(f"模型: {config.model_name}\n")

    # 演示 1：基本字符串翻译
    demo_string_output()

    # 演示 2：结构化输出
    demo_structured_output()

    # 演示 3：交互式
    demo_interactive()

    print("\n✅ P2 演示完成！")


if __name__ == "__main__":
    main()
