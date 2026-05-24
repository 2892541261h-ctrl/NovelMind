"""Writer Context 写作上下文模型。"""

from typing import Any

from pydantic import BaseModel, Field

from .chapter import ChapterSummary
from .novel_project import NovelProjectDetail
from .project_config import (
    AutomationConfig,
    OutlineConfig,
    StyleProfileConfig,
    SummariesList,
)
from .story_bible import StoryBible


class WriterContextWarning(BaseModel):
    """写作上下文警告信息。"""
    type: str = ""       # missing_outline / missing_style_profile / missing_automation 等
    message: str = ""


class WriterContext(BaseModel):
    """完整的写作上下文，组合已有项目信息。"""
    project_id: str
    project: NovelProjectDetail | None = None
    story_bible: StoryBible | None = None
    chapters: list[ChapterSummary] = Field(default_factory=list)
    outline: OutlineConfig | None = None
    style_profile: StyleProfileConfig | None = None
    automation: AutomationConfig | None = None
    summaries: SummariesList = Field(default_factory=lambda: SummariesList(project_id=""))
    warnings: list[WriterContextWarning] = Field(default_factory=list)


class NextChapterPreview(BaseModel):
    """下一章预览（只预览，不创建文件）。"""
    project_id: str
    suggested_chapter_id: str = ""
    suggested_title: str = ""
    suggested_filename: str = ""
    next_order: int = 0
    target_word_count: int = 0
    would_overwrite: bool = False


class PromptMessage(BaseModel):
    """prompt 消息。"""
    role: str = "user"   # system / user / assistant
    content: str = ""


class PromptPreview(BaseModel):
    """prompt 预览（mock，不调用真实 AI）。"""
    project_id: str
    provider: str = "mock"
    model: str = "mock-model"
    uses_real_ai: bool = False
    messages: list[dict[str, Any]] = Field(default_factory=list)
    raw_prompt: str = ""
