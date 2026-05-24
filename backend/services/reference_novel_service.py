import json

from sqlalchemy.orm import Session

from ai.gateway import generate_text
from ai.types import AIMessage, AIRequest
from models.reference_novel import ReferenceNovel
from models.reference_profile import ReferenceProfile
from schemas.reference_novel import ReferenceNovelCreate, ReferenceNovelUpdate
from schemas.reference_profile import ReferenceProfileCreate


def list_novels(db: Session, project_id: int) -> list[ReferenceNovel]:
    return db.query(ReferenceNovel).filter(ReferenceNovel.project_id == project_id).all()


def get_novel(db: Session, novel_id: int) -> ReferenceNovel | None:
    return db.query(ReferenceNovel).filter(ReferenceNovel.id == novel_id).first()


def create_novel(db: Session, data: ReferenceNovelCreate) -> ReferenceNovel:
    novel = ReferenceNovel(**data.model_dump())
    db.add(novel)
    db.commit()
    db.refresh(novel)
    return novel


def update_novel(db: Session, novel_id: int, data: ReferenceNovelUpdate) -> ReferenceNovel | None:
    novel = db.query(ReferenceNovel).filter(ReferenceNovel.id == novel_id).first()
    if not novel:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(novel, key, val)
    db.commit()
    db.refresh(novel)
    return novel


def delete_novel(db: Session, novel_id: int) -> bool:
    novel = db.query(ReferenceNovel).filter(ReferenceNovel.id == novel_id).first()
    if not novel:
        return False
    db.query(ReferenceProfile).filter(ReferenceProfile.novel_id == novel_id).delete()
    db.delete(novel)
    db.commit()
    return True


def list_profiles(db: Session, project_id: int) -> list[ReferenceProfile]:
    return db.query(ReferenceProfile).filter(ReferenceProfile.project_id == project_id).all()


def get_profile(db: Session, profile_id: int) -> ReferenceProfile | None:
    return db.query(ReferenceProfile).filter(ReferenceProfile.id == profile_id).first()


def get_profile_by_novel(db: Session, novel_id: int) -> ReferenceProfile | None:
    return db.query(ReferenceProfile).filter(ReferenceProfile.novel_id == novel_id).first()


def delete_profile(db: Session, profile_id: int) -> bool:
    profile = db.query(ReferenceProfile).filter(ReferenceProfile.id == profile_id).first()
    if not profile:
        return False
    db.delete(profile)
    db.commit()
    return True


async def generate_profile(db: Session, data: ReferenceProfileCreate) -> ReferenceProfile:
    novel = db.query(ReferenceNovel).filter(ReferenceNovel.id == data.novel_id).first()
    if not novel:
        raise ValueError("Reference novel not found")

    existing = db.query(ReferenceProfile).filter(ReferenceProfile.novel_id == data.novel_id).first()

    request = AIRequest(
        task="reference_novel_analysis",
        messages=[
            AIMessage(role="system", content=_system_prompt()),
            AIMessage(role="user", content=_user_prompt(novel.content[:3000])),
        ],
    )
    response = await generate_text(request)

    profile_data = {
        "novel_id": data.novel_id,
        "project_id": data.project_id,
        "genre": novel.title or "unknown",
        "worldbuilding_pattern": _extract_section(response.content, "worldbuilding"),
        "character_archetypes": _extract_section(response.content, "characters"),
        "conflict_patterns": _extract_section(response.content, "conflict"),
        "writing_style_profile": _extract_section(response.content, "style"),
        "plot_progression_model": _extract_section(response.content, "plot"),
        "target_novel_direction": _extract_section(response.content, "direction"),
        "confidence": "low",
        "status": "draft",
    }

    if existing:
        for key, val in profile_data.items():
            setattr(existing, key, val)
        db.commit()
        db.refresh(existing)
        return existing

    profile = ReferenceProfile(**profile_data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _system_prompt() -> str:
    return (
        "You analyze reference novels to extract creative patterns. "
        "Do NOT copy original text, character names, or plot events. "
        "Abstract only: genre, worldbuilding, character types, conflict types, "
        "writing style, plot progression, and creative direction."
    )


def _user_prompt(content: str) -> str:
    return (
        "Analyze this reference novel text and extract:\n"
        "1. [worldbuilding] Setting and world rules pattern\n"
        "2. [characters] Character archetypes and relationship patterns\n"
        "3. [conflict] Conflict types and resolution patterns\n"
        "4. [style] Writing style and narrative techniques\n"
        "5. [plot] Plot progression model\n"
        "6. [direction] Suggested original creative direction\n\n"
        "Respond with clear section headers. Abstract only, do not copy names.\n\n"
        f"Text:\n{content}"
    )


def _extract_section(text: str, tag: str) -> str:
    try:
        start = text.lower().index(f"[{tag}]")
        rest = text[start + len(tag) + 2:]
        for end_tag in ["[worldbuilding]", "[characters]", "[conflict]", "[style]", "[plot]", "[direction]"]:
            end_pos = rest.lower().find(f"[{end_tag}]")
            if end_pos > 0:
                return rest[:end_pos].strip()
        return rest.strip()
    except ValueError:
        return text[:200] if text else ""
