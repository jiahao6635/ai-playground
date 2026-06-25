# AI Playground — LangChain + LangGraph 渐进式学习路径

通过 **10 个渐进式项目**，从零开始系统学习 LangChain 和 LangGraph 框架。

## 快速开始

```bash
# 1. 克隆项目
cd ai-playground

# 2. 安装 uv（如未安装）
# macOS:   brew install uv
# Linux:   curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. 安装依赖（uv 会自动创建 .venv 虚拟环境）
uv sync

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 LLM base_url 和模型名

# 5. 验证连通性
uv run python -c "from common.llm import get_llm; print(get_llm().invoke('你好').content)"
```

## 学习路径总览

### Phase 1: LangChain 基础（约 12-16 小时）

| # | 项目 | 学习目标 | 预计耗时 |
|---|------|---------|---------|
| 1 | [LLM 对话助手](01-chat-assistant/) | ChatOpenAI 配置、消息类型、流式输出 | 1-2h |
| 2 | [智能翻译器](02-smart-translator/) | Prompt 模板、Few-shot、结构化输出 | 2-3h |
| 3 | [文本分析管道](03-text-analyzer/) | LCEL 链式调用、并行链、Runnable | 2-3h |
| 4 | [知识库问答 (RAG)](04-knowledge-base/) | 文档加载、向量检索、RAG 链 | 3-4h |
| 5 | [智能工具助手](05-tool-assistant/) | 工具定义、bind_tools、工具调用循环 | 3-4h |

### Phase 2: LangGraph 基础（约 6-8 小时）

| # | 项目 | 学习目标 | 预计耗时 |
|---|------|---------|---------|
| 6 | [文档审批工作流](06-workflow-engine/) | StateGraph、状态、条件路由 | 3-4h |
| 7 | [ReAct 研究助手](07-react-agent/) | Agent 循环、ToolNode、create_react_agent | 3-4h |

### Phase 3: LangGraph 高级（约 10-13 小时）

| # | 项目 | 学习目标 | 预计耗时 |
|---|------|---------|---------|
| 8 | [持久化记忆助手](08-persistent-memory/) | Checkpointing、thread_id 会话管理 | 3-4h |
| 9 | [代码审批系统 (HITL)](09-code-approval/) | interrupt/resume、Human-in-the-Loop | 3-4h |
| 10 | [多智能体开发团队](10-dev-team/) | Supervisor 编排、子图、流式输出 | 4-5h |

## 知识图谱

```
Phase 1: LangChain 基础
  P1 对话助手 → P2 翻译器 → P3 文本分析 → P4 RAG → P5 工具调用
  (LLM基础)    (Prompt)    (LCEL链)    (检索增强)  (工具调用)
                          │
                  掌握 LangChain 核心
                  理解 Runnable 协议
                          │
Phase 2: LangGraph 基础         ▼
  P6 审批工作流 → P7 ReAct Agent
  (StateGraph)    (Agent循环)
              │
      掌握 State/Node/Edge
      理解条件路由和循环
              │
Phase 3: LangGraph 高级         ▼
  P8 持久化记忆 → P9 代码审批 → P10 多智能体团队
  (Checkpoint)   (HITL)       (Multi-Agent)
```

## 配置说明

在 `.env` 文件中配置你的 LLM 和 Embedding 模型。支持任意 OpenAI 兼容 API：

| 提供商 | LLM_BASE_URL | LLM_MODEL_NAME |
|--------|-------------|----------------|
| 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |

> **注意**：本地小模型（如 7B）在工具调用和结构化输出时可能不稳定，P5/P7/P10 建议 14B+ 模型或 API 级模型。

## 项目结构

```
ai-playground/
├── common/              # 公共模块（所有项目复用）
│   ├── config.py        #   配置加载
│   ├── llm.py           #   LLM 初始化工厂
│   └── utils.py         #   通用工具
├── 01-chat-assistant/   # P1: LLM 对话助手
├── 02-smart-translator/ # P2: 智能翻译器
├── 03-text-analyzer/    # P3: 文本分析管道
├── 04-knowledge-base/   # P4: 知识库问答 (RAG)
├── 05-tool-assistant/   # P5: 智能工具助手
├── 06-workflow-engine/  # P6: 文档审批工作流
├── 07-react-agent/      # P7: ReAct 研究助手
├── 08-persistent-memory/ # P8: 持久化记忆助手
├── 09-code-approval/    # P9: 代码审批系统 (HITL)
└── 10-dev-team/         # P10: 多智能体开发团队
```
# ai-playground