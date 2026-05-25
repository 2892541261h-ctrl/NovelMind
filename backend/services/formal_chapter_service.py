from datetime import datetime

from sqlalchemy.orm import Session

from models.chapter import Chapter
from models.chapter_draft import ChapterDraft
from schemas.formal_chapter import FormalChapterCreate, FormalChapterUpdate


def list_chapters(db: Session, project_id: int) -> list[Chapter]:
    return (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id)
        .order_by(Chapter.chapter_number)
        .all()
    )


def get_chapter(db: Session, chapter_id: int) -> Chapter | None:
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def get_by_number(db: Session, project_id: int, chapter_number: int) -> Chapter | None:
    return (
        db.query(Chapter)
        .filter(Chapter.project_id == project_id, Chapter.chapter_number == chapter_number)
        .first()
    )


def create_chapter(db: Session, data: FormalChapterCreate) -> Chapter:
    ch = Chapter(**data.model_dump(), word_count=_count_words(data.content))
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


def update_chapter(db: Session, chapter_id: int, data: FormalChapterUpdate) -> Chapter | None:
    ch = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not ch:
        return None
    for key, val in data.model_dump(exclude_unset=True).items():
        if key == "content" and val is not None:
            ch.word_count = _count_words(val)
        setattr(ch, key, val)
    db.commit()
    db.refresh(ch)
    return ch


def delete_chapter(db: Session, chapter_id: int) -> bool:
    ch = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not ch:
        return False
    db.delete(ch)
    db.commit()
    return True


def publish_draft(db: Session, draft_id: int, overwrite_existing: bool = False) -> Chapter:
    draft = db.query(ChapterDraft).filter(ChapterDraft.id == draft_id).first()
    if not draft:
        raise ValueError("Draft not found")
    content = draft.content or ""
    title = draft.title or ""
    if not content.strip():
        raise ValueError("Cannot publish empty draft")

    existing = get_by_number(db, draft.project_id, draft.chapter_number)
    if existing and not overwrite_existing:
        raise ValueError(
            f"Chapter {draft.chapter_number} already exists for project {draft.project_id}. "
            "Set overwrite_existing=true to replace."
        )

    if existing and overwrite_existing:
        existing.title = title
        existing.content = content
        existing.word_count = _count_words(content)
        existing.source_draft_id = draft.id
        existing.published_at = datetime.utcnow()
        existing.status = "published"
        db.commit()
        db.refresh(existing)
        return existing

    ch = Chapter(
        project_id=draft.project_id,
        chapter_number=draft.chapter_number,
        title=title,
        content=content,
        word_count=_count_words(content),
        status="published",
        source_draft_id=draft.id,
        published_at=datetime.utcnow(),
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ch


def _count_words(content: str | None) -> int:
    if not content:
        return 0
    return len(content.replace(" ", "").replace("\n", "").replace("\r", ""))
