from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DB
from app.schemas.folder import FolderCreate, FolderUpdate, FolderResponse
from app.services.folder_service import FolderService

router = APIRouter(prefix="/folders", tags=["Folders"])


@router.get("", response_model=List[FolderResponse])
async def list_folders(current_user: CurrentUser, db: DB):
    """
    Lấy danh sách tất cả folders của user hiện tại.
    Sắp xếp theo tên A-Z.
    """
    return await FolderService.get_all(db, current_user.id)


@router.post("", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(data: FolderCreate, current_user: CurrentUser, db: DB):
    """
    Tạo folder mới.
    - 201: Tạo thành công
    - 409: Tên folder đã tồn tại (trùng per user)
    """
    try:
        return await FolderService.create(db, current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(folder_id: UUID, current_user: CurrentUser, db: DB):
    """
    Xem chi tiết 1 folder.
    - 404: Không tồn tại hoặc không thuộc user hiện tại
    """
    folder = await FolderService.get_by_id(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )
    return folder


@router.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: UUID, data: FolderUpdate, current_user: CurrentUser, db: DB
):
    """
    Cập nhật folder (partial update — chỉ gửi field cần đổi).
    - 404: Không tồn tại hoặc không thuộc user hiện tại
    - 409: Tên mới đã được dùng bởi folder khác
    """
    folder = await FolderService.get_by_id(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )
    try:
        return await FolderService.update(db, folder, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(folder_id: UUID, current_user: CurrentUser, db: DB):
    """
    Xóa folder.
    Sets bên trong KHÔNG bị xóa — folder_id của chúng tự động về NULL.
    - 204: Xóa thành công
    - 404: Không tồn tại hoặc không thuộc user hiện tại
    """
    folder = await FolderService.get_by_id(db, folder_id, current_user.id)
    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found",
        )
    await FolderService.delete(db, folder)