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
    ReferenceProfileSummary,
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
CHAPTER_STYLE_PATTERN = re.compile(r"^(?P<prefix>.*?)(?P<number>\d+)$")


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

    reference_profile = _safe_fetch_reference_profile(project_id, warnings)

    return WriterContext(
        project_id=project_id,
        project=project,
        story_bible=story_bible,
        chapters=chapters,
        outline=outline,
        style_profile=style_profile,
        automation=automation,
        summaries=summaries,
        reference_profile=reference_profile,
        warnings=warnings,
    )


def preview_next_chapter(project_id: str) -> NextChapterPreview:
    """预览下一章信息（只预览，不创建文件）。

    根据已有章节推断下一个 chapter_id 和 order。
    这里仅做预览，不创建文件，也不会覆盖已有章节。
    """
    _validate_project_id(project_id)

    chapters = list_chapters(project_id)
    reference_chapter = _pick_reference_chapter(chapters)
    next_order = _determine_next_order(chapters)

    # 尽量沿用现有命名风格；无法识别时回退到安全默认格式。
    suggested_chapter_id = _build_suggested_chapter_id(reference_chapter, next_order)
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
    """返回 mock prompt 预览。

    这里只用于本地拼装 prompt 供检查和调试，不执行 AI 生成。
    任何真正的 AI 生成都必须通过 `backend/ai/gateway.py`。
    """
    _validate_project_id(project_id)

    ctx = build_writer_context(project_id)
    preview = preview_next_chapter(project_id)

    # 这里只是本地预览，不会进入真实 AI 调用链。
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


def _determine_next_order(chapters: list[ChapterSummary]) -> int:
    """基于现有章节最大 order 或可识别编号推断下一章序号。"""
    highest_order = 0
    for chapter in chapters:
        highest_order = max(highest_order, chapter.order)
        highest_order = max(highest_order, _extract_numeric_part(chapter.chapter_id))
    if highest_order <= 0:
        return 1
    return highest_order + 1


def _pick_reference_chapter(chapters: list[ChapterSummary]) -> ChapterSummary | None:
    """选出最适合作为命名风格参考的章节。"""
    reference_chapter: ChapterSummary | None = None
    highest_score = 0
    for chapter in chapters:
        score = max(chapter.order, _extract_numeric_part(chapter.chapter_id))
        if score >= highest_score:
            highest_score = score
            reference_chapter = chapter
    return reference_chapter


def _build_suggested_chapter_id(
    reference_chapter: ChapterSummary | None,
    next_order: int,
) -> str:
    """尽量沿用现有命名风格；识别失败时回退安全默认格式。"""
    if reference_chapter is not None:
        match = CHAPTER_STYLE_PATTERN.fullmatch(reference_chapter.chapter_id)
        if match:
            prefix = match.group("prefix")
            width = len(match.group("number"))
            return f"{prefix}{next_order:0{width}d}"
    return f"chapter-{next_order:03d}"


def _safe_fetch(fn, warnings: list, warn_type: str, warn_msg: str):
    """安全获取数据，失败时记录 warning 并返回 None。"""
    try:
        return fn()
    except Exception:
        warnings.append(WriterContextWarning(type=warn_type, message=warn_msg))
        return None


def _safe_fetch_reference_profile(
    project_id: str, warnings: list
) -> ReferenceProfileSummary | None:
    try:
        pid = int(project_id)
    except ValueError:
        return None

    try:
        from database import SessionLocal
        from services.reference_novel_service import get_latest_profile_for_project

        db = SessionLocal()
        try:
            profile = get_latest_profile_for_project(db, pid)
            if profile is None:
                return None
            return ReferenceProfileSummary(
                id=profile.id,
                novel_id=profile.novel_id,
                project_id=profile.project_id,
                genre=profile.genre,
                worldbuilding_pattern=profile.worldbuilding_pattern,
                character_archetypes=profile.character_archetypes,
                conflict_patterns=profile.conflict_patterns,
                writing_style_profile=profile.writing_style_profile,
                plot_progression_model=profile.plot_progression_model,
                target_novel_direction=profile.target_novel_direction,
            )
        finally:
            db.close()
    except Exception:
        warnings.append(WriterContextWarning(
            type="reference_profile_unavailable",
            message=f"无法读取项目 {project_id} 的参考创作画像",
        ))
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
