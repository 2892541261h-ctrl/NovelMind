"""Novel Project 最小数据模型。"""

from pydantic import BaseModel, Field


class NovelProjectSummary(BaseModel):
    """小说项目摘要信息。"""
    project_id: str = Field(min_length=1)
    title: str = ""
    genre: str = ""
    language: str = "zh-CN"
    current_chapter_count: int = Field(default=0, ge=0)
    target_chapter_count: int = Field(default=0, ge=0)
    has_story_bible: bool = False


class ProjectPaths(BaseModel):
    """项目目录路径集合。"""
    project_dir: str = ""
    story_bible: str = ""
    chapters_dir: str = ""
    summaries_dir: str = ""
    reports_dir: str = ""


class ProjectFiles(BaseModel):
    """项目内已知文件是否存在。"""
    story_bible: bool = False
    outline: bool = False
    automation: bool = False
    style_profile: bool = False


class NovelProjectDetail(NovelProjectSummary):
    """小说项目详细信息。"""
    paths: ProjectPaths = Field(default_factory=ProjectPaths)
    available_files: ProjectFiles = Field(default_factory=ProjectFiles)
