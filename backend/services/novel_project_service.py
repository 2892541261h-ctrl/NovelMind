"""Novel Project 读取服务 —— 扫描 novels/ 目录识别小说项目。"""

import json
import re
from pathlib import Path

from schemas.novel_project import (
    NovelProjectDetail,
    NovelProjectSummary,
    ProjectFiles,
    ProjectPaths,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
NOVELS_ROOT = REPO_ROOT / "novels"
PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def list_novel_projects() -> list[NovelProjectSummary]:
    """列出 novels/ 下所有小说项目摘要。"""
    if not NOVELS_ROOT.is_dir():
        return []

    projects: list[NovelProjectSummary] = []

    for entry in sorted(NOVELS_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        project_id = entry.name
        if not PROJECT_ID_PATTERN.fullmatch(project_id):
            continue
        projects.append(_load_summary(project_id, entry))

    return projects


def get_novel_project(project_id: str) -> NovelProjectDetail:
    """获取指定小说项目的详细信息。

    Raises:
        ValueError: project_id 非法或指向 novels/ 外部。
        FileNotFoundError: 项目目录不存在。
    """
    _validate_project_id(project_id)

    project_dir = _resolve_project_dir(project_id)
    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"小说项目目录不存在：{project_dir}。"
            f" 请确认项目 ID {project_id} 正确。"
        )

    return _load_detail(project_id, project_dir)


def _validate_project_id(project_id: str) -> None:
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project_id 只能包含字母、数字、短横线和下划线。")

    project_dir = (NOVELS_ROOT / project_id).resolve()
    novels_root = NOVELS_ROOT.resolve()
    if project_dir != novels_root and novels_root not in project_dir.parents:
        raise ValueError("project_id 不能指向 novels 目录之外。")


def _resolve_project_dir(project_id: str) -> Path:
    return NOVELS_ROOT / project_id


def _load_summary(project_id: str, project_dir: Path) -> NovelProjectSummary:
    bible_path = project_dir / "story-bible.json"
    if bible_path.is_file():
        return _summary_from_bible(project_id, bible_path)

    return NovelProjectSummary(
        project_id=project_id,
        title=project_id,
        has_story_bible=False,
    )


def _load_detail(project_id: str, project_dir: Path) -> NovelProjectDetail:
    bible_path = project_dir / "story-bible.json"

    # 基础信息从 story-bible 读取（如存在）
    if bible_path.is_file():
        detail = _detail_from_bible(project_id, bible_path)
    else:
        detail = NovelProjectDetail(
            project_id=project_id,
            title=project_id,
            has_story_bible=False,
        )

    # 填充路径信息
    detail.paths = ProjectPaths(
        project_dir=str(project_dir.resolve()),
        story_bible=str(bible_path.resolve()) if bible_path.is_file() else "",
        chapters_dir=str((project_dir / "chapters").resolve()),
        summaries_dir=str((project_dir / "summaries").resolve()),
        reports_dir=str((project_dir / "reports").resolve()),
    )

    # 填充可用文件标记
    detail.available_files = ProjectFiles(
        story_bible=bible_path.is_file(),
        outline=(project_dir / "outline.json").is_file(),
        automation=(project_dir / "automation.json").is_file(),
        style_profile=(project_dir / "style-profile.json").is_file(),
    )

    return detail


def _read_bible_metadata(bible_path: Path) -> dict:
    """读取 story-bible.json 中的 metadata 字段，失败返回空 dict。"""
    try:
        raw = json.loads(bible_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {}
        metadata = raw.get("metadata", {})
        if not isinstance(metadata, dict):
            return {}
        return metadata
    except (json.JSONDecodeError, OSError):
        return {}


def _summary_from_bible(project_id: str, bible_path: Path) -> NovelProjectSummary:
    meta = _read_bible_metadata(bible_path)
    return _build_summary(
        project_id=project_id,
        title=meta.get("title"),
        genre=meta.get("genre"),
        language=meta.get("language"),
        current_chapter_count=meta.get("current_chapter_count"),
        target_chapter_count=meta.get("target_chapter_count"),
        has_story_bible=True,
    )


def _detail_from_bible(project_id: str, bible_path: Path) -> NovelProjectDetail:
    meta = _read_bible_metadata(bible_path)
    return NovelProjectDetail(
        **_build_summary(
            project_id=project_id,
            title=meta.get("title"),
            genre=meta.get("genre"),
            language=meta.get("language"),
            current_chapter_count=meta.get("current_chapter_count"),
            target_chapter_count=meta.get("target_chapter_count"),
            has_story_bible=True,
        ).model_dump()
    )


def _build_summary(
    project_id: str,
    title: object,
    genre: object,
    language: object,
    current_chapter_count: object,
    target_chapter_count: object,
    has_story_bible: bool,
) -> NovelProjectSummary:
    try:
        return NovelProjectSummary(
            project_id=project_id,
            title=title if isinstance(title, str) and title else project_id,
            genre=genre if isinstance(genre, str) else "",
            language=language if isinstance(language, str) and language else "zh-CN",
            current_chapter_count=current_chapter_count
            if isinstance(current_chapter_count, int) and current_chapter_count >= 0
            else 0,
            target_chapter_count=target_chapter_count
            if isinstance(target_chapter_count, int) and target_chapter_count >= 0
            else 0,
            has_story_bible=has_story_bible,
        )
    except ValueError:
        return NovelProjectSummary(
            project_id=project_id,
            title=project_id,
            has_story_bible=has_story_bible,
        )
