## 1. 系统概述
该项目采用 **`python-dotenv`** 结合 **Python `dataclasses`** 的方式构建了一个轻量级、类型安全的集中式配置管理系统。核心逻辑位于 `common/config.py`，通过环境变量（Environment Variables）驱动运行时配置，并利用 `.env.example` 提供标准化的配置模板。

## 2. 核心组件与文件
- **`common/config.py`**: 配置系统的核心。定义了 `LLMConfig` 和 `EmbeddingConfig` 数据类，并提供 `get_llm_config()` 和 `get_embedding_config()` 工厂函数。该模块在导入时自动调用 `load_dotenv()` 加载根目录下的 `.env` 文件。
- **`.env.example`**: 配置模板文件，详细列出了必填项（如 `LLM_BASE_URL`, `LLM_API_KEY`）和可选项（如 `LANGSMITH_API_KEY`），并提供了针对不同服务商（Ollama, DeepSeek, OpenAI 等）的示例值。
- **`pyproject.toml`**: 声明了 `python-dotenv>=1.0.0` 作为项目依赖，确保环境加载功能的可用性。
- **`common/llm.py`**: 配置的消费端。它不直接读取环境变量，而是依赖 `common.config` 提供的配置对象来初始化 `ChatOpenAI` 和 `OpenAIEmbeddings` 实例，实现了配置逻辑与业务逻辑的解耦。

## 3. 架构设计与约定
- **集中化管理**: 所有 10 个渐进式学习项目（从 `01-chat-assistant` 到 `10-dev-team`）均通过 `from common.config import ...` 或 `from common.llm import get_llm` 共享同一套配置源，避免了在每个子项目中重复定义环境变量读取逻辑。
- **默认值与回退机制**: 
  - `get_llm_config()` 为本地开发提供了合理的默认值（如指向 `http://localhost:11434/v1` 的 Ollama 服务）。
  - `get_embedding_config()` 实现了智能回退：如果未显式设置 `EMBEDDING_*` 变量，则自动复用 `LLM_*` 的配置，降低了初学者的配置复杂度。
- **类型安全**: 使用 `@dataclass` 封装配置项，确保了配置对象的结构化访问，避免了直接使用 `os.getenv()` 带来的字符串魔法值和潜在的 Key 拼写错误。
- **错误提示友好**: 在关键配置缺失时（如 `LLM_BASE_URL` 为空），系统会抛出带有明确指导信息的 `ValueError`，引导用户参考 `.env.example` 进行修复。

## 4. 开发者规范
- **配置初始化**: 在运行任何项目前，必须将 `.env.example` 复制为 `.env` 并根据实际使用的 LLM 服务提供商填写相应字段。
- **禁止硬编码**: 严禁在代码中硬编码 API Key 或 Base URL。所有敏感信息和环境相关参数必须通过 `common.config` 模块获取。
- **扩展新配置**: 若需添加新的全局配置（如数据库连接、追踪服务配置），应在 `common/config.py` 中新增对应的 `@dataclass` 和 getter 函数，并保持与现有风格一致（提供默认值、清晰的文档字符串）。
- **模型实例化**: 推荐直接使用 `common.llm.get_llm()` 和 `common.llm.get_embeddings()` 获取已配置好的 LangChain 组件实例，而非手动重新组装 `ChatOpenAI`。