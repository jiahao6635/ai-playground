# P4: 知识库问答（RAG）

> **学习目标**：Document Loaders、Text Splitters、Embeddings、Vector Stores、Retrievers、RAG 链

## 核心概念

### RAG（Retrieval Augmented Generation）

RAG = 检索增强生成，是 LLM 应用最重要的模式之一：

```
用户提问 → 检索相关文档 → 将文档作为上下文 → LLM 基于上下文回答
```

解决了 LLM 的两大问题：知识过时 和 幻觉。

### RAG 流程

```
文档摄入（Ingest）：
  加载文档 → 分割文本 → 生成 Embedding → 存入向量数据库

问答检索（Query）：
  用户问题 → Embedding → 向量检索 → 获取相关文档 → LLM 回答
```

## 运行方式

```bash
# 步骤1：摄入文档（生成向量索引）
python ingest.py

# 步骤2：问答系统
python main.py

# 步骤3：检索器对比（可选）
python retriever.py
```

## 知识点

1. `TextLoader` / `DirectoryLoader` — 加载文档
2. `RecursiveCharacterTextSplitter` — 递归文本分割
3. `OpenAIEmbeddings` — 文本向量化
4. `FAISS` — 向量存储与相似度搜索
5. `as_retriever()` — 将向量库转为检索器
6. LCEL 构建 RAG 链 — `retriever | format | prompt | llm | parser`

## 与下一项目的关系

P4 的 RAG 检索器将在 P5 中作为**工具**被 Agent 调用，实现智能助手的知识库查询能力。
