from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.chapter_review_schema import ChapterReviewListItem, ChapterReviewRead, SuggestRewriteResponse
from services import cr_service, chapter_draft_service, formal_chapter_service

router = APIRouter(prefix="/api/chapter-reviews", tags=["chapter-reviews"])

@router.get("", response_model=list[ChapterReviewListItem])
def list_reviews(project_id: int, db: Session = Depends(get_db)):
    return cr_service.list_reviews(db, project_id)

@router.get("/{review_id}", response_model=ChapterReviewRead)
def get_review(review_id: int, db: Session = Depends(get_db)):
    r = cr_service.get_review(db, review_id)
    if not r: raise HTTPException(404, "Review not found")
    return r

@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: int, db: Session = Depends(get_db)):
    ok = cr_service.delete_review(db, review_id)
    if not ok: raise HTTPException(404, "Review not found")

@router.post("/review-draft/{draft_id}", response_model=ChapterReviewRead, status_code=201)
async def review_draft(draft_id: int, db: Session = Depends(get_db)):
    d = chapter_draft_service.get_draft(db, draft_id)
    if not d: raise HTTPException(404, "Draft not found")
    content = d.content or ""
    if not content.strip(): raise HTTPException(400, "Draft content is empty")
    return await cr_service.review_content(db, d.project_id, d.chapter_number, content,
        draft_id=d.id, writing_goal=d.writing_goal)

@router.post("/review-formal/{chapter_id}", response_model=ChapterReviewRead, status_code=201)
async def review_formal(chapter_id: int, db: Session = Depends(get_db)):
    ch = formal_chapter_service.get_chapter(db, chapter_id)
    if not ch: raise HTTPException(404, "Chapter not found")
    content = ch.content or ""
    if not content.strip(): raise HTTPException(400, "Chapter content is empty")
    return await cr_service.review_content(db, ch.project_id, ch.chapter_number, content,
        formal_chapter_id=ch.id)

@router.post("/suggest-rewrite-draft/{draft_id}", response_model=SuggestRewriteResponse)
async def suggest_rewrite(draft_id: int, db: Session = Depends(get_db)):
    d = chapter_draft_service.get_draft(db, draft_id)
    if not d: raise HTTPException(404, "Draft not found")
    content = d.content or ""
    if not content.strip(): raise HTTPException(400, "Draft content is empty")
    reviews = cr_service.list_reviews(db, d.project_id)
    relevant = [r for r in reviews if r.chapter_number == d.chapter_number]
    issues = "\n".join([r.issues for r in relevant]) if relevant else ""
    result = await cr_service.suggest_rewrite(db, content, issues, d.title or "")
    return SuggestRewriteResponse(**result)
