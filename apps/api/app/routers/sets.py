from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CurrentUser, DB
from app.schemas.study_set import StudySetCreate, StudySetUpdate, StudySetResponse
from app.services.set_service import SetService

router = APIRouter(prefix="/sets", tags=["Study Sets"])


@router.get("", response_model=List[StudySetResponse])
async def list_sets(
    current_user: CurrentUser,
    db: DB,
    search: Optional[str] = Query(None),
    folder_id: Optional[UUID] = Query(None),
):
    return await SetService.get_all(db, current_user.id, search, folder_id)


@router.post("", response_model=StudySetResponse, status_code=status.HTTP_201_CREATED)
async def create_set(data: StudySetCreate, current_user: CurrentUser, db: DB):
    try:
        return await SetService.create(db, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{set_id}", response_model=StudySetResponse)
async def get_set(set_id: UUID, current_user: CurrentUser, db: DB):
    study_set = await SetService.get_by_id(db, set_id, current_user.id)
    if not study_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study set not found")
    return study_set


@router.patch("/{set_id}", response_model=StudySetResponse)
async def update_set(set_id: UUID, data: StudySetUpdate, current_user: CurrentUser, db: DB):
    study_set = await SetService.get_by_id(db, set_id, current_user.id)
    if not study_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study set not found")

    if study_set.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    try:
        return await SetService.update(db, study_set, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_set(set_id: UUID, current_user: CurrentUser, db: DB):
    study_set = await SetService.get_by_id(db, set_id, current_user.id)
    if not study_set:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study set not found")

    if study_set.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await SetService.delete(db, study_set)