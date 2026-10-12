"""Bot matnlari. Tilni o'zgartirish uchun faqat shu faylni tahrirlash kifoya."""

# ---------- tugmalar ----------
BTN_CREATE_ROOM = "➕ Xona yaratish"
BTN_MY_ROOMS = "📂 Mavjud xonalar"
BTN_ADD_TEACHER = "👨‍🏫 O'qituvchi qo'shish"
BTN_TEACHERS = "📋 O'qituvchilar ro'yxati"
BTN_REMOVE_TEACHER = "❌ O'qituvchini o'chirish"
BTN_CANCEL = "🚫 Bekor qilish"
BTN_DONE = "✅ Test yuborib bo'lindi"
BTN_YES = "✅ Ha"
BTN_NO = "❌ Yo'q"
BTN_BACK = "⬅️ Orqaga"
BTN_SEND_RESULTS = "📤 Natijalarni o'quvchilarga yuborish"
BTN_LINK = "🔗 Xona havolasi"
BTN_SHOW_TEST = "📄 Testni ko'rish"
BTN_DELETE_ROOM = "🗑 Xonani o'chirish"

# ---------- umumiy ----------
WELCOME_DIRECTOR = "Assalomu alaykum, direktor! 👋\nQuyidagi menyudan foydalaning."
WELCOME_TEACHER = "Assalomu alaykum, ustoz! 👋\nQuyidagi menyudan foydalaning."
WELCOME_STUDENT = (
    "Assalomu alaykum! 👋\n\n"
    "Testga kirish uchun o'qituvchingiz yuborgan havolani bosing."
)
CANCELLED = "Bekor qilindi."
UNKNOWN = "Tushunmadim 🤔 Menyudagi tugmalardan foydalaning yoki /start bosing."
NO_ACCESS = "Bu bo'lim siz uchun emas."

# ---------- direktor ----------
INVITE_CREATED = (
    "✅ O'qituvchi uchun taklif havolasi tayyor:\n\n{link}\n\n"
    "Bu havolani o'qituvchiga yuboring. U havolani bosgach, o'qituvchi roliga ega bo'ladi.\n"
    "⚠️ Havola faqat <b>bir marta</b> ishlaydi."
)
INVITE_INVALID = "❌ Bu taklif havolasi yaroqsiz yoki allaqachon ishlatilgan."
INVITE_ALREADY_TEACHER = "Siz allaqachon o'qituvchisiz 🙂"
INVITE_OK = "🎉 Tabriklaymiz! Sizga <b>o'qituvchi</b> roli berildi."
INVITE_USED_NOTIFY = "✅ {name} taklif havolangiz orqali o'qituvchi bo'ldi."
TEACHERS_EMPTY = "Hozircha o'qituvchilar yo'q."
TEACHERS_TITLE = "📋 <b>O'qituvchilar ro'yxati</b> ({count} ta):\n"
TEACHER_ROW = "{i}. {name}{username} — ID: <code>{id}</code>, xonalar: {rooms}"
REMOVE_TEACHER_CHOOSE = "Qaysi o'qituvchini o'chirmoqchisiz?"
REMOVE_TEACHER_CONFIRM = "{name} o'qituvchilar ro'yxatidan o'chirilsinmi?"
TEACHER_REMOVED = "✅ {name} o'qituvchilar ro'yxatidan o'chirildi."
TEACHER_REMOVED_NOTIFY = "ℹ️ Sizning o'qituvchi rolingiz bekor qilindi."

# ---------- xona yaratish ----------
ASK_ROOM_NAME = "Xona nomini kiriting.\nMasalan: <b>11A Biologiya</b>"
ROOM_NAME_BAD = "Xona nomi 1–64 belgidan iborat matn bo'lishi kerak. Qaytadan kiriting."
ASK_TEST = (
    "📎 Endi testni yuboring.\n\n"
    "Test <b>matn</b>, <b>rasm</b> yoki <b>fayl</b> ko'rinishida bo'lishi mumkin. "
    "Bir nechta xabar/rasm yuborsangiz ham bo'ladi.\n\n"
    "Hammasini yuborib bo'lgach, «{done}» tugmasini bosing."
)
TEST_PART_SAVED = "✔️ Qabul qilindi ({count}). Yana yuborishingiz yoki «{done}» tugmasini bosishingiz mumkin."
TEST_PART_BAD = "Faqat matn, rasm yoki fayl yuboring."
TEST_EMPTY = "Siz hali test yubormadingiz. Avval testni yuboring."
ASK_EXAMPLE = (
    "✍️ O'quvchilar javoblarni qanday ko'rinishda yozishi kerakligiga <b>namuna</b> yozing.\n\n"
    "Masalan: <code>1A 2B 3C</code>\n\n"
    "Bu namuna o'quvchilarga test boshlanishidan oldin ko'rsatiladi."
)
EXAMPLE_BAD = "Namunani tushunmadim. Masalan shunday yozing: <code>1A 2B 3C</code>"
ASK_CORRECT = (
    "✅ Endi to'g'ri javoblarni kiriting.\n\n"
    "⚠️ Iltimos, javoblarni <b>bitta matnli xabarda</b> yuboring "
    "(rasm emas!) — shunda bot ularni avtomatik tekshira oladi.\n\n"
    "Masalan:\n<code>1 C\n2 A\n3 B</code>"
)
CORRECT_BAD = (
    "❌ Javoblarni ajrata olmadim. Har bir savol raqamidan keyin harf yozing:\n"
    "<code>1 C\n2 A\n3 B</code>"
)
CORRECT_CONFIRM = (
    "Tekshiring, to'g'ri javoblar shularmi?\n\n"
    "Savollar soni: <b>{total}</b>\n{answers}"
)
ROOM_CREATED = (
    "🎉 <b>{name}</b> xonasi yaratildi!\n\n"
    "Savollar soni: {total}\n\n"
    "Quyidagi havolani o'quvchilarga yuboring 👇\n{link}"
)

