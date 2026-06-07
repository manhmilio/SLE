from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from app.schemas.card import CardCreate, CardUpdate, CardResponse
from app.services.card_service import CardService
from app.dependencies import CurrentUser, DB

router = APIRouter(prefix="/sets", tags=["cards"])
service = CardService()


@router.get("/{set_id}/cards", response_model=dict)
async def list_cards(
    set_id: UUID,
    current_user: CurrentUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    cards, total = await service.get_cards(
        db, set_id, current_user.id, page, page_size
    )
    return {
        "items": [CardResponse.model_validate(c) for c in cards],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{set_id}/cards/{card_id}", response_model=CardResponse)
async def get_card(
    set_id: UUID,
    card_id: UUID,
    current_user: CurrentUser,
    db: DB,
):
    card = await service.get_card(db, set_id, card_id, current_user.id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post("/{set_id}/cards", response_model=CardResponse, status_code=201)
async def create_card(
    set_id: UUID,
    data: CardCreate,
    current_user: CurrentUser,
    db: DB,
):
    card = await service.create_card(db, set_id, current_user.id, data)
    if not card:
        raise HTTPException(status_code=404, detail="Study set not found or access denied")
    return card


@router.patch("/{set_id}/cards/{card_id}", response_model=CardResponse)
async def update_card(
    set_id: UUID,
    card_id: UUID,
    data: CardUpdate,
    current_user: CurrentUser,
    db: DB,
):
    card = await service.update_card(db, set_id, card_id, current_user.id, data)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found or access denied")
    return card


@router.delete("/{set_id}/cards/{card_id}", status_code=204)
async def delete_card(
    set_id: UUID,
    card_id: UUID,
    current_user: CurrentUser,
    db: DB,
):
    deleted = await service.delete_card(db, set_id, card_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Card not found or access denied")