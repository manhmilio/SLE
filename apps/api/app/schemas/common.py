"""
schemas/common.py — Schema chung dùng chung nhiều router
"""
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class SuccessEnvelope(BaseModel, Generic[T]):
    """Bọc response thành công theo format {success, data} thống nhất toàn API."""
    success: bool = True
    data: T


class MessageData(BaseModel):
    """Dùng cho các response chỉ trả về 1 message (logout, logout-all...)."""
    message: str