"""
llm.py — LLM 初始化工厂（核心公共模块）

所有项目通过 from common.llm import get_llm 复用 LLM 实例。
支持任意 OpenAI 兼容 API（Ollama、vLLM、DeepSeek、通义千问等）。
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from common.config import get_llm_config, get_embedding_config


def get_llm(temperature: float = 0.7, **kwargs) -> ChatOpenAI:
    """
    获取配置好的 ChatOpenAI 实例。

    从 .env 读取 base_url、api_key、model_name，
    显式传入参数确保最高优先级。

    Args:
        temperature: 生成温度，0.0 严谨 / 0.7 平衡 / 1.0 创意
        **kwargs: 额外传递给 ChatOpenAI 的参数

    Returns:
        ChatOpenAI 实例，已配置自定义 base_url 和模型

    用法:
        from common.llm import get_llm
        llm = get_llm()
        response = llm.invoke("你好")
    """
    config = get_llm_config()
    return ChatOpenAI(
        model=config.model_name,
        base_url=config.base_url,
        api_key=config.api_key,
        temperature=temperature,
        streaming=True,
        **kwargs,
    )


def get_embeddings() -> OpenAIEmbeddings:
    """
    获取配置好的 Embedding 模型实例。

    用于 RAG 项目（P4 起），从 .env 读取 embedding 配置。
    如果未单独配置 embedding，默认使用 LLM 的端点。

    Returns:
        OpenAIEmbeddings 实例
    """
    config = get_embedding_config()
    return OpenAIEmbeddings(
        model=config.model_name,
        base_url=config.base_url,
        api_key=config.api_key,
    )
