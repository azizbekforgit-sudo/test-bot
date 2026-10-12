"""Kanal uchun test kartasi (e'lon posti)."""

import html
import re

from aiogram import Bot
from aiogram.types import Message

BLANK = "________"
CAPTION_LIMIT = 1024


def _e(text: str | None) -> str:
    return html.escape(text or "")


def channel_username(channel: str | None) -> str | None:
    """'@kanal', 'https://t.me/kanal', 't.me/kanal', 'kanal' -> 'kanal'."""
    if not channel:
        return None
    m = re.fullmatch(r"\s*(?:https?://)?(?:t\.me/|telegram\.me/|@)?([A-Za-z][A-Za-z0-9_]{3,31})/?\s*", channel)
    return m.group(1) if m else None


def find_channel(text: str | None, bot_username: str | None = None) -> str | None:
    """Matndan kanal nomini topadi. Admin butun kartani yuborsa ham ishlaydi:
    matndagi oxirgi @nom yoki t.me/nom olinadi (botning o'z nomi hisobga olinmaydi)."""
    skip = {"share", (bot_username or "").lower()}
    exact = channel_username(text)
    if exact:
        return exact if exact.lower() not in skip else None
    found = re.findall(r"(?:t\.me/|telegram\.me/|@)([A-Za-z][A-Za-z0-9_]{3,31})\b", text or "")
    found = [x for x in found if x.lower() not in skip]
    return found[-1] if found else None


def build_card(d: dict, bot_username: str, channel: str | None, blank: bool = False) -> str:
    """Kartani HTML ko'rinishida yasaydi. blank=True bo'lsa bo'sh joylar chiziqcha bilan to'ldiriladi."""

    def v(key: str) -> str:
        val = d.get(key) or ""
        return _e(val) if val else (BLANK if blank else "")

    code = d.get("code") or ""
    lines: list[str] = []

    head = " ".join(x for x in (v("hashtags"), v("date")) if x)
    if head:
        lines.append(head)
    if v("subtitle"):
        lines.append(v("subtitle"))
    lines.append("")
    lines.append(f"<blockquote>🏆 <b>{v('title') or BLANK}</b> ✅</blockquote>")
    lines.append(f"🕙 Test boshlandi: {v('start_time') or BLANK}")
    lines.append(f"🕧 Testni tugash vaqti: {v('end_time') or BLANK}")
    if v("subject"):
        lines += ["", f"☑️ <u>{v('subject')}</u>"]

    bot_link = f"https://t.me/{bot_username}" + (f"?start={code}" if code else "")
    lines += [
        "",
        f'🤖 Javob yuborish uchun : <a href="{bot_link}">@{bot_username}</a>',
        f"🔑 Test kodi : <code>{_e(code) or BLANK}</code>",
    ]
    if v("footer"):
        lines += ["", f"<blockquote>{v('footer')}</blockquote>"]

    ch = channel_username(channel)
    if ch:
        share = f"https://t.me/share/url?url=https://t.me/{ch}"
        lines += [
            "✅",
            f'🔗 <a href="{share}">Testni maksimal darajada tarqatib yuboring</a> ✉️',
            "",
            f"✈️ @{ch}",
        ]
    return "\n".join(lines)


def _visible_len(html_text: str) -> int:
    plain = html.unescape(re.sub(r"<[^>]+>", "", html_text))
    return len(plain.encode("utf-16-le")) // 2


async def send_card(bot: Bot, chat_id: int | str, d: dict, card: str) -> Message:
    """Kartani fayl bilan birga yuboradi. Matn izoh (caption) uchun uzun bo'lsa — alohida xabar."""
    kind, file_id = d.get("file_kind"), d.get("file_id")
    fits = _visible_len(card) <= CAPTION_LIMIT
    if kind == "document":
        if fits:
            return await bot.send_document(chat_id, file_id, caption=card)
        await bot.send_document(chat_id, file_id)
    elif kind == "photo":
        if fits:
            return await bot.send_photo(chat_id, file_id, caption=card)
        await bot.send_photo(chat_id, file_id)
    return await bot.send_message(chat_id, card, disable_web_page_preview=True)
