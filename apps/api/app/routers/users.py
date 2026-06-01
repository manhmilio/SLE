from fastapi import APIRouter, HTTPException, status

from app.dependencies import CurrentUser, DB
from app.schemas.user import UserProfile, UpdateProfileRequest, ChangePasswordRequest
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfile)
async def get_my_profile(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_my_profile(
    data: UpdateProfileRequest,
    current_user: CurrentUser,
    db: DB,
):
    # Phải có ít nhất 1 field được gửi lên
    if data.display_name is None and data.avatar_url is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one field must be provided",
        )

    updated = await user_service.update_profile(db, current_user, data)
    return updated


@router.patch("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DB,
):
    try:
        await user_service.change_password(
            db, current_user, data.old_password, data.new_password
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )