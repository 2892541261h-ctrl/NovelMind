"""Writer Context Builder —— 组合已有项目信息构建写作上下文（只读）。"""

import re
from pathlib import Path

from schemas.chapter import ChapterSummary
from schemas.novel_project import NovelProjectDetail
from schemas.project_config import (
    AutomationConfig,
    OutlineConfig,
    StyleProfileConfig,
    SummariesList,
)
from schemas.story_bible import StoryBible
from schemas.writer_context import (
    NextChapterPreview,
    PromptPreview,
    WriterContext,
    WriterContextWarning,
)

from .chapter_service import list_chapters
from .novel_project_service import get_novel_project
from .project_config_service import (
    load_automation,
    load_outline,
    load_style_profile,
    list_summaries,
)
from .story_bible_service import load_story_bible

PROJECT_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
CHAPTER_EXTENSIONS = {".md", ".txt"}
FILENAME_DIGITS_PATTERN = re.compile(r"(\d+)")


def build_writer_context(project_id: str) -> WriterContext:
    """构建完整的写作上下文。

    组合项目详情、Story Bible、章节列表、大纲、风格、自动化配置和摘要。
    缺失的配置文件记录到 warnings，不影响整体返回。
    """
    _validate_project_id(project_id)

    warnings: list[WriterContextWarning] = []

    # 项目详情
    project = _safe_fetch(
        lambda: get_novel_project(project_id),
        warnings, "missing_project", f"无法读取项目 {project_id} 详情",
    )

    # Story Bible
    story_bible = _safe_fetch(
        lambda: load_story_bible(project_id),
        warnings, "missing_story_bible", f"Story Bible 不存在于项目 {project_id}",
    )

    # 章节列表
    chapters = list_chapters(project_id)

    # 大纲
    outline = _safe_fetch(
        lambda: load_outline(project_id),
        warnings, "missing_outline", f"outline.json 不存在于项目 {project_id}",
    )

    # 风格配置
    style_profile = _safe_fetch(
        lambda: load_style_profile(project_id),
        warnings, "missing_style_profile", f"style-profile.json 不存在于项目 {project_id}",
    )

    # 自动化配置
    automation = _safe_fetch(
        lambda: load_automation(project_id),
        warnings, "missing_automation", f"automation.json 不存在于项目 {project_id}",
    )

    # 摘要列表
    summaries = _safe_fetch_summaries(project_id, warnings)

    return WriterContext(
        project_id=project_id,
        project=project,
        story_bible=story_bible,
        chapters=chapters,
        outline=outline,
        style_profile=style_profile,
        automation=automation,
        summaries=summaries,
        warnings=warnings,
    )


def preview_next_chapter(project_id: str) -> NextChapterPreview:
    """预览下一章信息（只预览，不创建文件）。

    根据已有章节推断下一个 chapter_id 和 order。
    """
    _validate_project_id(project_id)

    chapters = list_chapters(project_id)
    next_order = len(chapters) + 1

    # 推断下一个 chapter_id
    if not chapters:
        suggested_chapter_id = "chapter-001"
        suggested_filename = "chapter-001.md"
    else:
        last_chapter = chapters[-1]
        last_num = _extract_numeric_part(last_chapter.chapter_id)
        if last_num > 0:
            next_num = last_num + 1
            width = len(str(last_num))
            suggested_chapter_id = f"ch{next_num:0{width}d}"
        else:
            suggested_chapter_id = f"chapter-{next_order:03d}"
        suggested_filename = f"{suggested_chapter_id}.md"

    # 检查是否会覆盖已有章节
    project_dir = Path(__file__).resolve().parent.parent.parent / "novels" / project_id
    chapters_dir = project_dir / "chapters"
    would_overwrite = False
    if chapters_dir.is_dir():
        for ext in CHAPTER_EXTENSIONS:
            if (chapters_dir / f"{suggested_chapter_id}{ext}").is_file():
                would_overwrite = True
                break

    # 从自动化配置获取目标字数
    target_word_count = 0
    try:
        automation = load_automation(project_id)
        if automation.enabled:
            target_word_count = 2500  # 默认每章 2500 字（可后续扩展）
    except (ValueError, FileNotFoundError):
        pass

    return NextChapterPreview(
        project_id=project_id,
        suggested_chapter_id=suggested_chapter_id,
        suggested_title="",
        suggested_filename=suggested_filename,
        next_order=next_order,
        target_word_count=target_word_count,
        would_overwrite=would_overwrite,
    )


