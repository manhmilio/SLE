from sqlalchemy.ext.asyncio import AsyncSession

from app.models.config import SystemConfig

CONFIG_ROW_ID = 1


async def get_current_config(db: AsyncSession) -> SystemConfig:
    """
    Trả về raw SystemConfig model (KHÔNG qua Pydantic schema), dùng cho
    các service nội bộ (sm2, stats, set, card, minio, auth) — khác với
    admin_service.get_config() là trả SystemConfigResponse cho API admin.
    """
    config = await db.get(SystemConfig, CONFIG_ROW_ID)
    if config is None:
        raise RuntimeError(
            "System config row (id=1) not found — check migration 004_system_config"
        )
    return config