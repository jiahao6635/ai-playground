"""
P4: 知识库问答 — 检索器配置

学习内容：
  1. 从本地加载 FAISS 索引
  2. as_retriever() 将向量库转为检索器
  3. 对比 similarity search vs MMR 检索策略

运行：python retriever.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_embeddings
from common.utils import print_separator, print_step
from common.config import get_embedding_config

from langchain_community.vectorstores import FAISS

VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorstore")


def load_vectorstore():
    """加载已保存的 FAISS 索引"""
    embeddings = get_embeddings()

    # ──────────────────────────────────────────────
    # FAISS.load_local() 从本地加载之前保存的索引
    # allow_dangerous_deserialization=True 允许加载 pickle 格式
    # FAISS 索引包含 .faiss（向量数据）和 .pkl（元数据）两个文件
    # ──────────────────────────────────────────────
    vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return vectorstore


def demo_similarity_search():
    """演示 1：直接相似度搜索"""
    print_step("演示 1：相似度搜索（similarity）")

    vectorstore = load_vectorstore()

    # 直接调用 similarity_search 方法
    query = "LangChain 有哪些核心概念？"
    print(f"\n  🔍 查询: {query}")

    results = vectorstore.similarity_search(query, k=3)

    for i, doc in enumerate(results):
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"\n  结果 {i+1}: {preview}...")


def demo_retriever():
    """演示 2：使用 Retriever 接口"""
    print_step("演示 2：Retriever 接口")

    vectorstore = load_vectorstore()

    # ──────────────────────────────────────────────
    # as_retriever() 将向量库转为检索器
    # Retriever 是 LangChain 的标准检索接口
    # 可以在 LCEL 链中使用，更灵活
    #
    # search_type 参数：
    #   "similarity" — 纯相似度搜索（默认）
    #   "mmr" — 最大边际相关性，平衡相关性和多样性
    # ──────────────────────────────────────────────
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},  # 返回 top-3 结果
    )

    query = "如何安装 Python？"
    print(f"\n  🔍 查询: {query}")

    # Retriever 通过 invoke 调用
    results = retriever.invoke(query)

    for i, doc in enumerate(results):
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"  结果 {i+1}: {preview}...")


def demo_mmr():
    """演示 3：MMR（最大边际相关性）检索"""
    print_step("演示 3：MMR 检索（平衡相关性和多样性）")

    vectorstore = load_vectorstore()

    # ──────────────────────────────────────────────
    # MMR (Maximal Marginal Relevance) 策略：
    #   1. 先检索 top-k 个相关文档
    #   2. 从中选出与查询相关但又彼此不重复的文档
    #   避免返回内容过于相似的多个块
    #
    # 参数：
    #   fetch_k: 初始检索的候选数量
    #   lambda_mult: 0=最大多样性, 1=最大相关性
    # ──────────────────────────────────────────────
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 3,
            "fetch_k": 10,
            "lambda_mult": 0.5,
        },
    )

    query = "什么是 Python？"
    print(f"\n  🔍 查询: {query}")
    print(f"  策略: MMR (平衡相关性和多样性)")

    results = retriever.invoke(query)
    for i, doc in enumerate(results):
        preview = doc.page_content[:80].replace("\n", " ")
        print(f"  结果 {i+1}: {preview}...")

    print("\n  💡 MMR 避免返回内容重复的文档块，结果更多样")


def get_retriever():
    """
    获取配置好的检索器（供 main.py 复用）

    Returns:
        配置好的 Retriever 实例
    """
    vectorstore = load_vectorstore()
    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
    )


def main():
    config = get_embedding_config()
    print_separator("P4: 检索器演示")
    print(f"Embedding 模型: {config.model_name}\n")

    if not os.path.exists(VECTOR_DIR):
        print("  ❌ 向量索引不存在！请先运行: python ingest.py")
        return

    demo_similarity_search()
    demo_retriever()
    demo_mmr()

    print("\n✅ 检索器演示完成！")


if __name__ == "__main__":
    main()
