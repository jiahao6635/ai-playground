"""
models.py — Pydantic 数据模型

定义结构化输出的数据结构。
LangChain 1.x 基于 Pydantic v2，必须使用 from pydantic import BaseModel。
"""

from pydantic import BaseModel, Field


class TranslationResult(BaseModel):
    """翻译结果的结构化输出"""

    source_language: str = Field(
        ...,
        description="检测到的源语言，如 '中文'、'English'、'日本語'"
    )
    target_language: str = Field(
        ...,
        description="翻译目标语言，如 'English'、'中文'、'French'"
    )
    original_text: str = Field(
        ...,
        description="原文内容"
    )
    translated_text: str = Field(
        ...,
        description="翻译后的文本"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="翻译置信度，0.0 到 1.0 之间"
    )
    notes: str = Field(
        default="",
        description="翻译说明，如有歧义或多义词，说明选择理由"
    )


class TranslationRequest(BaseModel):
    """翻译请求的结构"""
    text: str = Field(..., description="要翻译的文本")
    target_language: str = Field(default="English", description="目标语言")
