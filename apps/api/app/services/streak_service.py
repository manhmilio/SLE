from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


async def update_streak(user: User, db: AsyncSession) -> None:
    """
    Cập nhật streak và last_studied sau khi session kết thúc.
    Tính theo ngày UTC — không phải 24h rolling.
    """
    now = datetime.now(timezone.utc)
    today = now.date()

    if user.last_studied is None:
        # Lần đầu tiên học
        user.streak = 1
    else:
        last = user.last_studied.date()

        if last == today:
            # Đã học hôm nay rồi → giữ nguyên streak
            pass
        elif last == today - timedelta(days=1):
            # Học liên tiếp → cộng thêm 1
            user.streak += 1
        else:
            # Bỏ ít nhất 1 ngày → reset về 1
            user.streak = 1

    user.last_studied = now
    # Không commit ở đây — để caller quyết định