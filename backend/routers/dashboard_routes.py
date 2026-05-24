from fastapi import APIRouter
from services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/api/project-dashboard", tags=["dashboard"])

@router.get("/summary")
def dashboard_summary(project_id: int):
    return get_dashboard_summary(project_id)
