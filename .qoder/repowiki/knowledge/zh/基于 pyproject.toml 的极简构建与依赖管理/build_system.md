该仓库采用 Python 原生的 `pyproject.toml` 作为唯一的构建与依赖管理核心，未引入复杂的 CI/CD 流水线、容器化方案或自动化测试框架。

### 1. 构建系统与工具链
- **构建后端**：使用 `setuptools` (`setuptools.build_meta`) 作为标准的 Python 构建后端。
- **依赖管理**：通过 `[project]` 字段声明项目元数据及运行时依赖（如 `langchain`, `langgraph`, `pydantic` 等）。
- **安装方式**：开发者需手动创建虚拟环境并通过 `pip install -e .` 进行可编辑安装，以支持本地开发与模块引用。

### 2. 关键配置文件
- `pyproject.toml`: 定义项目名称 `ai-playground`、Python 版本要求 (`>=3.10`) 以及所有第三方库的版本约束。
- `.env.example`: 提供环境变量模板，指导开发者配置 LLM API 地址与密钥，是运行沙盒的必要前置步骤。
- `.gitignore`: 明确了 Python 缓存、虚拟环境目录 (`venv/`)、敏感配置 (`.env`) 及运行时产生的向量索引文件 (`*.faiss`) 等忽略规则。

### 3. 架构约定与开发流程
- **模块化组织**：项目采用“渐进式沙盒”架构，包含 10 个独立的学习模块（`01-` 至 `10-`）和一个共享的 `common` 公共模块。`pyproject.toml` 中显式声明 `packages = ["common"]`，确保公共工具能被各子项目正确导入。
- **无自动化测试/CI**：仓库中未发现 `tests/` 目录、`pytest` 配置或 GitHub Actions 工作流。质量保障依赖于开发者手动运行各模块的 `main.py` 脚本进行功能验证。
- **环境隔离**：强烈依赖本地虚拟环境，所有运行时产生的状态（如 SQLite 检查点、FAISS 索引）均被纳入忽略列表，保持仓库纯净。

### 4. 开发者规范
- **环境初始化**：必须复制 `.env.example` 为 `.env` 并填入有效的 API 配置。
- **依赖同步**：新增依赖时需同步更新 `pyproject.toml` 中的 `dependencies` 列表。
- **运行方式**：每个子项目均为独立的入口点，通过 `python <module>/main.py` 直接执行，无需额外的编译或打包步骤。