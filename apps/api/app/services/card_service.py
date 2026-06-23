from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.services.config_service import get_current_config

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

        config = await get_current_config(db)
        if study_set.card_count >= config.max_cards_per_set:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum number of cards reached ({config.max_cards_per_set})",
            )

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
    
    async def reorder_card(
        self,
        db: AsyncSession,
        set_id: UUID,
        card_id: UUID,
        user_id: UUID,
        prev_order: Optional[float],
        next_order: Optional[float],
    ) -> Optional[Card]:
        """
        Đặt lại vị trí card bằng FLOAT order.
        - prev_order: order của card phía trên (None nếu lên đầu)
        - next_order: order của card phía dưới (None nếu xuống cuối)
        """
        study_set = await self._get_set_if_owner(db, set_id, user_id)
        if not study_set:
            return None

        result = await db.execute(
            select(Card).where(Card.id == card_id, Card.study_set_id == set_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            return None

        # Tính order mới
        if prev_order is None and next_order is None:
            new_order = 1.0
        elif prev_order is None:
            assert next_order is not None
            new_order = next_order - 1.0
        elif next_order is None:
            new_order = prev_order + 1.0
        else:
            new_order = (prev_order + next_order) / 2.0
            
        card.order = new_order
        await db.flush()

        # Kiểm tra nếu cần rebalance
        needs_rebalance = False
        if prev_order is not None and abs(new_order - prev_order) < 1e-9:
            needs_rebalance = True
        if next_order is not None and abs(next_order - new_order) < 1e-9:
            needs_rebalance = True

        if needs_rebalance:
            await self._rebalance(db, set_id)
            # Refresh lại card sau rebalance
            await db.refresh(card)

        await db.commit()
        await db.refresh(card)
        return card

    async def _rebalance(self, db: AsyncSession, set_id: UUID) -> None:
        """Reset toàn bộ order về 1.0, 2.0, 3.0, ... theo thứ tự hiện tại."""
        result = await db.execute(
            select(Card)
            .where(Card.study_set_id == set_id)
            .order_by(Card.order)
        )
        cards = result.scalars().all()
        for i, c in enumerate(cards, start=1):
            c.order = float(i)
        await db.flush()