from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas.reference_novel import (
    ReferenceNovelCreate,
    ReferenceNovelResponse,
    ReferenceNovelUpdate,
)
from schemas.reference_profile import ReferenceProfileCreate, ReferenceProfileResponse
from services import reference_novel_service as svc

router = APIRouter(prefix="/api/reference-novels", tags=["reference-novels"])


@router.get("", response_model=list[ReferenceNovelResponse])
def list_novels(project_id: int, db: Session = Depends(get_db)):
    return svc.list_novels(db, project_id)


@router.post("", response_model=ReferenceNovelResponse, status_code=201)
def create_novel(data: ReferenceNovelCreate, db: Session = Depends(get_db)):
    return svc.create_novel(db, data)


@router.get("/{novel_id}", response_model=ReferenceNovelResponse)
def get_novel(novel_id: int, db: Session = Depends(get_db)):
    novel = svc.get_novel(db, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Reference novel not found")
    return novel


@router.put("/{novel_id}", response_model=ReferenceNovelResponse)
def update_novel(novel_id: int, data: ReferenceNovelUpdate, db: Session = Depends(get_db)):
    novel = svc.update_novel(db, novel_id, data)
    if not novel:
        raise HTTPException(status_code=404, detail="Reference novel not found")
    return novel


@router.delete("/{novel_id}", status_code=204)
def delete_novel(novel_id: int, db: Session = Depends(get_db)):
    ok = svc.delete_novel(db, novel_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Reference novel not found")


@router.post("/{novel_id}/analyze", response_model=ReferenceProfileResponse, status_code=201)
async def analyze_novel(novel_id: int, db: Session = Depends(get_db)):
    novel = svc.get_novel(db, novel_id)
    if not novel:
        raise HTTPException(status_code=404, detail="Reference novel not found")
    profile_data = ReferenceProfileCreate(novel_id=novel_id, project_id=novel.project_id)
    return await svc.generate_profile(db, profile_data)


@router.get("/{novel_id}/profile", response_model=ReferenceProfileResponse)
def get_novel_profile(novel_id: int, db: Session = Depends(get_db)):
    profile = svc.get_profile_by_novel(db, novel_id)
    if not profile:
        raise HTTPException(status_code=404, detail="No profile found. Run analysis first.")
    return profile


@router.get("/profiles/{profile_id}", response_model=ReferenceProfileResponse)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = svc.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.delete("/profiles/{profile_id}", status_code=204)
def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    ok = svc.delete_profile(db, profile_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Profile not found")
