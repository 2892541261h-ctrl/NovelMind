"""Daily Writer prompt builder —— assembles writing context for chapter generation."""

from database import SessionLocal
from schemas.chapter_draft import ChapterDraftGenerateRequest
from services.reference_novel_service import get_latest_profile_for_project


async def build_prompt(req: ChapterDraftGenerateRequest) -> tuple[str, str]:
    """Build system and user prompts for chapter generation.

    Returns (system_prompt, user_prompt).
    """
    db = SessionLocal()
    try:
        ref_profile = get_latest_profile_for_project(db, req.project_id)
    finally:
        db.close()

    system_parts = [_SYSTEM_BASE]

    # reference profile guidance
    if ref_profile:
        system_parts.append("")
        system_parts.append("=== REFERENCE CREATIVE DIRECTION ===")
        system_parts.append("The following is abstract creative guidance extracted from reference novels.")
        system_parts.append("Use it ONLY for creative direction. DO NOT copy, continue, or rewrite the reference work.")
        if ref_profile.genre:
            system_parts.append(f"Genre inspiration: {ref_profile.genre}")
        if ref_profile.worldbuilding_pattern:
            system_parts.append(f"Worldbuilding approach: {ref_profile.worldbuilding_pattern}")
        if ref_profile.character_archetypes:
            system_parts.append(f"Character archetype patterns: {ref_profile.character_archetypes}")
        if ref_profile.conflict_patterns:
            system_parts.append(f"Conflict pattern inspiration: {ref_profile.conflict_patterns}")
        if ref_profile.writing_style_profile:
            system_parts.append(f"Writing style direction: {ref_profile.writing_style_profile}")
        if ref_profile.plot_progression_model:
            system_parts.append(f"Plot progression model: {ref_profile.plot_progression_model}")
        if ref_profile.target_novel_direction:
            system_parts.append(f"Target creative direction: {ref_profile.target_novel_direction}")
        system_parts.append("")
        system_parts.append("=== ORIGINALITY CONSTRAINTS ===")
        for c in _ORIGINALITY_CONSTRAINTS:
            system_parts.append(f"- {c}")

    system_prompt = "\n".join(system_parts)

    user_parts = [
        f"Write chapter {req.chapter_number} for project {req.project_id}.",
    ]
    if req.title:
        user_parts.append(f"Chapter title: {req.title}")
    if req.writing_goal:
        user_parts.append(f"Writing goal: {req.writing_goal}")
    if req.extra_instruction:
        user_parts.append(f"Extra instructions: {req.extra_instruction}")
    user_parts.append("")
    user_parts.append("Generate original novel chapter content. Write in Chinese.")
    user_prompt = "\n".join(user_parts)

    return system_prompt, user_prompt


_SYSTEM_BASE = (
    "You are NovelMind Daily Writer, an AI novel chapter generator. "
    "Your task is to write ORIGINAL novel chapters for the user's own novel project. "
    "You are NOT continuing, rewriting, or copying any reference novel. "
    "Generate creative, engaging, original content."
)

_ORIGINALITY_CONSTRAINTS = [
    "DO NOT continue or extend any reference novel.",
    "DO NOT copy original text from any reference work.",
    "DO NOT reuse character names, place names, organization names, or plot events from reference works.",
    "ONLY abstract narrative rhythm, conflict patterns, worldbuilding approaches, character relationship structures, and writing style direction.",
    "ALL generated content MUST serve the user's own original novel.",
]
