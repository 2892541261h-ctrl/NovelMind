import json

from sqlalchemy.orm import Session

from ai.gateway import generate_text
from ai.types import AIMessage, AIRequest
from models.chapter_draft import ChapterDraft
from schemas.chapter_draft import (
    ChapterDraftCreate,
    ChapterDraftGenerateRequest,
    ChapterDraftListItem,
    ChapterDraftRead,
)


def list_drafts(db: Session, project_id: int) -> list[ChapterDraft]:
    return (
        db.query(ChapterDraft)
        .filter(ChapterDraft.project_id == project_id)
        .order_by(ChapterDraft.chapter_number)
        .all()
    )


def get_draft(db: Session, draft_id: int) -> ChapterDraft | None:
    return db.query(ChapterDraft).filter(ChapterDraft.id == draft_id).first()


def create_draft(db: Session, data: ChapterDraftCreate) -> ChapterDraft:
    draft = ChapterDraft(**data.model_dump())
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def update_draft(
    db: Session, draft_id: int, title: str | None = None, content: str | None = None
) -> ChapterDraft | None:
    draft = db.query(ChapterDraft).filter(ChapterDraft.id == draft_id).first()
    if not draft:
        return None
    if title is not None:
        draft.title = title
    if content is not None:
        draft.content = content
    db.commit()
    db.refresh(draft)
    return draft


def delete_draft(db: Session, draft_id: int) -> bool:
    draft = db.query(ChapterDraft).filter(ChapterDraft.id == draft_id).first()
    if not draft:
        return False
    db.delete(draft)
    db.commit()
    return True


def check_exists(db: Session, project_id: int, chapter_number: int) -> bool:
    return (
        db.query(ChapterDraft)
        .filter(
            ChapterDraft.project_id == project_id,
            ChapterDraft.chapter_number == chapter_number,
        )
        .first()
        is not None
    )


def to_list_item(draft: ChapterDraft) -> ChapterDraftListItem:
    return ChapterDraftListItem.model_validate(draft)


def to_read(draft: ChapterDraft) -> ChapterDraftRead:
    return ChapterDraftRead.model_validate(draft)


async def generate_draft(
    db: Session,
    req: ChapterDraftGenerateRequest,
    prompt_builder,
) -> ChapterDraft:
    if not req.allow_new_version and check_exists(db, req.project_id, req.chapter_number):
        raise ValueError(
            f"chapter {req.chapter_number} already exists for project {req.project_id}. "
            "set allow_new_version=true to create a new version."
        )

    system_prompt, user_prompt = await prompt_builder(req)

    ai_req = AIRequest(
        task="daily_writer_generate",
        messages=[
            AIMessage(role="system", content=system_prompt),
            AIMessage(role="user", content=user_prompt),
        ],
    )
    ai_resp = await generate_text(ai_req)

    if not ai_resp.content.strip():
        raise ValueError("AI Gateway returned empty content")

    if ai_resp.error:
        raise ValueError(f"AI Gateway error: {ai_resp.error}")

    draft_data = ChapterDraftCreate(
        project_id=req.project_id,
        chapter_number=req.chapter_number,
        title=req.title or f"Chapter {req.chapter_number}",
        content=ai_resp.content,
        status="draft",
        source="daily_writer",
        writing_goal=req.writing_goal,
        prompt_snapshot=json.dumps(
            {"system": system_prompt[:500], "user": user_prompt[:500]},
            ensure_ascii=False,
        ),
        context_snapshot=json.dumps(
            {"ai_response_error": ai_resp.error},
            ensure_ascii=False,
        ),
    )

    return create_draft(db, draft_data)
