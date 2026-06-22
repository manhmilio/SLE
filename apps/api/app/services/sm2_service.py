from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional


# ── Constants (Phase 8 sẽ thay bằng system_config từ DB) ──────────────────────
INITIAL_EASE_FACTOR = 2.5
MIN_EASE_FACTOR = 1.3
KNOWN_THRESHOLD_DAYS = 7  # interval >= 7 ngày → card chuyển sang "known"


# ── Data classes ───────────────────────────────────────────────────────────────
@dataclass
class SM2Input:
    """State hiện tại của 1 card trong study_progress."""
    ease_factor: float = INITIAL_EASE_FACTOR
    interval: int = 0       # số ngày tới lần review tiếp theo
    repetitions: int = 0    # số lần trả lời đúng liên tiếp


@dataclass
class SM2Output:
    """Giá trị mới sau khi tính SM-2."""
    ease_factor: float
    interval: int
    repetitions: int
    next_review: datetime
    status: str  # "learning" | "known"


# ── Core function ──────────────────────────────────────────────────────────────
def calculate_sm2(
    current: SM2Input,
    quality: int,
    known_threshold_days: int = KNOWN_THRESHOLD_DAYS,
    min_ease_factor: float = MIN_EASE_FACTOR,
) -> SM2Output:
    """
    Tính SM-2 thuần logic, không truy cập DB.

    quality: 1–5
      >= 3  → đúng: tăng interval, điều chỉnh ease_factor
      < 3   → sai:  reset interval=1, giảm ease_factor, reset repetitions
    """
    ef = current.ease_factor
    interval = current.interval
    repetitions = current.repetitions

    if quality >= 3:
        # Đúng: tính ease_factor mới trước, rồi dùng nó tính interval
        new_ef = max(min_ease_factor, ef + 0.1 - (5 - quality) * 0.08)
        new_interval = round(max(1, interval) * new_ef)
        new_repetitions = repetitions + 1
    else:
        # Sai: giảm ease_factor, reset interval và repetitions
        new_ef = max(min_ease_factor, ef - 0.2)
        new_interval = 1
        new_repetitions = 0

    now = datetime.now(timezone.utc)
    next_review = now + timedelta(days=new_interval)

    status = "known" if new_interval >= known_threshold_days else "learning"

    return SM2Output(
        ease_factor=round(new_ef, 4),
        interval=new_interval,
        repetitions=new_repetitions,
        next_review=next_review,
        status=status,
    )


# ── Helper ─────────────────────────────────────────────────────────────────────
def map_quality(
    is_correct: bool,
    mode: str,
    explicit_quality: Optional[int] = None,
) -> int:
    """
    Chuyển đổi is_correct → quality (1–5).

    - mode "learn":     dùng explicit_quality do user chọn (bắt buộc 1–5)
    - flashcard/test/match: auto-map → đúng = 4, sai = 1
    """
    if mode == "learn":
        if explicit_quality is None:
            raise ValueError("mode 'learn' yêu cầu explicit_quality (1–5)")
        if not 1 <= explicit_quality <= 5:
            raise ValueError(f"quality phải từ 1–5, nhận được: {explicit_quality}")
        return explicit_quality

    return 4 if is_correct else 1