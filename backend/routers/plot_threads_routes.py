from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.plot_thread_schema import PlotThreadCreate, PlotThreadListItem, PlotThreadRead, PlotThreadUpdate
from services import pt_service

router = APIRouter(prefix="/api/plot-threads", tags=["plot-threads"])

@router.get("", response_model=list[PlotThreadListItem])
def list_threads(project_id: int, db: Session = Depends(get_db)):
    return pt_service.list_threads(db, project_id)

@router.post("", response_model=PlotThreadRead, status_code=201)
def create_thread(data: PlotThreadCreate, db: Session = Depends(get_db)):
    return pt_service.create_thread(db, data)

@router.get("/{thread_id}", response_model=PlotThreadRead)
def get_thread(thread_id: int, db: Session = Depends(get_db)):
    t = pt_service.get_thread(db, thread_id)
    if not t: raise HTTPException(404, "Plot thread not found")
    return t

@router.patch("/{thread_id}", response_model=PlotThreadRead)
def update_thread(thread_id: int, data: PlotThreadUpdate, db: Session = Depends(get_db)):
    t = pt_service.update_thread(db, thread_id, data)
    if not t: raise HTTPException(404, "Plot thread not found")
    return t

@router.delete("/{thread_id}", status_code=204)
def delete_thread(thread_id: int, db: Session = Depends(get_db)):
    ok = pt_service.delete_thread(db, thread_id)
    if not ok: raise HTTPException(404, "Plot thread not found")
