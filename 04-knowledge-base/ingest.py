"""
P4: 知识库问答 — 文档摄入（Ingest）

学习内容：
  1. TextLoader 加载文本文档
  2. RecursiveCharacterTextSplitter 递归文本分割
  3. OpenAIEmbeddings 文本向量化
  4. FAISS.from_documents() 创建向量存储并保存

运行：python ingest.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.llm import get_embeddings
from common.utils import print_separator, print_step

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


# 路径常量
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
VECTOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vectorstore")


def load_documents():
    """步骤 1：加载文档"""
    print_step("步骤 1：加载文档")

    # TextLoader 加载单个文本文件
    # 返回 Document 对象列表，每个 Document 有 page_content 和 metadata
    file_path = os.path.join(DATA_DIR, "sample.txt")
    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    print(f"  📄 加载文件: {file_path}")
    print(f"  📊 文档数量: {len(documents)}")
    print(f"  📝 总字符数: {sum(len(d.page_content) for d in documents)}")

    # 也可以用 DirectoryLoader 加载整个目录
    # from langchain_community.document_loaders import DirectoryLoader
    # loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    # documents = loader.load()

    return documents


def split_documents(documents):
    """步骤 2：分割文本"""
    print_step("步骤 2：文本分割")

    # ──────────────────────────────────────────────
    # RecursiveCharacterTextSplitter 是最常用的分割器
    # 它递归地按 ["\n\n", "\n", " ", ""] 分隔符分割
    # 尽量保持段落完整性，超长段落再按句子分割
    #
    # 参数说明：
    #   chunk_size: 每个文本块的最大字符数
    #   chunk_overlap: 相邻块的重叠字符数（保持上下文连续性）
    # ──────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # 每块最多 500 字符
        chunk_overlap=50,    # 相邻块重叠 50 字符
        separators=["\n\n", "\n", "。", "，", " ", ""],  # 中文友好的分隔符
    )

    chunks = splitter.split_documents(documents)

    print(f"  ✂️ 分割参数: chunk_size=500, overlap=50")
    print(f"  📊 分割后块数: {len(chunks)}")

    # 展示前两个块
    for i, chunk in enumerate(chunks[:2]):
        preview = chunk.page_content[:80].replace("\n", " ")
        print(f"  📦 块 {i+1}: [{len(chunk.page_content)}字符] {preview}...")

    return chunks


def create_vectorstore(chunks):
    """步骤 3：创建向量存储"""
    print_step("步骤 3：生成 Embedding 并存入 FAISS")

    # 获取 embedding 模型
    embeddings = get_embeddings()

    # ──────────────────────────────────────────────
    # FAISS.from_documents() 做了两件事：
    # 1. 对每个文本块调用 embedding 模型生成向量
    # 2. 将向量和文本存入 FAISS 索引
    # ──────────────────────────────────────────────
    print("  🔄 正在生成 Embedding（可能需要几秒）...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # 保存到本地，下次可以直接加载，不用重新生成
    os.makedirs(VECTOR_DIR, exist_ok=True)
    vectorstore.save_local(VECTOR_DIR)
    print(f"  💾 向量存储已保存到: {VECTOR_DIR}")

    # 验证：简单相似度搜索
    print("\n  🔍 验证搜索：'Python 的数据类型有哪些？'")
    results = vectorstore.similarity_search("Python 的数据类型有哪些？", k=2)
    for i, doc in enumerate(results):
        preview = doc.page_content[:60].replace("\n", " ")
        print(f"     结果 {i+1}: {preview}...")

    return vectorstore


def main():
    print_separator("P4: 文档摄入（Ingest）")
    print("  将本地文档转为向量索引，供问答系统检索\n")

    # 执行完整的摄入流程
    documents = load_documents()
    chunks = split_documents(documents)
    create_vectorstore(chunks)

    print_step("摄入完成！")
    print("  ✅ 文档已成功转换为向量索引")
    print(f"  📁 索引位置: {VECTOR_DIR}")
    print("\n  下一步：运行 python main.py 开始问答\n")


if __name__ == "__main__":
    main()
