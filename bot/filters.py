from aiogram.filters import Filter
from aiogram.types import CallbackQuery, Message

from .config import config


def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


class IsAdmin(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return is_admin(event.from_user.id)
