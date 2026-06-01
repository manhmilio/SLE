from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UpdateProfileRequest
from app.core.security import verify_password, hash_password


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_profile(
    db: AsyncSession,
    user: User,
    data: UpdateProfileRequest,
) -> User:
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def change_password(
    db: AsyncSession,
    user: User,
    old_password: str,
    new_password: str,
) -> None:
    """Raises ValueError nếu old_password sai."""
    if not verify_password(old_password, user.password):
        raise ValueError("Current password is incorrect")

    user.password = hash_password(new_password)
    db.add(user)
    await db.commit()