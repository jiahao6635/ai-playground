"""
P4: 知识库问答 — RAG 主流程

学习内容：
  1. 使用 LCEL 构建 RAG 链
  2. RunnablePassthrough 在 RAG 链中的作用
  3. 带来源引用的问答

RAG 链结构：
  {"context": retriever | format, "question": RunnablePassthrough()}
  | prompt | llm | parser

  1. 用户问题 → retriever 检索相关文档
  2. 文档格式化为文本 → 作为 context
  3. 原始问题 → 作为 question
  4. context + question → prompt → llm → 回答

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
from langchain_core.documents import Document

# 复用本项目的检索器
from retriever import get_retriever, VECTOR_DIR


def format_docs(docs: list[Document]) -> str:
    """将检索到的文档列表格式化为纯文本"""
    return "\n\n".join(
        f"[片段 {i+1}] {doc.page_content}"
        for i, doc in enumerate(docs)
    )


def build_rag_chain():
    """构建 RAG 链"""
    llm = get_llm(temperature=0.3)
    retriever = get_retriever()

    # ──────────────────────────────────────────────
    # RAG 提示模板
    # 关键：告诉 LLM 只基于提供的上下文回答，不要编造
    # ──────────────────────────────────────────────
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个知识库问答助手。请基于以下检索到的上下文回答用户问题。\n\n"
            "规则：\n"
            "1. 只使用上下文中的信息回答，不要编造\n"
            "2. 如果上下文中没有相关信息，诚实回答'根据已有资料无法回答'\n"
            "3. 回答简洁准确\n\n"
            "上下文：\n{context}"
        )),
        ("human", "{question}"),
    ])

    # ──────────────────────────────────────────────
    # 构建 RAG 链（LCEL）
    #
    # 数据流：
    #   输入: "用户问题"
    #   → RunnableParallel 并行处理：
    #       "context": retriever(问题) → format_docs(文档列表) → 字符串
    #       "question": RunnablePassthrough() → 原始问题
    #   → prompt(context + question) → llm → StrOutputParser
    #
    # RunnablePassthrough() 的作用：
    #   透传输入，这里将用户的问题原封不动传给 prompt 的 {question}
    # ──────────────────────────────────────────────
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever


def demo_rag_with_sources():
    """演示：带来源引用的 RAG"""
    print_step("演示：带来源引用的 RAG")

    llm = get_llm(temperature=0.3)
    retriever = get_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你是一个知识库问答助手。基于上下文回答问题。\n"
            "回答末尾列出引用的片段编号。\n\n"
            "上下文：\n{context}"
        )),
        ("human", "{question}"),
    ])

    # 这个链同时返回检索结果和 LLM 回答
    chain = (
        RunnablePassthrough.assign(
            # 先检索文档，保留在 sources 字段
            sources=retriever,
        ).assign(
            # 再用文档格式化后生成回答
            answer=(
                lambda x: format_docs(x["sources"])
            )
            | prompt
            | llm
            | StrOutputParser()
        )
    )

    query = "LangChain 的核心概念有哪些？"
    print(f"\n  🔍 问题: {query}")

    result = chain.invoke(query)

    print(f"\n  🤖 回答:\n  {result['answer']}")

    print(f"\n  📚 检索到的来源（{len(result['sources'])} 个片段）:")
    for i, doc in enumerate(result["sources"]):
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"     片段 {i+1}: {preview}...")


def demo_interactive():
    """交互式问答"""
    print_step("交互式知识库问答")

    chain, retriever = build_rag_chain()

    print("\n  输入 'quit' 退出\n")

    while True:
        question = input("  ❓ 问题: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue

        # 先展示检索到的文档
        docs = retriever.invoke(question)
        print(f"\n  📚 检索到 {len(docs)} 个相关片段")

        # 调用 RAG 链
        try:
            answer = chain.invoke(question)
            print(f"\n  🤖 回答: {answer}\n")
        except Exception as e:
            print(f"\n  ❌ 回答失败: {e}\n")


def main():
    config = get_llm_config()
    print_separator("P4: 知识库问答（RAG）")
    print(f"模型: {config.model_name}\n")

    # 检查向量索引是否存在
    if not os.path.exists(VECTOR_DIR):
        print("  ❌ 向量索引不存在！")
        print("  请先运行: python ingest.py")
        print("  这会将 data/sample.txt 转为向量索引\n")
        return

    # 演示 1：带来源引用
    demo_rag_with_sources()

    # 演示 2：交互式
    demo_interactive()

    print("\n✅ P4 演示完成！")


if __name__ == "__main__":
    main()
