该仓库采用现代 Python 项目标准 `pyproject.toml` 进行依赖管理，未使用传统的 `requirements.txt` 或 `setup.py`。

### 1. 核心系统与工具
- **配置中心**：根目录下的 `pyproject.toml` 是唯一的依赖声明文件。
- **构建后端**：使用 `setuptools` (`setuptools.build_meta`) 作为构建系统。
- **安装方式**：通过 `pip install -e .` 以可编辑模式安装项目及其依赖，便于在沙盒环境中即时修改 `common` 模块并同步到所有子项目。

### 2. 关键依赖包
依赖项集中在 LangChain 生态及必要的辅助库：
- **LangChain 核心**：`langchain`, `langchain-core`, `langchain-openai`, `langchain-community`, `langchain-text-splitters`（均要求 `>=1.0.0`）。
- **LangGraph**：`langgraph` 及 `langgraph-checkpoint-sqlite`（用于持久化记忆）。
- **基础工具**：`pydantic`（结构化输出）、`python-dotenv`（环境变量加载）、`faiss-cpu`（向量检索）。

### 3. 架构与约定
- **共享依赖模型**：所有 10 个渐进式学习项目（`01-*` 到 `10-*`）共享同一套依赖环境，避免了为每个子项目单独维护 `requirements.txt` 的冗余。
- **环境隔离**：`.gitignore` 明确排除了 `venv/`、`.venv/` 和 `.env` 文件，强制开发者在本地创建虚拟环境并自行管理敏感配置。
- **版本策略**：依赖版本采用宽泛的最小版本约束（如 `>=1.0.0`），旨在确保学习者能获取较新的功能特性，但也可能带来潜在的兼容性波动。

### 4. 开发者规范
- **初始化流程**：克隆后需执行 `python -m venv venv` 创建环境，随后运行 `pip install -e .` 统一安装依赖。
- **配置管理**：必须从 `.env.example` 复制并填充 `.env` 文件以提供 LLM API 密钥和端点信息。