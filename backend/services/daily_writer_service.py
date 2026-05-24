"""Daily Writer prompt builder - v1.2: reads Story Bible + Character Cards + World Entries + Chapter Plans."""

from database import SessionLocal
from schemas.chapter_draft import ChapterDraftGenerateRequest
from services.reference_novel_service import get_latest_profile_for_project
from services.sb_service import list_bibles as list_bibles_svc
from services.cc_service import list_cards
from services.we_service import list_entries
from services.cp_service import get_plan_by_number
from services.cs_service import get_recent_summaries
from services.pt_service import get_open_threads


async def build_prompt(req: ChapterDraftGenerateRequest) -> tuple[str, str]:
    db = SessionLocal()
    try:
        ref_profile = get_latest_profile_for_project(db, req.project_id)
        bibles = list_bibles_svc(db, req.project_id)
        cards = list_cards(db, req.project_id)
        entries = list_entries(db, req.project_id)
        plan = get_plan_by_number(db, req.project_id, req.chapter_number)
        recent_summaries = get_recent_summaries(db, req.project_id, limit=3)
        open_threads = get_open_threads(db, req.project_id)
    finally:
        db.close()

    system_parts = [_SYSTEM_IDENTITY]

    # story bible
    for sb in bibles[:1]:
        system_parts.append("")
        system_parts.append(f"== Story Bible: {sb.title} ==")
        if sb.genre: system_parts.append(f"Genre: {sb.genre}")
        if sb.tone: system_parts.append(f"Tone: {sb.tone}")
        if sb.theme: system_parts.append(f"Theme: {sb.theme[:300]}")
        if sb.world_rules: system_parts.append(f"World rules: {sb.world_rules[:300]}")
        if sb.narrative_style: system_parts.append(f"Narrative style: {sb.narrative_style[:300]}")

    # character cards
    if cards:
        system_parts.append("")
        system_parts.append("== Character Cards ==")
        for c in cards[:8]:
            parts = [f"- {c.name}" + (f" ({c.role})" if c.role else "")]
            if c.personality: parts.append(f"personality: {c.personality[:100]}")
            if c.motivation: parts.append(f"motivation: {c.motivation[:100]}")
            system_parts.append(" | ".join(parts))

    # world entries
    if entries:
        system_parts.append("")
        system_parts.append("== World Entries ==")
        for e in entries[:6]:
            system_parts.append(f"- [{e.entry_type}] {e.name}: {e.description[:120]}")

    # chapter plan
    if plan:
        system_parts.append("")
        system_parts.append(f"== Chapter Plan #{plan.chapter_number} ==")
        if plan.title: system_parts.append(f"Title: {plan.title}")
        if plan.goal: system_parts.append(f"Goal: {plan.goal[:200]}")
        if plan.key_events: system_parts.append(f"Key events: {plan.key_events[:200]}")
        if plan.pov_character: system_parts.append(f"POV: {plan.pov_character}")

    # recent chapter summaries
    if recent_summaries:
        system_parts.append("")
        system_parts.append("== Recent Chapter Summaries ==")
        for s in recent_summaries:
            summary_line = f"- Ch#{s.chapter_number}: {s.key_events[:150]}" if s.key_events else f"- Ch#{s.chapter_number}: {s.summary[:150]}"
            if s.unresolved_threads:
                summary_line += f" [unresolved: {s.unresolved_threads[:100]}]"
            system_parts.append(summary_line)

    # open plot threads
    if open_threads:
        system_parts.append("")
        system_parts.append("== Open Plot Threads (need resolution) ==")
        for t in open_threads[:6]:
            system_parts.append(f"- [{t.status}] {t.title}: {t.description[:120]}")

    # continuity rules
    system_parts.append("")
    system_parts.append(_CONTINUITY_RULES)

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
    "7. 本章结尾可以留下合理钩子，但不要重复上一章内容。"
    "8. 不要跳过关键情节推进。"
)

_CONTINUITY_RULES = (
    "长篇连续性规则："
    "1. 参考最近章节摘要，保持前后文连续。"
    "2. 延续未解决伏笔，不要随意忘记。"
    "3. 不要突然改变人物性格。"
    "4. 不要无解释改变世界观规则。"
    "5. 当前章节应服务于章节计划。"
    "6. 不要重复上一章内容。"
    "7. 不要跳过关键情节推进。"
)

_ORIGINALITY_RULES = [
    "DO NOT continue or extend any reference novel.",
    "DO NOT copy original text from any reference work.",
    "DO NOT reuse character names, place names, organization names, or plot events from reference works.",
    "ONLY abstract narrative rhythm, conflict patterns, worldbuilding approaches, character relationship structures, and writing style direction.",
    "ALL generated content MUST serve the user's own original novel.",
]
