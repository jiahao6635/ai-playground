# LangChain + LangGraph 渐进式学习路径

## Context

用户希望系统学习 LangChain 和 LangGraph 框架，通过一个一个的代码项目来循序渐进。当前工作区 `/Users/happyelements/workspace/Projects/GitHub/ai-playground` 基本为空（仅有空 README.md）。用户使用 Python，通过自定义 base_url 和模型名连接 OpenAI 兼容 API（如 Ollama、vLLM、DeepSeek 等），对 LangChain 有一定了解但不深入。

本方案设计 10 个渐进式项目，分三个阶段覆盖 LangChain 核心组件和 LangGraph 全部核心能力，总计预计 28-37 小时。

## 技术版本基线

| 组件 | 推荐版本 |
|------|---------|
| Python | >= 3.10（建议 3.11/3.12）|
| langchain | >= 1.0.0 |
| langchain-core | >= 1.0.0 |
| langchain-openai | >= 1.0.0 |
| langchain-community | >= 1.0.0 |
| langchain-text-splitters | >= 1.0.0 |
| langgraph | >= 1.0.0 |
| langgraph-checkpoint-sqlite | >= 2.0.0 |
| pydantic | >= 2.0.0 |
| python-dotenv | >= 1.0.0 |
| faiss-cpu | >= 1.7.0 |

## 目录结构

```
ai-playground/
├── README.md                          # 项目总览与学习指南
├── pyproject.toml                     # 依赖配置
├── .env.example                       # 环境变量模板
├── .gitignore
│
├── common/                            # 公共模块（所有项目复用）
│   ├── __init__.py
│   ├── config.py                      # 配置加载（读取 .env）
│   ├── llm.py                         # LLM 初始化工厂（自定义 base_url）
│   └── utils.py                       # 通用工具函数
│
├── 01-chat-assistant/                 # P1: LLM 对话助手
│   ├── README.md
│   ├── main.py                        # 基础对话
│   └── streaming.py                   # 流式输出
│
├── 02-smart-translator/               # P2: 智能翻译器
│   ├── README.md
│   ├── main.py                        # 模板 + 结构化输出
│   ├── fewshot.py                     # Few-shot 示例
│   └── models.py                      # Pydantic 模型
│
├── 03-text-analyzer/                  # P3: 文本分析管道
│   ├── README.md
│   ├── main.py                        # LCEL 链式调用
│   ├── parallel.py                    # 并行链
│   └── models.py
│
├── 04-knowledge-base/                 # P4: 知识库问答（RAG）
│   ├── README.md
│   ├── main.py                        # RAG 主流程
│   ├── ingest.py                     # 文档加载与索引
│   ├── retriever.py                   # 检索器配置
│   ├── data/                          # 示例文档
│   │   └── sample.txt
│   └── models.py
│
├── 05-tool-assistant/                 # P5: 智能工具助手
│   ├── README.md
│   ├── main.py                        # 工具调用主流程
│   ├── tools.py                      # 工具定义
│   └── models.py
│
├── 06-workflow-engine/                # P6: 文档审批工作流
│   ├── README.md
│   ├── main.py                        # StateGraph 主流程
│   ├── state.py                      # 状态定义
│   └── nodes.py                       # 节点函数
│
├── 07-react-agent/                    # P7: ReAct 研究助手
│   ├── README.md
│   ├── main.py                        # create_react_agent
│   ├── custom_agent.py                # 手动构建 Agent 循环
│   ├── tools.py                       # 研究工具集
│   └── state.py
│
├── 08-persistent-memory/              # P8: 持久化记忆助手
│   ├── README.md
│   ├── main.py                        # 检查点 + 对话记忆
│   ├── checkpointer.py                # 持久化配置
│   └── state.py
│
├── 09-code-approval/                  # P9: 代码审批系统（HITL）
│   ├── README.md
│   ├── main.py                        # interrupt + resume
│   ├── graph.py                       # 工作流图定义
│   ├── tools.py                       # 代码生成/执行工具
│   └── state.py
│
└── 10-dev-team/                       # P10: 多智能体开发团队
    ├── README.md
    ├── main.py                        # Supervisor 编排
    ├── agents/
    │   ├── pm_agent.py                # 产品经理智能体
    │   ├── dev_agent.py               # 开发者智能体
    │   └── tester_agent.py            # 测试员智能体
    ├── supervisor.py                  # 主管路由逻辑
    ├── tools.py
    └── state.py
```

