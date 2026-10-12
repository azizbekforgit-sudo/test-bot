"""Bot matnlari. Tilni o'zgartirish uchun asosan shu faylni tahrirlash kifoya."""

# ---------- tugmalar ----------
BTN_NEW_TEST = "➕ Yangi test"
BTN_TESTS = "📋 Testlar"
BTN_SETTINGS = "⚙️ Sozlamalar"
BTN_CANCEL = "🚫 Bekor qilish"
BTN_FROM_SCRATCH = "🆕 Noldan yaratish"
BTN_FROM_OLD = "♻️ Oldingi testdan"
BTN_SKIP = "⏭ O'tkazib yuborish"
BTN_SAVE = "✅ Saqlash"
BTN_EDIT = "✏️ O'zgartirish"
BTN_YES = "✅ Ha"
BTN_NO = "❌ Yo'q"
BTN_BACK = "⬅️ Orqaga"
BTN_SEND_RESULTS = "📤 Natijalarni o'quvchilarga yuborish"
BTN_SHOW_CARD = "👁 Kartani ko'rish"
BTN_POST_CHANNEL = "📢 Kanalga joylash"
BTN_CLONE = "♻️ Nusxa olish"
BTN_DELETE = "🗑 O'chirish"
BTN_CHANGE_CHANNEL = "✏️ Kanalni o'zgartirish"
BTN_OPEN_RESULTS = "📊 Natijalarni ochish"

# ---------- umumiy ----------
WELCOME_ADMIN = "Assalomu alaykum, admin! 👋\nQuyidagi menyudan foydalaning."
WELCOME_STUDENT = (
    "Assalomu alaykum! 👋\n\n"
    "Testga kirish uchun <b>test kodini</b> yuboring.\n"
    "Masalan: <code>mock002</code>"
)
CANCELLED = "Bekor qilindi."

# ---------- sozlamalar ----------
ASK_CHANNEL = (
    "📢 Telegram <b>kanalingizni</b> kiriting (bir marta so'raladi, keyin bot eslab qoladi).\n"
    "U kartaning pastida ko'rsatiladi va «📢 Kanalga joylash» tugmasi shu kanalga yuboradi.\n\n"
    "Masalan: <code>@xodiyevacademy</code>\n\n"
    "Kanal kerak bo'lmasa — <code>-</code> yuboring."
)
CHANNEL_BAD = "❌ Kanalni tushunmadim. Masalan: <code>@kanal_nomi</code> yoki <code>-</code>"
CHANNEL_SAVED = "✅ Saqlandi. Kanal: {channel}"
SETTINGS_VIEW = (
    "⚙️ <b>Sozlamalar</b>\n\n"
    "📢 Kanal: {channel}\n"
    "🤖 Bot: @{bot}\n\n"
    "Kanalga to'g'ridan-to'g'ri joylash uchun botni kanalga <b>admin</b> qilib qo'shing."
)
NO_CHANNEL = "yo'q"

# ---------- test yaratish ----------
NEW_TEST_CHOOSE = "Qanday test yaratamiz?"
BLANK_CARD_INTRO = "📄 Karta namunasi (bo'sh joylarni hozir birma-bir to'ldiramiz) 👇"
CLONE_INTRO = (
    "♻️ «{title}» testidan nusxa olinmoqda.\n"
    "Yangi <b>sana, vaqt va kodni</b> kiriting. Qolgan narsalarni (fayl, javoblar, matnlar) "
    "oxirida «{edit}» tugmasi orqali o'zgartirishingiz mumkin."
)
PICK_OLD_TEST = "Qaysi testdan nusxa olamiz?"
NO_TESTS = "Hali testlar yo'q. «{new}» tugmasi orqali yarating."
CODE_TAKEN = "❌ <code>{code}</code> kodi boshqa testda ishlatilgan. Boshqa kod kiriting."
FILE_BAD = "📎 Fayl (PDF) yoki rasm yuboring."
FILE_SAVED = "✔️ Fayl qabul qilindi."
PREVIEW = (
    "👆 Karta shunday ko'rinadi.\n\n"
    "Savollar soni: <b>{total}</b>\n"
    "To'g'ri javoblar: <code>{answers}</code>\n\n"
    "Hammasi to'g'rimi?"
)
PREVIEW_MISSING = "⚠️ Hali to'ldirilmagan majburiy maydonlar: {fields}"
PREVIEW_PAST = "⚠️ Diqqat: bu sana va vaqt allaqachon o'tib ketgan — o'quvchilar javob yubora olmaydi."
EDITING = "✏️ Tahrirlash"
PREVIEW_HINT = "Pastdagi tugmalardan foydalaning: «✅ Saqlash» yoki «✏️ O'zgartirish»."
EDITED = "✅ O'zgartirildi."
CHOOSE_FIELD = "Nimani o'zgartiramiz?"
TEST_SAVED = "🎉 Test saqlandi! Endi kartani kanalga joylashingiz mumkin."
DRAFT_EXPIRED = "Bu qoralama eskirgan. «{new}» tugmasini qaytadan bosing."

