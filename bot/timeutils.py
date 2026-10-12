"""Sana va vaqt bilan ishlash. Barcha vaqtlar .env dagi TIMEZONE bo'yicha."""

import re
from datetime import datetime

from .config import config

UPCOMING, ACTIVE, FINISHED = "upcoming", "active", "finished"


def now() -> datetime:
    return datetime.now(config.tz)


def parse_date(text: str) -> str:
    """'12.07.2026', '12/07/2026', '12-07-26' -> '12.07.2026'. Xato bo'lsa ValueError."""
    m = re.fullmatch(r"\s*(\d{1,2})[./-](\d{1,2})[./-](\d{2}|\d{4})\s*", text or "")
    if not m:
        raise ValueError
    d, mo, y = (int(x) for x in m.groups())
    if y < 100:
        y += 2000
    return datetime(y, mo, d).strftime("%d.%m.%Y")


def parse_time(text: str) -> str:
    """'10:00', '10.00', '9:5' -> '10:00', '09:05'. Xato bo'lsa ValueError."""
    m = re.fullmatch(r"\s*(\d{1,2})[:.](\d{1,2})\s*", text or "")
    if not m:
        raise ValueError
    h, mi = int(m.group(1)), int(m.group(2))
    if not (0 <= h <= 23 and 0 <= mi <= 59):
        raise ValueError
    return f"{h:02d}:{mi:02d}"


def to_dt(date: str, time: str) -> datetime:
    return datetime.strptime(f"{date} {time}", "%d.%m.%Y %H:%M").replace(tzinfo=config.tz)


def status(date: str, start: str, end: str) -> str:
    n = now()
    if n < to_dt(date, start):
        return UPCOMING
    if n >= to_dt(date, end):
        return FINISHED
    return ACTIVE


def status_of(test) -> str:
    """Test obyekti (yoki shunga o'xshash) uchun holat."""
    return status(test.date, test.start_time, test.end_time)
