# 📝 Test qabul qiluvchi Telegram bot

Bu bot o'qituvchilarga test o'tkazish, o'quvchilarning javoblarini avtomatik tekshirish
va natijalarni o'quvchilarga yuborish uchun mo'ljallangan.

Botda **3 ta rol** bor:

| Rol | Kim | Nima qila oladi |
|-----|-----|-----------------|
| 👔 **Direktor** (admin) | `.env` faylida ID raqami yozilgan odam | O'qituvchi qo'shadi, ro'yxatini ko'radi, o'chiradi. Xohlasa, o'zi ham xona yarata oladi |
| 👨‍🏫 **O'qituvchi** | Direktor bergan havolani bosgan odam | Xona (test) yaratadi, natijalarni ko'radi, natijalarni o'quvchilarga yuboradi |
| 🎓 **O'quvchi** | Qolgan hamma | Faqat o'qituvchi bergan havola orqali testga kiradi va javob yuboradi |

---

## 1. Botni ishga tushirish

### 1.1. Bot yaratish
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
2. `/newbot` buyrug'ini yuboring, botga nom va username bering.
3. BotFather bergan **tokenni** saqlab qo'ying (masalan `123456789:AAH...`).

### 1.2. Direktor ID sini bilish
[@userinfobot](https://t.me/userinfobot) ga `/start` yozing — u sizning **ID** raqamingizni beradi
(masalan `123456789`).

### 1.3. Sozlash
Loyiha papkasida `.env.example` faylidan nusxa olib, `.env` deb nomlang va to'ldiring:

```env
BOT_TOKEN=123456789:AAH...........
DIRECTOR_IDS=123456789
DB_PATH=bot.db
```

* `BOT_TOKEN` — BotFather bergan token.
* `DIRECTOR_IDS` — direktor(lar) ID si. Bir nechta bo'lsa vergul bilan: `111,222`.
* `DB_PATH` — ma'lumotlar saqlanadigan fayl nomi (o'zgartirmasangiz ham bo'ladi).

### 1.4. O'rnatish va ishga tushirish
Kompyuterda **Python 3.10 yoki undan yangi** versiya bo'lishi kerak.

```bash
python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

Terminalda `Bot ishga tushdi: @sizning_bot` yozuvi chiqsa — bot ishlayapti ✅.
Bot doim ishlab turishi uchun uni server (VPS) da yoki hosting (Render, Railway va h.k.) da ishga tushiring.

---

## 2. Direktor (admin panel) 👔

Direktor `/start` bosganda unga quyidagi menyu chiqadi:

* **👨‍🏫 O'qituvchi qo'shish** — bot maxsus havola beradi, masalan:
  `https://t.me/sizning_bot?start=teacher_xxxxxx`.
  Bu havolani o'qituvchiga yuborasiz. O'qituvchi havolani bosishi bilan unga
  **o'qituvchi roli** beriladi va direktorga xabar keladi.
  ⚠️ Har bir havola **faqat bir marta** ishlaydi — har bir o'qituvchi uchun yangi havola oling.
* **📋 O'qituvchilar ro'yxati** — rol berilgan barcha o'qituvchilar: ismi, username, ID si va nechta xonasi borligi.
* **❌ O'qituvchini o'chirish** — ro'yxatdan o'qituvchini tanlaysiz, «Ha» bosasiz va
  uning o'qituvchi roli olib tashlanadi (o'qituvchiga ham xabar boradi).
  Uning xonalari va natijalari o'chib ketmaydi — qayta qo'shilsa, hammasi joyida bo'ladi.

Direktorda o'qituvchi tugmalari ham bor (**➕ Xona yaratish**, **📂 Mavjud xonalar**),
shuning uchun botni o'zi ham sinab ko'rishi mumkin.

---

## 3. O'qituvchi 👨‍🏫

O'qituvchi menyusida 2 ta tugma bor: **➕ Xona yaratish** va **📂 Mavjud xonalar**.

### 3.1. Xona (test) yaratish — qadamma-qadam

1. **➕ Xona yaratish** bosiladi.
2. Bot: *«Xona nomini kiriting»* → o'qituvchi yozadi, masalan `11A Biologiya`.
3. Bot: *«Endi testni yuboring»* → o'qituvchi testni **matn**, **rasm** yoki **fayl** ko'rinishida yuboradi.
   Bir nechta xabar yoki bir nechta rasm (albom) yuborish mumkin.
   Hammasini yuborib bo'lgach **«✅ Test yuborib bo'lindi»** tugmasi bosiladi.
