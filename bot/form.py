"""Test maydonlari: qanday so'raladi va qanday tekshiriladi."""

import re
from dataclasses import dataclass

from . import timeutils
from .answers import parse_answers


@dataclass(frozen=True)
class Field:
    label: str          # tugmadagi nom
    prompt: str         # adminga beriladigan savol
    required: bool = True


FIELDS: dict[str, Field] = {
    "title": Field(
        "🏆 Sarlavha",
        "🏆 Test <b>sarlavhasini</b> kiriting.\n\n"
        "Masalan: <code>2-MILLIY SERTIFIKAT DIAGNOSTIK TEST TOPSHIRIQLARI KITOBI (RASH MODELIDA)</code>",
    ),
    "subject": Field(
        "☑️ Fan / til",
        "☑️ <b>Fan yoki til</b> qatorini kiriting.\n\nMasalan: <code>Til: Qoraqalpoq tili</code>",
        required=False,
    ),
    "hashtags": Field(
        "#️⃣ Heshteglar",
        "#️⃣ <b>Heshteglarni</b> kiriting.\n\nMasalan: <code>#MOCKEXAM #RASH</code>",
        required=False,
    ),
    "subtitle": Field(
        "📌 Kichik sarlavha",
        "📌 Sana ostidagi <b>kichik sarlavhani</b> kiriting.\n\n"
        "Masalan: <code>Bilimni baholash agentligi formatida 🔴</code>",
        required=False,
    ),
    "footer": Field(
        "💬 Yakuniy matn",
        "💬 Kartaning pastidagi <b>yakuniy matnni</b> kiriting.\n\n"
        "Masalan: <code>Hammaga omad🚀 Test yakunlangach natijalar soat 13:00 gacha "
        "telegram kanalda e'lon qilinadi</code>",
        required=False,
    ),
    "date": Field(
        "📅 Sana",
        "📅 Test <b>sanasini</b> kiriting (kun.oy.yil).\n\nMasalan: <code>{today}</code>",
    ),
    "start_time": Field(
        "🕙 Boshlanish vaqti",
        "🕙 Test <b>boshlanish vaqtini</b> kiriting (soat:daqiqa).\n\nMasalan: <code>10:00</code>",
    ),
    "end_time": Field(
        "🕧 Tugash vaqti",
        "🕧 Test <b>tugash vaqtini</b> kiriting (soat:daqiqa).\n"
        "Shu vaqtdan keyin bot javob qabul qilmaydi.\n\nMasalan: <code>12:30</code>",
    ),
    "code": Field(
        "🔑 Test kodi",
        "🔑 <b>Test kodini</b> kiriting. O'quvchilar aynan shu kod orqali testga kiradi.\n"
        "Faqat lotin harflari, raqamlar, «-» va «_» (2–32 belgi).\n\nMasalan: <code>mock002</code>",
    ),
    "file": Field(
        "📎 Test fayli",
        "📎 Test <b>faylini</b> yuboring (PDF yoki rasm).\n"
        "Bu fayl kartaga biriktiriladi va testga kirgan o'quvchiga ham yuboriladi.",
        required=False,
    ),
    "answers": Field(
        "✅ To'g'ri javoblar",
        "✅ <b>To'g'ri javoblarni</b> kiriting.\n\n"
        "⚠️ Barcha javoblarni <b>bitta matnli xabarda</b> yuboring (rasm emas!) — "
        "shunda bot o'quvchilarni avtomatik tekshiradi.\n\n"
        "Masalan:\n<code>1 C\n2 A\n3 B</code>",
    ),
}

# Yangi test yaratishda so'raladigan tartib
NEW_TEST_ORDER = [
    "title", "subject", "hashtags", "subtitle", "footer",
    "date", "start_time", "end_time", "code", "file", "answers",
]
# Oldingi testdan nusxa olinganda faqat shular qayta so'raladi
CLONE_ORDER = ["date", "start_time", "end_time", "code"]

TEXT_LIMIT = 300
CODE_RE = re.compile(r"[A-Za-z0-9_-]{2,32}")


def prompt(field: str) -> str:
    return FIELDS[field].prompt.replace("{today}", timeutils.now().strftime("%d.%m.%Y"))


def validate_text(field: str, text: str, draft: dict) -> dict:
    """Matnli qiymatni tekshiradi. Natija — draft ga yoziladigan maydonlar.
    Xato bo'lsa ValueError(xabar) chiqaradi."""
    text = (text or "").strip()

    if field == "code":
        if not CODE_RE.fullmatch(text):
            raise ValueError("❌ Kod faqat lotin harflari, raqamlar, «-» va «_» dan iborat bo'lsin (2–32 belgi).")
        return {"code": text}

    if field == "date":
        try:
            return {"date": timeutils.parse_date(text)}
        except ValueError:
            raise ValueError("❌ Sanani tushunmadim. Masalan: <code>12.07.2026</code>")

    if field in ("start_time", "end_time"):
        try:
            value = timeutils.parse_time(text)
        except ValueError:
            raise ValueError("❌ Vaqtni tushunmadim. Masalan: <code>10:00</code>")
        start = value if field == "start_time" else draft.get("start_time")
        end = value if field == "end_time" else draft.get("end_time")
        if start and end and end <= start:
            raise ValueError(
                f"❌ Tugash vaqti ({end}) boshlanish vaqtidan ({start}) keyin bo'lishi kerak."
            )
        return {field: value}

    if field == "answers":
        answers = parse_answers(text)
        if not answers:
            raise ValueError(
                "❌ Javoblarni ajrata olmadim. Har bir savol raqamidan keyin harf yozing:\n"
                "<code>1 C\n2 A\n3 B</code>"
            )
        return {"correct_answers": answers}

    if field == "file":
        raise ValueError("📎 Fayl (PDF) yoki rasm yuboring.")

    # oddiy matnli maydonlar
    if not text or len(text) > TEXT_LIMIT:
        raise ValueError(f"❌ Matn 1–{TEXT_LIMIT} belgidan iborat bo'lishi kerak.")
    return {field: text}


def missing_required(draft: dict) -> list[str]:
    keys = {"answers": "correct_answers"}
    return [f for f, spec in FIELDS.items() if spec.required and not draft.get(keys.get(f, f))]
