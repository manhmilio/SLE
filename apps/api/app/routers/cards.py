from uuid import UUID
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile

from app.schemas.card import CardCreate, CardUpdate, CardResponse, CardReorderRequest
from app.services.card_service import CardService
from app.dependencies import CurrentUser, DB
from app.services.minio_service import upload_card_image
from app.services.config_service import get_current_config

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


@router.patch("/{set_id}/cards/{card_id}/order", response_model=CardResponse)
async def reorder_card(
    set_id: UUID,
    card_id: UUID,
    data: CardReorderRequest,
    current_user: CurrentUser,
    db: DB,
):
    card = await service.reorder_card(
        db, set_id, card_id, current_user.id,
        data.prev_order, data.next_order,
    )
    if not card:
        raise HTTPException(status_code=404, detail="Card not found or access denied")
    return card

@router.post("/{set_id}/cards/{card_id}/image", response_model=CardResponse)
async def upload_card_image_endpoint(
    set_id: UUID,
    card_id: UUID,
    file: UploadFile,
    current_user: CurrentUser,
    db: DB,
):
    # Kiểm tra quyền và card tồn tại
    card = await service.get_card(db, set_id, card_id, current_user.id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Chỉ owner mới được upload
    if card.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    file_data = await file.read()
    content_type = file.content_type or ""
    config = await get_current_config(db)

    try:
        image_url = upload_card_image(
            file_data, content_type, str(card_id), max_size_mb=config.max_image_size_mb
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Cập nhật image_url vào card
    updated_card = await service.update_card(
        db, set_id, card_id, current_user.id,
        CardUpdate.model_validate({"image_url": image_url}),
    )
    assert updated_card is not None
    return updated_card