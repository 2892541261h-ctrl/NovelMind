from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.chapter_plan_schema import ChapterPlanCreate, ChapterPlanListItem, ChapterPlanRead, ChapterPlanUpdate
from services import cp_service

router = APIRouter(prefix="/api/chapter-plans", tags=["chapter-plans"])

@router.get("", response_model=list[ChapterPlanListItem])
def list_plans(project_id: int, db: Session = Depends(get_db)):
    return cp_service.list_plans(db, project_id)

@router.post("", response_model=ChapterPlanRead, status_code=201)
def create_plan(data: ChapterPlanCreate, db: Session = Depends(get_db)):
    try:
        return cp_service.create_plan(db, data)
    except ValueError as e:
        raise HTTPException(409, detail=str(e))

@router.get("/{plan_id}", response_model=ChapterPlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    cp = cp_service.get_plan(db, plan_id)
    if not cp: raise HTTPException(404, "Chapter plan not found")
    return cp

@router.patch("/{plan_id}", response_model=ChapterPlanRead)
def update_plan(plan_id: int, data: ChapterPlanUpdate, db: Session = Depends(get_db)):
    cp = cp_service.update_plan(db, plan_id, data)
    if not cp: raise HTTPException(404, "Chapter plan not found")
    return cp

@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    ok = cp_service.delete_plan(db, plan_id)
    if not ok: raise HTTPException(404, "Chapter plan not found")
