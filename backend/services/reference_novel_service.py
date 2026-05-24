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


def get_latest_profile_for_project(db: Session, project_id: int) -> ReferenceProfile | None:
    return (
        db.query(ReferenceProfile)
        .filter(ReferenceProfile.project_id == project_id)
        .order_by(ReferenceProfile.created_at.desc())
        .first()
    )


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

    if response.error:
        raise ValueError(f"AI profile generation failed: {response.error}")

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
        "你是参考小说创作规律分析师。你的唯一任务是从参考小说中提取抽象创作规律。"
        "你不是续写作家，不是同人作者，不是翻译。你是规律分析师。"
        "只能提取抽象规律：流派类型、世界观构建方式、人物原型类型、冲突模式类型、写作风格特征、情节推进模式、创作方向建议。"
        "严禁复制原文、搬运角色名/地名/组织名、搬运完整剧情桥段、简单换皮。"
    )


def _user_prompt(content: str) -> str:
    return (
        "请分析以下参考小说文本，提取抽象创作规律。用 [tag] 标题形式回复：\n"
        "1. [worldbuilding] 世界观构建方式和设定规则（抽象描述，不含原书具体地名/设定）\n"
        "2. [characters] 人物原型和关系模式（抽象人物类型，不含原书角色名）\n"
        "3. [conflict] 冲突类型和解决模式（抽象冲突规律，不含具体剧情）\n"
        "4. [style] 写作风格和叙事技法（抽象风格特征，不含原文引用）\n"
        "5. [plot] 情节推进模型（抽象推进模式，不含具体事件链条）\n"
        "6. [direction] 原创创作方向建议（基于规律的建议，不含续写/改写提示）\n\n"
        "严禁复制原文、搬运角色名、搬运完整剧情桥段或简单换皮。\n\n"
        f"参考文本：\n{content}"
    )


def _extract_section(text: str, tag: str) -> str:
    if not text:
        return ""
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
