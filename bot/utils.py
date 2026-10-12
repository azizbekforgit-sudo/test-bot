import html

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message

from . import keyboards as kb
from .db import Database, Material
from .filters import is_director


def esc(text: str | None) -> str:
    return html.escape(text or "")


def room_link(bot_username: str, code: str) -> str:
    return f"https://t.me/{bot_username}?start=room_{code}"


def invite_link(bot_username: str, token: str) -> str:
    return f"https://t.me/{bot_username}?start=teacher_{token}"


async def menu_for(user_id: int, db: Database):
    return kb.main_menu(is_director(user_id), await db.is_teacher(user_id))


async def safe_edit(message: Message, text: str, markup: InlineKeyboardMarkup | None = None) -> None:
    """Xabarni tahrirlaydi; tahrirlab bo'lmasa yangisini yuboradi."""
    try:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)


async def send_materials(message: Message, materials: list[Material]) -> None:
    """Test materiallarini (matn/rasm/fayl) foydalanuvchiga yuboradi."""
    for m in materials:
        caption = m.text or None
        if m.kind == "photo":
            await message.answer_photo(m.file_id, caption=caption)
        elif m.kind == "document":
            await message.answer_document(m.file_id, caption=caption)
        elif m.text:
            await message.answer(m.text)
