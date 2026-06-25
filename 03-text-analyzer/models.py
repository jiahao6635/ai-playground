"""
models.py — 文本分析的数据模型

定义结构化分析报告的输出格式。
"""

from pydantic import BaseModel, Field


class SentimentResult(BaseModel):
    """情感分析结果"""
    sentiment: str = Field(..., description="情感倾向：positive / negative / neutral")
    score: float = Field(..., ge=-1.0, le=1.0, description="情感分值，-1 最消极到 1 最积极")
    explanation: str = Field(..., description="分析理由")


class KeywordResult(BaseModel):
    """关键词提取结果"""
    keywords: list[str] = Field(..., description="关键词列表")
    summary: str = Field(..., description="一句话概括文本内容")


class AnalysisReport(BaseModel):
    """完整的文本分析报告"""
    sentiment: str = Field(..., description="情感倾向")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="情感分值")
    keywords: list[str] = Field(..., description="关键词列表")
    summary: str = Field(..., description="摘要")
    category: str = Field(..., description="文本分类")
