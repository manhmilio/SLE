from uuid import UUID
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.content import Folder
from app.schemas.folder import FolderCreate, FolderUpdate


class FolderService:

    @staticmethod
    async def get_all(db: AsyncSession, user_id: UUID) -> Sequence[Folder]:
        result = await db.execute(
            select(Folder)
            .where(Folder.owner_id == user_id)
            .order_by(Folder.name.asc())
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession, folder_id: UUID, user_id: UUID
    ) -> Folder | None:
        result = await db.execute(
            select(Folder).where(
                Folder.id == folder_id,
                Folder.owner_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession, user_id: UUID, data: FolderCreate
    ) -> Folder:
        folder = Folder(
            owner_id=user_id,
            name=data.name,
            description=data.description,
        )
        db.add(folder)
        try:
            await db.commit()
            await db.refresh(folder)
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Folder name '{data.name}' already exists")
        return folder

    @staticmethod
    async def update(
        db: AsyncSession, folder: Folder, data: FolderUpdate
    ) -> Folder:
        update_fields = data.model_dump(exclude_unset=True)
        if not update_fields:
            return folder
        for field, value in update_fields.items():
            setattr(folder, field, value)
        try:
            await db.commit()
            await db.refresh(folder)
        except IntegrityError:
            await db.rollback()
            raise ValueError(f"Folder name '{data.name}' already exists")
        return folder

    @staticmethod
    async def delete(db: AsyncSession, folder: Folder) -> None:
        await db.delete(folder)
        await db.commit()
