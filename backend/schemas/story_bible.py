"""Story Bible 最小数据模型。"""

from typing import Literal

from pydantic import BaseModel, Field


class StoryMetadata(BaseModel):
    """小说项目元信息。"""
    project_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    genre: str = ""
    language: str = "zh-CN"
    target_chapter_count: int = Field(default=0, ge=0)
    current_chapter_count: int = Field(default=0, ge=0)


class CharacterProfile(BaseModel):
    """角色档案。"""
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    role: str = ""          # 主角 / 配角 / 反派 等
    description: str = ""
    goals: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    relationships: dict[str, str] = Field(default_factory=dict)


class LocationProfile(BaseModel):
    """地点档案。"""
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = ""
    atmosphere: str = ""    # 氛围描述


class WorldRule(BaseModel):
    """世界设定规则。"""
    id: str = Field(min_length=1)
    category: str = ""      # 社会 / 自然 / 科技 等
    rule: str = Field(min_length=1)
    importance: Literal["high", "medium", "low"] = "medium"


class PlotThread(BaseModel):
    """剧情线。"""
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    status: Literal["planned", "in_progress", "completed", "abandoned"] = "planned"
    summary: str = ""


class StyleProfile(BaseModel):
    """写作风格配置。"""
    tone: str = ""          # 基调（冷峻 / 温暖 / 诙谐 等）
    pov: str = ""           # 视角（第一人称 / 第三人称有限 / 全知 等）
    pacing: str = ""        # 节奏（慢热 / 紧凑 / 张弛交替 等）
    taboo: list[str] = Field(default_factory=list)
    notes: str = ""


class StoryBible(BaseModel):
    """Story Bible —— 一个小说项目的完整设定。"""
    metadata: StoryMetadata
    characters: list[CharacterProfile] = Field(default_factory=list)
    locations: list[LocationProfile] = Field(default_factory=list)
    world_rules: list[WorldRule] = Field(default_factory=list)
    plot_threads: list[PlotThread] = Field(default_factory=list)
    style: StyleProfile = Field(default_factory=StyleProfile)