def preview_prompt(project_id: str) -> PromptPreview:
    """返回 mock prompt 预览，不调用真实 AI。"""
    _validate_project_id(project_id)

    ctx = build_writer_context(project_id)
    preview = preview_next_chapter(project_id)

    # 构建 mock system prompt
    system_parts = ["你是一个专业的长篇小说写作助手。"]
    if ctx.style_profile:
        sp = ctx.style_profile
        if sp.tone:
            system_parts.append(f"写作基调：{sp.tone}。")
        if sp.point_of_view:
            system_parts.append(f"叙事视角：{sp.point_of_view}。")
        if sp.pace:
            system_parts.append(f"节奏：{sp.pace}。")
    if ctx.story_bible:
        sb = ctx.story_bible
        system_parts.append(f"项目：{sb.metadata.title}（{sb.metadata.genre}）。")
        if sb.world_rules:
            rules = "；".join(r.rule for r in sb.world_rules[:3])
            system_parts.append(f"世界观规则：{rules}。")

    system_content = " ".join(system_parts)

    # 构建 mock user prompt
    user_parts = [f"请为小说项目 {project_id} 生成第 {preview.next_order} 章。"]
    user_parts.append(f"建议章节 ID：{preview.suggested_chapter_id}。")
    if ctx.outline:
        outline = ctx.outline
        if outline.chapters:
            # 尝试找到对应的章节大纲条目
            idx = preview.next_order - 1
            if idx < len(outline.chapters):
                ch = outline.chapters[idx]
                user_parts.append(f"章节大纲：{ch.get('title', '')} - {ch.get('summary', '')}。")

    if preview.would_overwrite:
        user_parts.append("⚠️ 警告：目标章节文件已存在，生成将覆盖原有内容。")

    user_content = " ".join(user_parts)

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]
    raw_prompt = f"[MOCK] system: {system_content}\n\n[MOCK] user: {user_content}"

    return PromptPreview(
        project_id=project_id,
        provider="mock",
        model="mock-model",
        uses_real_ai=False,
        messages=messages,
        raw_prompt=raw_prompt,
    )


def _validate_project_id(project_id: str) -> None:
    if not PROJECT_ID_PATTERN.fullmatch(project_id):
        raise ValueError("project_id 只能包含字母、数字、短横线和下划线。")


def _extract_numeric_part(s: str) -> int:
    """从字符串中提取连续数字部分。"""
    match = FILENAME_DIGITS_PATTERN.search(s)
    if match:
        return int(match.group(1))
    return 0


def _safe_fetch(fn, warnings: list, warn_type: str, warn_msg: str):
    """安全获取数据，失败时记录 warning 并返回 None。"""
    try:
        return fn()
    except Exception:
        warnings.append(WriterContextWarning(type=warn_type, message=warn_msg))
        return None


def _safe_fetch_summaries(project_id: str, warnings: list) -> SummariesList:
    try:
        return list_summaries(project_id)
    except FileNotFoundError:
        warnings.append(WriterContextWarning(
            type="missing_project",
            message=f"无法读取项目 {project_id} 摘要（项目目录不存在）",
        ))
        return SummariesList(project_id=project_id, files=[])
    except Exception:
        warnings.append(WriterContextWarning(
            type="missing_summaries",
            message=f"summaries 目录不存在或不可读于项目 {project_id}",
        ))
        return SummariesList(project_id=project_id, files=[])