# ---------- testlar ro'yxati ----------
TESTS_TITLE = "📋 <b>Testlar</b>\n⏳ — boshlanmagan, 🟢 — davom etmoqda, 🔴 — yakunlangan"
TEST_BTN = "{icon} {code} · {date} · {count} ta"
STATUS_TEXT = {
    "upcoming": "⏳ Hali boshlanmagan",
    "active": "🟢 Hozir davom etmoqda",
    "finished": "🔴 Yakunlangan",
}
STATUS_ICON = {"upcoming": "⏳", "active": "🟢", "finished": "🔴"}
TEST_VIEW = (
    "🔑 <b>{code}</b>\n"
    "🏆 {title}\n"
    "📅 {date}, {start} – {end}\n"
    "{status}\n\n"
    "Savollar soni: {total}\n"
    "Javob berganlar: {count} ta\n\n"
    "{hint}"
)
TEST_NO_RESULTS = "Hali hech kim javob bermadi."
TEST_RESULTS_HINT = "O'quvchilar natijasi bo'yicha tartiblangan. Ism ustiga bossangiz — batafsil:"
RESULT_BTN = "{medal}{rank}. {mark}{name} — {correct}/{total}"
MEDALS = {1: "🥇 ", 2: "🥈 ", 3: "🥉 "}
TEST_NOT_FOUND = "Test topilmadi."
DELETE_CONFIRM = "⚠️ <b>{code}</b> testi va undagi barcha natijalar o'chirilsinmi?"
DELETED = "🗑 Test o'chirildi."
POSTED = "✅ Karta {channel} kanaliga joylandi."
POST_NO_CHANNEL = "Avval «⚙️ Sozlamalar» bo'limida kanalni kiriting."
POST_FAILED = (
    "❌ Kanalga yuborib bo'lmadi.\n"
    "Botni {channel} kanaliga <b>admin</b> qilib qo'shing (xabar yuborish huquqi bilan) va qaytadan urinib ko'ring.\n\n"
    "Yoki «👁 Kartani ko'rish» bosib, kartani kanalga o'zingiz forward qiling."
)

RESULT_DETAIL = (
    "👤 <b>{name}</b>\n"
    "🔑 Test: {code}\n"
    "Natija: <b>{correct}/{total}</b> ({percent}%)\n"
    "O'rni: {rank}\n"
    "Yuborilgan vaqt: {time}\n\n"
    "{rows}"
)
ROW_OK = "✅ {q}. {given}"
ROW_BAD = "❌ {q}. {given} (to'g'ri: {correct})"
NO_ANSWER = "—"

