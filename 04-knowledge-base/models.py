"""
models.py — RAG 相关数据模型
"""

from pydantic import BaseModel, Field


class RAGAnswer(BaseModel):
    """带来源引用的 RAG 回答"""
    answer: str = Field(..., description="回答内容")
    sources: list[str] = Field(default_factory=list, description="引用的来源片段")
    confidence: str = Field(default="medium", description="置信度：high/medium/low")
