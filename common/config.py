"""
config.py — 配置加载模块

从 .env 文件读取环境变量，提供类型安全的配置访问。
所有项目通过 get_llm_config() 和 get_embedding_config() 获取配置。
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# 加载 .env 文件（如果存在）
load_dotenv()


@dataclass
class LLMConfig:
    """LLM 配置"""
    base_url: str
    api_key: str
    model_name: str


@dataclass
class EmbeddingConfig:
    """Embedding 模型配置"""
    base_url: str
    api_key: str
    model_name: str


def get_llm_config() -> LLMConfig:
    """
    获取 LLM 配置。

    从环境变量读取，如果缺少必填项则给出清晰提示。

    Returns:
        LLMConfig 实例
    """
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("LLM_API_KEY", "ollama")
    model_name = os.getenv("LLM_MODEL_NAME", "qwen2.5:7b")

    if not base_url or not model_name:
        raise ValueError(
            "缺少 LLM 配置！请在项目根目录创建 .env 文件，"
            "参考 .env.example 填写 LLM_BASE_URL 和 LLM_MODEL_NAME。"
        )

    return LLMConfig(
        base_url=base_url,
        api_key=api_key,
        model_name=model_name,
    )


def get_embedding_config() -> EmbeddingConfig:
    """
    获取 Embedding 模型配置。

    用于 RAG 项目（P4 起）。如果未配置，默认使用与 LLM 相同的端点。

    Returns:
        EmbeddingConfig 实例
    """
    base_url = os.getenv("EMBEDDING_BASE_URL") or os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("EMBEDDING_API_KEY") or os.getenv("LLM_API_KEY", "ollama")
    model_name = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text")

    return EmbeddingConfig(
        base_url=base_url,
        api_key=api_key,
        model_name=model_name,
    )
