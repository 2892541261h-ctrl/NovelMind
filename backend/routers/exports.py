from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from services.export_service import export_markdown, export_txt

router = APIRouter(prefix="/api/exports", tags=["exports"])


@router.get("/project/{project_id}/markdown")
def export_project_markdown(project_id: int):
    text = export_markdown(project_id)
    return PlainTextResponse(content=text, media_type="text/markdown; charset=utf-8")


@router.get("/project/{project_id}/txt")
def export_project_txt(project_id: int):
    text = export_txt(project_id)
    return PlainTextResponse(content=text, media_type="text/plain; charset=utf-8")
