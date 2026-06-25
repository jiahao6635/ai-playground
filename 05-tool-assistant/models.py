"""
models.py — 工具助手数据模型
"""

from pydantic import BaseModel, Field


class WeatherInfo(BaseModel):
    """天气信息"""
    city: str = Field(..., description="城市名")
    temperature: float = Field(..., description="温度（摄氏度）")
    condition: str = Field(..., description="天气状况")
    suggestion: str = Field(default="", description="出行建议")
