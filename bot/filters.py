from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from .config import config
from .db import Database


def is_director(user_id: int) -> bool:
    return user_id in config.director_ids


class IsDirector(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return is_director(event.from_user.id)


class IsTeacher(Filter):
    """O'qituvchi yoki direktor (direktor ham xona yarata oladi)."""

    async def __call__(self, event: Message | CallbackQuery, db: Database) -> bool:
        uid = event.from_user.id
        return is_director(uid) or await db.is_teacher(uid)
