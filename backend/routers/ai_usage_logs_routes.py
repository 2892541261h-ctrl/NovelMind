from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.ai_usage_log_schema import UsageLogListItem, UsageLogRead, UsageSummary
from services import aul_service

router = APIRouter(prefix="/api/ai/usage-logs", tags=["ai-usage-logs"])

@router.get("", response_model=list[UsageLogListItem])
def list_logs(db: Session = Depends(get_db)):
    return aul_service.list_logs(db)

@router.get("/summary", response_model=UsageSummary)
def get_summary(db: Session = Depends(get_db)):
    return aul_service.get_summary(db)

@router.get("/{log_id}", response_model=UsageLogRead)
def get_log(log_id: int, db: Session = Depends(get_db)):
    l = aul_service.get_log(db, log_id)
    if not l: raise HTTPException(404, "Log not found")
    return l
