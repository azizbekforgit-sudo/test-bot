import html

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, Message


def esc(text: str | None) -> str:
    return html.escape(text or "")


def percent(correct: int, total: int) -> str:
    return f"{correct / total * 100:.1f}".rstrip("0").rstrip(".") if total else "0"


async def safe_edit(message: Message, text: str, markup: InlineKeyboardMarkup | None = None) -> None:
    """Xabarni tahrirlaydi; tahrirlab bo'lmasa (masalan, rasmli xabar) yangisini yuboradi."""
    try:
        await message.edit_text(text, reply_markup=markup, disable_web_page_preview=True)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            return
        await message.answer(text, reply_markup=markup, disable_web_page_preview=True)
