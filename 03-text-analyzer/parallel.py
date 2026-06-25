"""
P3: 文本分析管道 — 并行链演示

学习内容：
  1. RunnableParallel 并行执行多个链
  2. 对比串行 vs 并行执行的耗时
  3. 并行链的数据流和结果合并

RunnableParallel 原理：
  并行执行多个链，每个链的输出合并为字典。
  字典的键是链的名称，值是链的输出。

  {
      "analysis_1": chain_1,
      "analysis_2": chain_2,
  }

  输入 → 同时执行 chain_1 和 chain_2 → {"analysis_1": result1, "analysis_2": result2}

  实际执行中，LangChain 会并行调度（对 LLM 来说，并发发送多个请求）

运行：python parallel.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_llm
from common.utils import print_separator, print_step
from common.config import get_llm_config

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from operator import itemgetter


def demo_sequential():
    """串行执行：依次运行三个分析链"""
    print_step("串行执行（依次运行三个分析）")

    llm = get_llm(temperature=0.3)

    # 三个独立的分析链
    sentiment_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "分析文本情感，只输出一个词：positive/negative/neutral"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    keyword_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "提取3个关键词，逗号分隔"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    summary_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "一句话概括文本"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    text = "人工智能技术正在快速发展，大语言模型在各个领域展现出强大能力，但也引发了关于隐私和就业的担忧。"

    # 串行：一个接一个执行
    start = time.time()
    sentiment = sentiment_chain.invoke({"text": text})
    keywords = keyword_chain.invoke({"text": text})
    summary = summary_chain.invoke({"text": text})
    elapsed = time.time() - start

    print(f"\n  情感:   {sentiment}")
    print(f"  关键词: {keywords}")
    print(f"  摘要:   {summary}")
    print(f"\n  ⏱️ 串行总耗时: {elapsed:.2f}s（3次 LLM 调用依次执行）")

    return elapsed


def demo_parallel():
    """并行执行：使用 RunnableParallel 同时运行三个链"""
    print_step("并行执行（RunnableParallel 同时运行三个分析）")

    llm = get_llm(temperature=0.3)

    sentiment_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "分析文本情感，只输出一个词：positive/negative/neutral"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    keyword_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "提取3个关键词，逗号分隔"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    summary_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "一句话概括文本"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    # ──────────────────────────────────────────────
    # RunnableParallel：并行执行多个链
    # 语法 1：直接传字典
    # ──────────────────────────────────────────────
    parallel_chain = RunnableParallel(
        sentiment=sentiment_chain,
        keywords=keyword_chain,
        summary=summary_chain,
    )

    # ──────────────────────────────────────────────
    # 语法 2：用字典字面量（效果相同）
    # parallel_chain = {
    #     "sentiment": sentiment_chain,
    #     "keywords": keyword_chain,
    #     "summary": summary_chain,
    # }
    # 当字典被放在 | 管道中时，会自动转为 RunnableParallel
    # ──────────────────────────────────────────────

    text = "人工智能技术正在快速发展，大语言模型在各个领域展现出强大能力，但也引发了关于隐私和就业的担忧。"

    # 并行执行
    start = time.time()
    result = parallel_chain.invoke({"text": text})
    elapsed = time.time() - start

    print(f"\n  情感:   {result['sentiment']}")
    print(f"  关键词: {result['keywords']}")
    print(f"  摘要:   {result['summary']}")
    print(f"\n  ⏱️ 并行总耗时: {elapsed:.2f}s（3次 LLM 调用同时进行）")

    return elapsed


def demo_parallel_with_passthrough():
    """RunnableParallel + RunnablePassthrough：并行分析 + 保留原文"""
    print_step("RunnableParallel + RunnablePassthrough 组合")

    llm = get_llm(temperature=0.3)

    sentiment_chain = (
        ChatPromptTemplate.from_messages([
            ("system", "分析情感，只输出一个词"),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )

    # RunnablePassthrough() 透传输入不做处理
    # 用于在并行结果中保留原始输入
    # itemgetter("text") 提取 text 字段
    chain = RunnableParallel(
        original=RunnablePassthrough(),      # 保留原始输入
        sentiment=itemgetter("text") | sentiment_chain,  # 提取 text 后分析
    )

    result = chain.invoke({"text": "今天心情很好！"})

    print(f"\n  原始输入: {result['original']}")
    print(f"  情感分析: {result['sentiment']}")

    print("\n  💡 RunnablePassthrough 保留了完整的原始输入")
    print("     itemgetter('text') 只把 text 字段传给情感分析链")


def main():
    config = get_llm_config()
    print_separator("P3: 并行链演示")
    print(f"模型: {config.model_name}\n")

    # 串行执行
    seq_time = demo_sequential()

    # 并行执行
    par_time = demo_parallel()

    # 对比
    print_step("串行 vs 并行耗时对比")
    speedup = seq_time / par_time if par_time > 0 else 0
    print(f"\n  串行: {seq_time:.2f}s")
    print(f"  并行: {par_time:.2f}s")
    print(f"  加速: {speedup:.1f}x")
    print(f"\n  💡 并行执行将多个独立 LLM 调用同时发送，")
    print(f"     总耗时接近最慢的单次调用，而非所有调用之和。")

    # 组合演示
    demo_parallel_with_passthrough()

    print("\n✅ 并行链演示完成！")


if __name__ == "__main__":
    main()
