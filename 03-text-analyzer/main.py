"""
P3: 文本分析管道 — LCEL 链式调用

学习内容：
  1. LCEL 管道操作符 | 组合链
  2. RunnablePassthrough 透传输入
  3. RunnablePassthrough.assign() 追加字段到数据流
  4. with_structured_output() 结构化输出
  5. itemgetter 从字典提取字段

场景：输入一段文本，依次进行情感分析、关键词提取、摘要生成，
     最终汇总为结构化分析报告。

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
from langchain_core.runnables import RunnablePassthrough

from models import AnalysisReport, SentimentResult, KeywordResult


def demo_single_chain():
    """演示 1：单条链 — 情感分析"""
    print_step("演示 1：单条链（情感分析）")

    llm = get_llm(temperature=0.3)

    # 基本链：prompt | llm | parser
    # 输入 {"text": "..."} → prompt 格式化 → llm 生成 → parser 提取字符串
    prompt = ChatPromptTemplate.from_messages([
        ("system", "分析以下文本的情感倾向，用中文简洁回答。"),
        ("human", "{text}"),
    ])

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({
        "text": "今天天气真好，阳光明媚，心情非常愉快！",
    })
    print(f"\n  结果: {result}")


def demo_structured_chain():
    """演示 2：结构化输出链"""
    print_step("演示 2：结构化输出链（Pydantic）")

    llm = get_llm(temperature=0.3)

    # with_structured_output 让链直接返回 Pydantic 对象
    structured_llm = llm.with_structured_output(SentimentResult)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是情感分析专家。分析文本的情感倾向、分值和理由。"),
        ("human", "{text}"),
    ])

    # 链：prompt | structured_llm
    # 不需要 parser，因为 structured_llm 已经返回 Pydantic 对象
    chain = prompt | structured_llm

    result: SentimentResult = chain.invoke({
        "text": "产品体验极差，客服态度恶劣，再也不买了。",
    })

    print(f"\n  情感: {result.sentiment}")
    print(f"  分值: {result.score}")
    print(f"  理由: {result.explanation}")


def demo_assign_chain():
    """演示 3：RunnablePassthrough.assign() — 多步分析汇总"""
    print_step("演示 3：RunnablePassthrough.assign() 多步分析")

    llm = get_llm(temperature=0.3)

    # ──────────────────────────────────────────────
    # RunnablePassthrough.assign() 的作用：
    #   接收输入，执行传入的链，将结果作为新字段追加到输出中
    #
    # 数据流：
    #   {"text": "..."}
    #   → assign(sentiment=情感分析链) → {"text": "...", "sentiment": "..."}
    #   → assign(keywords=关键词链)   → {"text": "...", "sentiment": "...", "keywords": "..."}
    #   → assign(summary=摘要链)      → {"text": "...", "sentiment": "...", "keywords": "...", "summary": "..."}
    # ──────────────────────────────────────────────

    # 情感分析链
    sentiment_prompt = ChatPromptTemplate.from_messages([
        ("system", "分析文本情感，只输出一个词：positive / negative / neutral"),
        ("human", "{text}"),
    ])
    sentiment_chain = sentiment_prompt | llm | StrOutputParser()

    # 关键词提取链
    keyword_prompt = ChatPromptTemplate.from_messages([
        ("system", "提取文本中的3个关键词，用逗号分隔，只输出关键词"),
        ("human", "{text}"),
    ])
    keyword_chain = keyword_prompt | llm | StrOutputParser()

    # 摘要链
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "用一句话概括文本内容"),
        ("human", "{text}"),
    ])
    summary_chain = summary_prompt | llm | StrOutputParser()

    # 使用 assign 逐步追加结果
    # itemgetter("text") 从输入字典中提取 text 字段
    from operator import itemgetter

    full_chain = RunnablePassthrough.assign(
        sentiment=sentiment_chain,  # 自动从输入中取 text
    ).assign(
        keywords=keyword_chain,
    ).assign(
        summary=summary_chain,
    )

    # 也可以用 itemgetter 精确控制传递给每个子链的输入
    # full_chain = (
    #     RunnablePassthrough.assign(
    #         sentiment=itemgetter("text") | sentiment_chain,
    #     )
    #     ...

    result = full_chain.invoke({
        "text": "这家餐厅的菜品味道不错，环境也很好，就是价格有点贵。整体来说值得一试。",
    })

    print(f"\n  原文:   {result['text']}")
    print(f"  情感:   {result['sentiment']}")
    print(f"  关键词: {result['keywords']}")
    print(f"  摘要:   {result['summary']}")

    print("\n  💡 assign() 的数据流：每一步都在前一步的基础上追加字段")
    print("     最终结果包含所有中间步骤的输出")


def demo_full_report():
    """演示 4：完整分析报告（结构化）"""
    print_step("演示 4：完整分析报告（结构化输出）")

    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(AnalysisReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是文本分析专家。对输入文本进行全面分析，包括：\n"
            "1. 情感倾向（positive/negative/neutral）和分值（-1到1）\n"
            "2. 关键词（3-5个）\n"
            "3. 一句话摘要\n"
            "4. 文本分类（如：产品评价、新闻报道、技术文档等）"
        )),
        ("human", "{text}"),
    ])

    chain = prompt | structured_llm

    texts = [
        "这款手机性能强劲，拍照效果出色，但电池续航一般。整体来说是一款值得推荐的产品。",
        "公司第三季度营收同比下降15%，主要受市场需求疲软和竞争加剧影响，管理层表示正在调整战略。",
    ]

    for text in texts:
        report: AnalysisReport = chain.invoke({"text": text})
        print(f"\n  原文: {text}")
        print(f"  情感: {report.sentiment} (分值: {report.sentiment_score})")
        print(f"  关键词: {', '.join(report.keywords)}")
        print(f"  摘要: {report.summary}")
        print(f"  分类: {report.category}")


def demo_interactive():
    """演示 5：交互式文本分析"""
    print_step("演示 5：交互式文本分析")

    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(AnalysisReport)

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是文本分析专家。对输入文本进行全面分析，包括：\n"
            "1. 情感倾向和分值\n"
            "2. 关键词\n"
            "3. 摘要\n"
            "4. 文本分类"
        )),
        ("human", "{text}"),
    ])
    chain = prompt | structured_llm

    print("\n  输入 'quit' 退出\n")

    while True:
        text = input("  📝 输入文本: ").strip()
        if text.lower() in ("quit", "exit"):
            break
        if not text:
            continue

        try:
            report: AnalysisReport = chain.invoke({"text": text})
            print(f"\n  📊 分析报告:")
            print(f"     情感: {report.sentiment} (分值: {report.sentiment_score})")
            print(f"     关键词: {', '.join(report.keywords)}")
            print(f"     摘要: {report.summary}")
            print(f"     分类: {report.category}\n")
        except Exception as e:
            print(f"\n  ❌ 分析失败: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P3: 文本分析管道")
    print(f"模型: {config.model_name}\n")

    demo_single_chain()
    demo_structured_chain()
    demo_assign_chain()
    demo_full_report()
    demo_interactive()

    print("\n✅ P3 演示完成！")


if __name__ == "__main__":
    main()
