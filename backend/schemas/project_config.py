"""项目配置文件最小数据模型。"""

from typing import Any

from pydantic import BaseModel, Field


class OutlineConfig(BaseModel):
    """大纲配置。"""
    project_id: str = ""
    acts: list[dict[str, Any]] = Field(default_factory=list)
    chapters: list[dict[str, Any]] = Field(default_factory=list)


class AutomationSchedule(BaseModel):
    """自动化调度配置。"""
    type: str = "manual"
    timezone: str = "Asia/Macau"


class AutomationSafety(BaseModel):
    """自动化安全配置。"""
    never_overwrite_existing_chapters: bool = True


class AutomationConfig(BaseModel):
    """自动化配置。"""
    project_id: str = ""
    enabled: bool = False
    last_generated_chapter: int = Field(default=0, ge=0)
    schedule: AutomationSchedule = Field(default_factory=AutomationSchedule)
    safety: AutomationSafety = Field(default_factory=AutomationSafety)


class StyleProfileConfig(BaseModel):
    """写作风格配置。"""
    project_id: str = ""
    tone: str = ""
    point_of_view: str = ""
    pace: str = ""
    style_notes: list[str] = Field(default_factory=list)


class SummaryFileEntry(BaseModel):
    """摘要文件条目。"""
    filename: str
    file_type: str = ""   # .md / .txt / .json


class SummariesList(BaseModel):
    """摘要文件列表。"""
    project_id: str
    files: list[SummaryFileEntry] = Field(default_factory=list)