## 公共模块设计

### `.env.example` — 环境变量模板
- `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL_NAME`：LLM 配置
- `EMBEDDING_BASE_URL` / `EMBEDDING_API_KEY` / `EMBEDDING_MODEL_NAME`：Embedding 配置（RAG 项目用）
- 支持任意 OpenAI 兼容 API（Ollama、vLLM、DeepSeek、通义千问、智谱等）

### `common/config.py` — 配置加载
- 使用 `python-dotenv` 从 `.env` 加载
- 提供 `get_llm_config()` 和 `get_embedding_config()` 便捷方法
- 支持环境变量覆盖

### `common/llm.py` — LLM 工厂（核心复用模块）
- `get_llm(temperature=0.7)` → 返回配置好的 `ChatOpenAI` 实例（显式传入 base_url，最高优先级）
- `get_embeddings()` → 返回配置好的 `OpenAIEmbeddings` 实例（RAG 项目复用）
- 所有项目通过 `from common.llm import get_llm` 复用

## 10 个项目详细设计

### Phase 1: LangChain 基础（约 12-16 小时）

---

**P1: LLM 对话助手**（1-2h）
- 学习目标：ChatOpenAI 配置、消息类型（System/Human/AI）、流式输出
- 场景：命令行交互式对话助手，支持多轮对话和流式打字效果
- 核心逻辑：
  - `main.py`：构造消息列表，`llm.invoke(messages)`，维护消息历史实现多轮对话
  - `streaming.py`：`llm.stream(messages)` 逐 token 输出，对比 invoke vs stream
- 组件：`ChatOpenAI`、`SystemMessage`、`HumanMessage`、`AIMessage`

---

**P2: 智能翻译器**（2-3h）
- 学习目标：PromptTemplate、ChatPromptTemplate、Few-shot、Output Parsers、Pydantic 结构化输出
- 场景：多语言翻译器，返回结构化结果（原文、译文、置信度、说明）
- 核心逻辑：
  - `models.py`：Pydantic v2 模型 `TranslationResult`
  - `main.py`：`ChatPromptTemplate.from_messages()` + `llm.with_structured_output(TranslationResult)`
  - `fewshot.py`：`FewShotChatMessagePromptTemplate` 嵌入翻译示例
- 组件：`ChatPromptTemplate`、`FewShotChatMessagePromptTemplate`、`with_structured_output()`、LCEL `|` 管道

---

**P3: 文本分析管道**（2-3h）
- 学习目标：LCEL、Runnable 序列、RunnablePassthrough、RunnableParallel 并行链
- 场景：输入文本，并行进行情感分析、关键词提取、摘要生成，汇总为分析报告
- 核心逻辑：
  - `main.py`：`prompt | llm | StrOutputParser()` 单链，`RunnablePassthrough.assign()` 合并多链
  - `parallel.py`：`RunnableParallel` 同时运行多个分析链，对比串行 vs 并行耗时
- 组件：`RunnableSequence`、`RunnablePassthrough`、`RunnableParallel`、`itemgetter`

---

**P4: 知识库问答（RAG）**（3-4h）
- 学习目标：Document Loaders、Text Splitters、Embeddings、Vector Stores、Retrievers、RAG 链
- 场景：加载本地文档，向量化存储，基于检索结果的问答系统
- 核心逻辑：
  - `ingest.py`：`TextLoader` → `RecursiveCharacterTextSplitter` → `FAISS.from_documents()`
  - `retriever.py`：`FAISS.load_local()` → `as_retriever(search_kwargs={"k": 3})`，对比 similarity vs MMR
  - `main.py`：RAG 链