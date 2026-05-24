"""Daily Writer prompt builder —— assembles writing context for chapter generation."""

from database import SessionLocal
from schemas.chapter_draft import ChapterDraftGenerateRequest
from services.reference_novel_service import get_latest_profile_for_project


async def build_prompt(req: ChapterDraftGenerateRequest) -> tuple[str, str]:
    db = SessionLocal()
    try:
        ref_profile = get_latest_profile_for_project(db, req.project_id)
    finally:
        db.close()

    system_parts = [_SYSTEM_IDENTITY]

    # reference profile guidance
    if ref_profile:
        system_parts.append("")
        system_parts.append("== 参考创作方向（仅抽象规律，非具体内容）==")
        system_parts.append("以下是参考小说抽象出的创作规律，只能作为原创方向参考。")
        if ref_profile.genre:
            system_parts.append(f"- 类型启发：{ref_profile.genre}")
        if ref_profile.worldbuilding_pattern:
            system_parts.append(f"- 世界观构建方式：{ref_profile.worldbuilding_pattern}")
        if ref_profile.character_archetypes:
            system_parts.append(f"- 人物原型模式：{ref_profile.character_archetypes}")
        if ref_profile.conflict_patterns:
            system_parts.append(f"- 冲突模式参考：{ref_profile.conflict_patterns}")
        if ref_profile.writing_style_profile:
            system_parts.append(f"- 写作风格方向：{ref_profile.writing_style_profile}")
        if ref_profile.plot_progression_model:
            system_parts.append(f"- 情节推进模型：{ref_profile.plot_progression_model}")
        if ref_profile.target_novel_direction:
            system_parts.append(f"- 目标创作方向：{ref_profile.target_novel_direction}")
        system_parts.append("")
        system_parts.append("== 原创性约束 ==")
        for c in _ORIGINALITY_RULES:
            system_parts.append(f"- {c}")

    system_parts.append("")
    system_parts.append(_OUTPUT_RULES)
    system_prompt = "\n".join(system_parts)

    user_parts = [f"请为项目 {req.project_id} 撰写第 {req.chapter_number} 章。"]
    if req.title:
        user_parts.append(f"章节标题：{req.title}")
    if req.writing_goal:
        user_parts.append(f"本章写作目标：{req.writing_goal}")
    if req.extra_instruction:
        user_parts.append(f"额外要求：{req.extra_instruction}")
    user_parts.append("")
    user_parts.append("请直接输出章节正文（用中文写作）。")
    user_prompt = "\n".join(user_parts)

    return system_prompt, user_prompt


_SYSTEM_IDENTITY = (
    "你是一位长篇小说章节写作助手。你的任务是撰写用户原创小说的章节。"
    "你不在续写、改写或复制任何参考小说。"
)

_OUTPUT_RULES = (
    "输出要求："
    "1. 生成完整的章节正文，包含开头、发展、转折和结尾钩子。"
    "2. 保持人物行为合理、叙事连贯。"
    "3. 不要输出解释、分析过程或'以下是章节内容'之类的引导语。"
    "4. 直接输出正文。"
    "5. 中文写作自然流畅，段落清晰。"
    "6. 每章建议 1500-3500 字，根据内容需要灵活控制。"
)

_ORIGINALITY_RULES = [
    "DO NOT continue or extend any reference novel.",
    "DO NOT copy original text from any reference work.",
    "DO NOT reuse character names, place names, organization names, or plot events from reference works.",
    "ONLY abstract narrative rhythm, conflict patterns, worldbuilding approaches, character relationship structures, and writing style direction.",
    "ALL generated content MUST serve the user's own original novel.",
]
