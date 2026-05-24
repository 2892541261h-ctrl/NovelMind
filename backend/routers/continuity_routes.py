from fastapi import APIRouter
from services.continuity_service import get_continuity_snapshot

router = APIRouter(prefix="/api/continuity", tags=["continuity"])

@router.get("/report")
def continuity_report(project_id: int):
    return get_continuity_snapshot(project_id, 0)

@router.get("/snapshot")
def continuity_snapshot(project_id: int, chapter_number: int = 0):
    return get_continuity_snapshot(project_id, chapter_number)
