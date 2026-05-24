from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.world_setting import WorldSetting
from schemas.world_setting import WorldSettingCreate, WorldSettingUpdate, WorldSettingResponse

router = APIRouter(tags=["world-settings"])


@router.get("/api/projects/{project_id}/world-settings", response_model=list[WorldSettingResponse])
def list_world_settings(project_id: int, db: Session = Depends(get_db)):
    return db.query(WorldSetting).filter(WorldSetting.project_id == project_id).all()


@router.post("/api/projects/{project_id}/world-settings", response_model=WorldSettingResponse, status_code=201)
def create_world_setting(project_id: int, data: WorldSettingCreate, db: Session = Depends(get_db)):
    ws = WorldSetting(project_id=project_id, **data.model_dump(exclude={"project_id"}))
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws


@router.get("/api/world-settings/{setting_id}", response_model=WorldSettingResponse)
def get_world_setting(setting_id: int, db: Session = Depends(get_db)):
    ws = db.query(WorldSetting).filter(WorldSetting.id == setting_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="World setting not found")
    return ws


@router.put("/api/world-settings/{setting_id}", response_model=WorldSettingResponse)
def update_world_setting(setting_id: int, data: WorldSettingUpdate, db: Session = Depends(get_db)):
    ws = db.query(WorldSetting).filter(WorldSetting.id == setting_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="World setting not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(ws, key, val)
    db.commit()
    db.refresh(ws)
    return ws


@router.delete("/api/world-settings/{setting_id}", status_code=204)
def delete_world_setting(setting_id: int, db: Session = Depends(get_db)):
    ws = db.query(WorldSetting).filter(WorldSetting.id == setting_id).first()
    if not ws:
        raise HTTPException(status_code=404, detail="World setting not found")
    db.delete(ws)
    db.commit()
