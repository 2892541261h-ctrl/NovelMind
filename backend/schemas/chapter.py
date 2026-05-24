"""Chapter 最小数据模型。"""

from pydantic import BaseModel, Field


class ChapterSummary(BaseModel):
    """章节摘要信息。"""
    project_id: str = Field(min_length=1)
    chapter_id: str = Field(min_length=1)
    title: str = ""
    filename: str = ""
    order: int = Field(default=0, ge=0)
    word_count: int = Field(default=0, ge=0)
    exists: bool = True


class ChapterContent(ChapterSummary):
    """章节完整内容。"""
    content: str = ""