4. Bot: *«O'quvchilar javobni qanday yozishi kerakligiga namuna yozing»* →
   o'qituvchi namuna yozadi, masalan `1A 2B 3C`.
   Bu namuna o'quvchilarga test oldidan ko'rsatiladi, shunda ular qanday yozishni biladi.
5. Bot ogohlantiradi: *«To'g'ri javoblarni **bitta matnli xabarda** yuboring (rasm emas!)»* —
   chunki bot javoblarni matndan o'qib, avtomatik tekshiradi. O'qituvchi yozadi:
   ```
   1 C
   2 A
   3 B
   ```
6. Bot to'g'ri javoblarni qaytarib ko'rsatadi va so'raydi: *«To'g'ri javoblar shularmi?»*
   * **✅ Ha** — xona yaratiladi;
   * **❌ Yo'q** — javoblarni qaytadan kiritasiz.
7. Bot **xona havolasini** beradi, masalan:
   `https://t.me/sizning_bot?start=room_AbC123xyz`
   Shu havolani o'quvchilarga (masalan, sinf guruhiga) yuborasiz.

Istalgan bosqichda **🚫 Bekor qilish** tugmasi yoki `/cancel` buyrug'i bilan jarayonni to'xtatish mumkin.

### 3.2. Mavjud xonalar

