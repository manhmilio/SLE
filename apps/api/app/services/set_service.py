from uuid import UUID
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.content import StudySet, Folder
from app.schemas.study_set import StudySetCreate, StudySetUpdate


class SetService:

    @staticmethod
    async def get_all(
        db: AsyncSession,
        user_id: UUID,
        search: Optional[str] = None,
        folder_id: Optional[UUID] = None,
    ) -> Sequence[StudySet]:
        q = select(StudySet).where(StudySet.owner_id == user_id)

        if folder_id is not None:
            q = q.where(StudySet.folder_id == folder_id)

        if search:
            q = q.where(
                StudySet.fts_vector.op("@@")(
                    func.plainto_tsquery("simple", search)
                )
            )

        q = q.order_by(StudySet.updated_at.desc())
        result = await db.execute(q)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        set_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> StudySet | None:
        result = await db.execute(
            select(StudySet).where(StudySet.id == set_id)
        )
        study_set = result.scalar_one_or_none()

        if not study_set:
            return None

        # Public → ai cũng xem được, Private → chỉ owner
        if not study_set.is_public and study_set.owner_id != user_id:
            return None

        return study_set

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        data: StudySetCreate,
    ) -> StudySet:
        if data.folder_id is not None:
            folder = await db.get(Folder, data.folder_id)
            if not folder or folder.owner_id != user_id:
                raise ValueError("Folder not found")

        study_set = StudySet(owner_id=user_id, **data.model_dump())
        db.add(study_set)
        await db.commit()
        await db.refresh(study_set)
        return study_set

    @staticmethod
    async def update(
        db: AsyncSession,
        study_set: StudySet,
        user_id: UUID,
        data: StudySetUpdate,
    ) -> StudySet:
        update_fields = data.model_dump(exclude_unset=True)

        if not update_fields:
            return study_set

        if "folder_id" in update_fields and update_fields["folder_id"] is not None:
            folder = await db.get(Folder, update_fields["folder_id"])
            if not folder or folder.owner_id != user_id:
                raise ValueError("Folder not found")

        for field, value in update_fields.items():
            setattr(study_set, field, value)

        await db.commit()
        await db.refresh(study_set)
        return study_set

    @staticmethod
    async def delete(db: AsyncSession, study_set: StudySet) -> None:
        await db.delete(study_set)
        await db.commit()