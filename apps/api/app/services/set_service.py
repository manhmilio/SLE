from uuid import UUID
from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.content import StudySet, Folder, Card
from app.models.learning import SetClone
from fastapi import HTTPException, status
from app.services.config_service import get_current_config

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

        config = await get_current_config(db)
        current_count = await db.scalar(
            select(func.count()).select_from(StudySet).where(StudySet.owner_id == user_id)
        )
        if (current_count or 0) >= config.max_sets_per_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum number of sets reached ({config.max_sets_per_user})",
            )

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

    @staticmethod
    async def clone(
        db: AsyncSession,
        set_id: UUID,
        user_id: UUID,
    ) -> StudySet:
        # 1. Lấy set gốc — public hoặc của chính mình
        original = await SetService.get_by_id(db, set_id, user_id)
        if not original:
            raise ValueError("Study set not found")

        # 2. Tạo set mới — copy toàn bộ fields, đổi owner + gắn cloned_from
        new_set = StudySet(
            owner_id=user_id,
            title=original.title,
            description=original.description,
            tags=original.tags,
            is_public=False,          # clone mặc định là private
            folder_id=None,           # không kế thừa folder của người khác
            cloned_from=original.id,
        )
        db.add(new_set)
        await db.flush()   # flush để new_set.id có giá trị, chưa commit

        # 3. Copy toàn bộ cards từ set gốc
        cards_result = await db.execute(
            select(Card)
            .where(Card.study_set_id == original.id)
            .order_by(Card.order.asc())
        )
        original_cards = cards_result.scalars().all()

        for card in original_cards:
            new_card = Card(
                study_set_id=new_set.id,
                owner_id=user_id,
                front=card.front,
                back=card.back,
                image_url=card.image_url,
                order=card.order,
            )
            db.add(new_card)

        # 4. Ghi analytics vào set_clones
        clone_record = SetClone(
            original_set_id=original.id,
            original_owner_id=original.owner_id,
            cloned_set_id=new_set.id,
            cloned_by=user_id,
        )
        db.add(clone_record)

        await db.commit()
        await db.refresh(new_set)
        return new_set