**📂 Mavjud xonalar** bosilganda o'qituvchi yaratgan barcha xonalar ro'yxati chiqadi
(har birining yonida nechta o'quvchi javob bergani yoziladi).
Xona tanlanganda:

* **O'quvchilar ro'yxati** — testni yechgan har bir o'quvchi va yonida natijasi, masalan:
  `Aliyev Ali — 8/10` (10 ta savoldan 8 tasi to'g'ri).
  O'quvchilar eng ko'p to'g'ri javob berganidan boshlab tartiblangan.
  Natijasi yuborilgan o'quvchilar yonida 📨 belgisi turadi.
* **O'quvchi ustiga bosilsa** — har bir savol bo'yicha batafsil:
  ```
  ✅ 1. C
  ❌ 2. B (to'g'ri: A)
  ✅ 3. B
  ```
* **📤 Natijalarni o'quvchilarga yuborish** — har bir o'quvchiga shaxsan natija boradi:
  nechta to'g'ri javob bergani va qaysi savollarda xato qilgani.
  Natija faqat hali yuborilmagan o'quvchilarga yuboriladi — keyinroq yangi o'quvchilar
  javob bersa, tugmani yana bossangiz, faqat ularga boradi.
* **🔗 Xona havolasi** — havolani qayta olish.
* **📄 Testni ko'rish** — yuklangan test va to'g'ri javoblarni ko'rish.
* **🗑 Xonani o'chirish** — xona va undagi barcha javoblarni o'chirish (tasdiqlash so'raladi).

Har safar o'quvchi javob yuborganda o'qituvchiga darhol xabar keladi:
`📥 11A Biologiya: Aliyev Ali javob yubordi — 8/10`.

> Bir o'qituvchi faqat **o'zi yaratgan** xonalarni ko'radi.

---

## 4. O'quvchi 🎓

1. O'quvchi o'qituvchi bergan havolani bosadi → Telegram botni ochadi → **Start** bosiladi.
2. Bot: *«✅ Siz **11A Biologiya** xonasiga kirdingiz!»*
3. Agar o'quvchi botdan birinchi marta foydalanayotgan bo'lsa, bot **ism va familiyasini** so'raydi
   (o'qituvchi ro'yxatida aynan shu ism ko'rinadi). Keyingi testlarda qayta so'ralmaydi.
4. Bot qoidani aytadi: savollar soni, **javoblarni bitta xabarda yuborish kerakligi** va namuna
   (masalan `1A 2B 3C`). Shundan keyin darhol **testni yuboradi**.
5. O'quvchi barcha javoblarni bitta xabarda yozadi:
   ```
   1A
   2B
   3C
   ```
6. Tushunmovchilik bo'lmasligi uchun bot o'quvchi yozgan javoblarni qaytarib ko'rsatadi va so'raydi:
   *«Barcha javoblarni yubordingizmi va namunadagidek to'g'ri yozdingizmi?»*
   Agar ba'zi savollarga javob yozilmagan bo'lsa, bot buni ham ogohlantiradi (*«Javobsiz savollar: 3»*).
   * **✅ Ha** — javoblar o'qituvchiga yuboriladi. Endi javobni o'zgartirib bo'lmaydi.
   * **❌ Yo'q** — o'quvchi javoblarni qaytadan yozadi.
7. O'qituvchi **«Natijalarni yuborish»** bosgandan keyin o'quvchiga natija keladi:
   ```
   📊 11A Biologiya testi natijasi
   Siz 10 ta savoldan 8 tasiga to'g'ri javob berdingiz.
   ❌ Xato qilingan savollar:
   2-savol (sizning javobingiz: B)
   7-savol (sizning javobingiz: D)
   ```
   (To'g'ri javoblar o'quvchilarga ko'rsatilmaydi — boshqalarga tarqalib ketmasligi uchun.)

Bitta o'quvchi bitta xonaga **faqat bir marta** javob yubora oladi.

---

## 5. Javoblar qanday tekshiriladi?

Bot matndan **«raqam + harf»** juftliklarini qidiradi. Quyidagi yozuvlarning hammasi tushuniladi:

```
1A 2B 3C
1 A, 2 B, 3 C
1-A 2-B 3-C
1)A 2.B 3:C
1A2B3C
```

* Katta-kichik harf farq qilmaydi (`1a` = `1A`).
* Kirill harflari lotinchaga aylantiriladi: **А→A, Б→B, С→C, Д→D, Е→E**.
  Ya'ni o'quvchi `1А 2Б 3С` (kirillda) yozsa ham, o'qituvchi `1 A 2 B 3 C` (lotinda) yozgan
  javoblar bilan to'g'ri solishtiriladi.
* Agar bitta savol ikki marta yozilsa, oxirgisi hisobga olinadi.
* Javob yozilmagan savol — xato hisoblanadi.

---

## 6. Loyiha tuzilishi (dasturchilar uchun)

```
test-bot/
├── .env.example          — sozlamalar namunasi
├── requirements.txt      — kerakli kutubxonalar (aiogram 3, aiosqlite, python-dotenv)
└── bot/
    ├── main.py           — botni ishga tushiruvchi fayl
    ├── config.py         — .env dan sozlamalarni o'qish
    ├── db.py             — SQLite ma'lumotlar bazasi bilan ishlash
    ├── answers.py        — javoblarni matndan ajratish va tekshirish
    ├── texts.py          — botning BARCHA matnlari (tilni shu yerda o'zgartirasiz)
    ├── keyboards.py      — tugmalar
    ├── filters.py        — rollarni tekshirish (direktor / o'qituvchi)
    ├── utils.py          — yordamchi funksiyalar (havolalar, test yuborish)
    └── handlers/
        ├── common.py     — /start, havolalarni qabul qilish, bekor qilish
        ├── director.py   — direktor paneli
        ├── teacher.py    — xona yaratish va natijalar
        └── student.py    — o'quvchining testga kirishi va javob yuborishi
```

### Ma'lumotlar bazasi (`bot.db`)

| Jadval | Nima saqlanadi |
|--------|----------------|
| `users` | Botdan foydalangan hamma: Telegram ismi, username, o'quvchi kiritgan ism-familiya |
| `teachers` | O'qituvchi roli berilganlar |
| `teacher_invites` | Direktor yaratgan taklif havolalari (ishlatilganmi yoki yo'qmi) |
| `rooms` | Xonalar: nomi, egasi (o'qituvchi), javob namunasi, to'g'ri javoblar |
| `room_materials` | Test materiallari (matn, rasm, fayl) |
| `submissions` | O'quvchilar javoblari, to'g'ri javoblar soni, natija yuborilganmi |

### Havolalar qanday ishlaydi?
Telegram'ning *deep link* imkoniyatidan foydalaniladi: `https://t.me/BOT?start=XXX`.
Havola bosilganda bot `/start XXX` buyrug'ini oladi:
* `teacher_...` bilan boshlansa — o'qituvchi taklifnomasi;
* `room_...` bilan boshlansa — xonaga kirish.

Havoladagi kodlar tasodifiy va uzun, shuning uchun ularni topib (taxmin qilib) bo'lmaydi.

### Muhim eslatmalar
* Bot qayta ishga tushirilsa, **jarayon o'rtasidagi** holatlar (masalan, xona yaratayotgan
  o'qituvchi yoki javob yozayotgan o'quvchi) unutiladi — `/start` bosib, qaytadan boshlash kerak.
  Yaratilgan xonalar, o'qituvchilar va yuborilgan javoblar esa bazada saqlanib qoladi.
* `bot.db` faylini vaqti-vaqti bilan zaxira nusxasini oling — barcha ma'lumotlar shu faylda.
* Botning tilini o'zgartirish uchun faqat `bot/texts.py` faylini tahrirlash kifoya.
