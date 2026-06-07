from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content import Card, StudySet
from app.schemas.card import CardCreate, CardUpdate


class CardService:

    async def _get_set_if_owner(
        self, db: AsyncSession, set_id: UUID, user_id: UUID
    ) -> Optional[StudySet]:
        """Trả về set nếu tồn tại và user là owner, ngược lại None."""
        result = await db.execute(
            select(StudySet).where(
                StudySet.id == set_id,
                StudySet.owner_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_cards(
        self,
        db: AsyncSession,
        set_id: UUID,
        user_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Card], int]:
        """
        Trả về (danh sách cards, tổng số cards).
        Set phải là của user HOẶC public.
        """
        # Kiểm tra set tồn tại và có quyền xem
        set_result = await db.execute(
            select(StudySet).where(
                StudySet.id == set_id,
                (StudySet.owner_id == user_id) | (StudySet.is_public == True),
            )
        )
        study_set = set_result.scalar_one_or_none()
        if not study_set:
            return [], 0

        # Đếm tổng
        count_result = await db.execute(
            select(Card).where(Card.study_set_id == set_id)
        )
        all_cards = count_result.scalars().all()
        total = len(all_cards)

        # Pagination — sắp xếp theo order
        offset = (page - 1) * page_size
        result = await db.execute(
            select(Card)
            .where(Card.study_set_id == set_id)
            .order_by(Card.order)
            .offset(offset)
            .limit(page_size)
        )
        cards = result.scalars().all()
        return list(cards), total

    async def get_card(
        self, db: AsyncSession, set_id: UUID, card_id: UUID, user_id: UUID
    ) -> Optional[Card]:
        """Lấy 1 card — set phải là của user hoặc public."""
        set_result = await db.execute(
            select(StudySet).where(
                StudySet.id == set_id,
                (StudySet.owner_id == user_id) | (StudySet.is_public == True),
            )
        )
        if not set_result.scalar_one_or_none():
            return None

        result = await db.execute(
            select(Card).where(Card.id == card_id, Card.study_set_id == set_id)
        )
        return result.scalar_one_or_none()

    async def create_card(
        self, db: AsyncSession, set_id: UUID, user_id: UUID, data: CardCreate
    ) -> Optional[Card]:
        """Tạo card mới — chỉ owner mới được tạo."""
        study_set = await self._get_set_if_owner(db, set_id, user_id)
        if not study_set:
            return None

        # Tính order cho card mới = max(order) hiện tại + 1.0
        result = await db.execute(
            select(Card.order)
            .where(Card.study_set_id == set_id)
            .order_by(Card.order.desc())
            .limit(1)
        )
        last_order = result.scalar_one_or_none()
        new_order = (last_order + 1.0) if last_order is not None else 1.0

        card = Card(
            study_set_id=set_id,
            owner_id=user_id,
            front=data.front,
            back=data.back,
            image_url=data.image_url,
            order=new_order,
        )
        db.add(card)
        await db.commit()
        await db.refresh(card)
        return card

    async def update_card(
        self,
        db: AsyncSession,
        set_id: UUID,
        card_id: UUID,
        user_id: UUID,
        data: CardUpdate,
    ) -> Optional[Card]:
        """Cập nhật card — chỉ owner mới được sửa."""
        study_set = await self._get_set_if_owner(db, set_id, user_id)
        if not study_set:
            return None

        result = await db.execute(
            select(Card).where(Card.id == card_id, Card.study_set_id == set_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        await db.commit()
        await db.refresh(card)
        return card

    async def delete_card(
        self, db: AsyncSession, set_id: UUID, card_id: UUID, user_id: UUID
    ) -> bool:
        """Xóa card — chỉ owner mới được xóa. Trả về True nếu xóa thành công."""
        study_set = await self._get_set_if_owner(db, set_id, user_id)
        if not study_set:
            return False

        result = await db.execute(
            select(Card).where(Card.id == card_id, Card.study_set_id == set_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            return False

        await db.delete(card)
        await db.commit()
        return True