RESULTS_NOT_FINISHED = "Test hali tugamagan. Natijalarni test tugagandan keyin yuborish mumkin."
RESULTS_NOTHING = "Barcha o'quvchilarga natijalar allaqachon yuborilgan."
RESULTS_SENDING = "📤 Natijalar yuborilmoqda... ({n} ta o'quvchi)"
RESULTS_SENT = "📤 Natijalar yuborildi: {ok} ta o'quvchiga.{failed}"
RESULTS_FAILED = "\n⚠️ {n} ta o'quvchiga yuborib bo'lmadi (botni bloklagan bo'lishi mumkin)."
STUDENT_RESULT = (
    "📊 <b>{code}</b> testi natijasi\n"
    "🏆 {title}\n\n"
    "Siz <b>{total}</b> ta savoldan <b>{correct}</b> tasiga to'g'ri javob berdingiz ({percent}%).\n"
    "{wrong}"
)
STUDENT_RESULT_WRONG = "\n❌ Xato qilingan savollar:\n{rows}"
STUDENT_RESULT_WRONG_ROW = "{q}-savol (sizning javobingiz: {given})"
STUDENT_RESULT_PERFECT = "\n🏆 Barcha javoblar to'g'ri! Barakalla!"

TEST_ENDED_NOTIFY = (
    "⏰ <b>{code}</b> testi yakunlandi!\n"
    "Javob berganlar: {count} ta.\n\n"
    "Natijalar eng ko'p to'g'ri javob berganidan boshlab tartiblangan."
)

# ---------- o'quvchi ----------
CODE_NOT_FOUND = "❌ <code>{code}</code> kodli test topilmadi.\nKodni tekshirib, qaytadan yuboring."
TEST_UPCOMING = (
    "⏳ <b>{code}</b> testi hali boshlanmagan.\n"
    "Boshlanish vaqti: <b>{date}, soat {start}</b>"
)
TEST_FINISHED = (
    "🔴 <b>{code}</b> testi yakunlangan ({date}, soat {end}).\n"
    "Javoblar endi qabul qilinmaydi."
)
ALREADY_SUBMITTED = "Siz <b>{code}</b> testiga allaqachon javob yuborgansiz ✅\nNatija test tugagandan keyin yuboriladi."
ASK_FULL_NAME = "Iltimos, <b>ism va familiyangizni</b> kiriting.\nMasalan: <b>Aliyev Vali</b>"
FULL_NAME_BAD = "Ism-familiya 3–64 belgidan iborat matn bo'lishi kerak. Qaytadan kiriting."
FULL_NAME_SAVED = "✅ Ism saqlandi: <b>{name}</b>"
JOINED_TEST = "✅ Siz <b>{code}</b> testiga kirdingiz!\n🏆 {title}"
TEST_RULES = (
    "📌 <b>Diqqat!</b>\n\n"
    "Testda <b>{total}</b> ta savol bor.\n"
    "Barcha javoblarni <b>bitta matnli xabarda</b> yuboring.\n"
    "⏰ Javoblar <b>soat {end}</b> gacha qabul qilinadi.\n\n"
    "Javob yozish namunasi:\n<code>{example}</code>"
)
ANSWER_EXAMPLE = "1A 2B 3C 4D"
STUDENT_ANSWER_BAD = (
    "❌ Javoblarni tushunmadim. Iltimos, namunadagidek yozing:\n<code>{example}</code>\n\n"
    "Boshqa testga o'tish uchun /start bosing."
)
STUDENT_ANSWER_TEXT_ONLY = "Javoblarni <b>matn</b> ko'rinishida, bitta xabarda yuboring."
STUDENT_CONFIRM = (
    "Siz yuborgan javoblar:\n<code>{answers}</code>\n\n"
    "{warn}"
    "❓ Barcha javoblarni yubordingizmi va namunadagidek to'g'ri yozdingizmi?\n"
    "«Ha» bosilgandan keyin javobni o'zgartirib bo'lmaydi."
)
STUDENT_MISSING = "⚠️ Javobsiz savollar: {numbers}\n\n"
STUDENT_EXTRA = "⚠️ Testda bunday savollar yo'q (hisobga olinmaydi): {numbers}\n\n"
STUDENT_RESEND = "Yaxshi, javoblaringizni qaytadan bitta xabarda yuboring.\nNamuna: <code>{example}</code>"
STUDENT_SUBMITTED = (
    "✅ Javoblaringiz qabul qilindi!\n"
    "Natijangiz test tugagandan keyin shu yerga yuboriladi."
)
TIME_IS_UP = "⏰ Kechirasiz, test vaqti tugadi ({end}). Javoblar qabul qilinmaydi."
TEST_GONE = "Bu test o'chirilgan ekan 😕"