# ---------- xonalar ro'yxati ----------
ROOMS_EMPTY = "Sizda hali xonalar yo'q. «{create}» tugmasi orqali yarating."
ROOMS_TITLE = "📂 <b>Sizning xonalaringiz</b>\nKerakli xonani tanlang:"
ROOM_BTN = "{name} ({count} ta javob)"
ROOM_VIEW = (
    "🏫 <b>{name}</b>\n"
    "Savollar soni: {total}\n"
    "Javob berganlar: {count} ta\n"
    "Havola: {link}\n\n"
    "{body}"
)
ROOM_NO_SUBS = "Hali hech kim javob bermadi."
ROOM_SUBS_HINT = "O'quvchi ustiga bossangiz, uning javoblarini ko'rasiz:"
STUDENT_BTN = "{mark}{name} — {correct}/{total}"
ROOM_LINK = "🔗 <b>{name}</b> xonasi havolasi:\n{link}"
ROOM_DELETE_CONFIRM = "⚠️ <b>{name}</b> xonasi va undagi barcha javoblar o'chirilsinmi?"
TEST_ANSWERS = "🔑 To'g'ri javoblar ({total} ta):\n<code>{answers}</code>"
ROOM_DELETED = "🗑 Xona o'chirildi."
ROOM_NOT_FOUND = "Xona topilmadi."

SUB_DETAIL = (
    "👤 <b>{name}</b>\n"
    "🏫 Xona: {room}\n"
    "Natija: <b>{correct}/{total}</b>\n"
    "Yuborilgan vaqt: {time}\n\n"
    "{rows}"
)
SUB_ROW_OK = "✅ {q}. {given}"
SUB_ROW_BAD = "❌ {q}. {given} (to'g'ri: {correct})"
NO_ANSWER = "—"

RESULTS_NOTHING = "Barcha o'quvchilarga natijalar allaqachon yuborilgan."
RESULTS_SENT = "📤 Natijalar yuborildi: {ok} ta o'quvchiga.{failed}"
RESULTS_FAILED = "\n⚠️ {n} ta o'quvchiga yuborib bo'lmadi (botni bloklagan bo'lishi mumkin)."
STUDENT_RESULT = (
    "📊 <b>{room}</b> testi natijasi\n\n"
    "Siz <b>{total}</b> ta savoldan <b>{correct}</b> tasiga to'g'ri javob berdingiz.\n"
    "{wrong}"
)
STUDENT_RESULT_WRONG = "\n❌ Xato qilingan savollar:\n{rows}"
STUDENT_RESULT_WRONG_ROW = "{q}-savol (sizning javobingiz: {given})"
STUDENT_RESULT_PERFECT = "\n🏆 Barcha javoblar to'g'ri! Barakalla!"

NEW_SUBMISSION_NOTIFY = "📥 <b>{room}</b>: {name} javob yubordi — {correct}/{total}"

# ---------- o'quvchi ----------
ROOM_LINK_INVALID = "❌ Bunday xona topilmadi. Havola noto'g'ri yoki xona o'chirilgan."
ASK_FULL_NAME = "Iltimos, ism va familiyangizni kiriting.\nMasalan: <b>Aliyev Vali</b>"
FULL_NAME_BAD = "Ism-familiya 3–64 belgidan iborat matn bo'lishi kerak. Qaytadan kiriting."
JOINED_ROOM = "✅ Siz <b>{name}</b> xonasiga kirdingiz!"
ALREADY_SUBMITTED = "Siz <b>{name}</b> xonasidagi testga allaqachon javob yuborgansiz ✅\nNatijani o'qituvchingiz yuboradi."
TEST_RULES = (
    "📌 <b>Diqqat!</b>\n\n"
    "Testda <b>{total}</b> ta savol bor.\n"
    "Barcha javoblarni <b>bitta matnli xabarda</b> yuboring.\n\n"
    "Javob yozish namunasi:\n<code>{example}</code>\n\n"
    "Test quyida 👇"
)
TEST_END = "✍️ Javoblaringizni bitta xabarda yuboring."
STUDENT_ANSWER_BAD = (
    "❌ Javoblarni tushunmadim. Iltimos, namunadagidek yozing:\n<code>{example}</code>"
)
STUDENT_ANSWER_TEXT_ONLY = "Javoblarni <b>matn</b> ko'rinishida, bitta xabarda yuboring."
STUDENT_CONFIRM = (
    "Siz yuborgan javoblar:\n<code>{answers}</code>\n\n"
    "{missing}"
    "❓ Barcha javoblarni yubordingizmi va namunadagidek to'g'ri yozdingizmi?\n"
    "«Ha» bosilgandan keyin javobni o'zgartirib bo'lmaydi."
)
STUDENT_MISSING = "⚠️ Javobsiz savollar: {numbers}\n\n"
STUDENT_EXTRA = "⚠️ Testda bunday savollar yo'q (hisobga olinmaydi): {numbers}\n\n"
STUDENT_RESEND = "Yaxshi, javoblaringizni qaytadan bitta xabarda yuboring.\nNamuna: <code>{example}</code>"
STUDENT_SUBMITTED = (
    "✅ Javoblaringiz o'qituvchiga yuborildi!\n"
    "Natijani o'qituvchingiz tekshirib yuboradi."
)
ROOM_GONE = "Xona o'chirilgan ekan 😕"
