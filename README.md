# 📝 Test qabul qiluvchi Telegram bot

Bu bot orqali admin **test e'lon qiladi** (kanal uchun tayyor karta bilan), o'quvchilar
**test kodi** orqali kirib javob yuboradi, bot javoblarni **avtomatik tekshiradi**,
natijalarni **eng yaxshidan boshlab tartiblaydi** va admin bir tugma bilan har bir
o'quvchiga uning natijasini yuboradi.

Botda faqat **2 ta rol** bor:

| Rol | Kim | Nima qila oladi |
|-----|-----|-----------------|
| 👑 **Admin** | `.env` faylida ID raqami yozilgan odam | Test yaratadi, kartani kanalga joylaydi, natijalarni ko'radi va o'quvchilarga yuboradi |
| 🎓 **O'quvchi** | Qolgan hamma | Test kodini yuborib testga kiradi va javob yuboradi |

---

## 1. Botni ishga tushirish

### 1.1. Bot yaratish
1. Telegramda [@BotFather](https://t.me/BotFather) ga kiring.
2. `/newbot` buyrug'ini yuboring, botga nom va username bering.
3. BotFather bergan **tokenni** saqlab qo'ying (masalan `123456789:AAH...`).

### 1.2. Admin ID sini bilish
[@userinfobot](https://t.me/userinfobot) ga `/start` yozing — u sizning **ID** raqamingizni beradi.

### 1.3. Sozlash
`.env.example` faylidan nusxa olib, `.env` deb nomlang va to'ldiring:

```env
BOT_TOKEN=123456789:AAH...........
ADMIN_IDS=123456789
TIMEZONE=Asia/Tashkent
DB_PATH=bot.db
```

* `BOT_TOKEN` — BotFather bergan token.
* `ADMIN_IDS` — admin(lar) ID si. Bir nechta bo'lsa vergul bilan: `111,222`.
* `TIMEZONE` — vaqt mintaqasi. Test boshlanish/tugash vaqtlari shu bo'yicha hisoblanadi
  (O'zbekiston uchun `Asia/Tashkent`, o'zgartirish shart emas).
* `DB_PATH` — ma'lumotlar saqlanadigan fayl.

### 1.4. O'rnatish va ishga tushirish
Kompyuterda **Python 3.10 yoki undan yangi** versiya bo'lishi kerak.

```bash
python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python -m bot.main
```

Terminalda `Bot ishga tushdi: @sizning_bot` chiqsa — bot ishlayapti ✅.
Bot doim ishlab turishi uchun uni serverda (VPS) yoki hostingda (Render, Railway va h.k.) ishga tushiring.

> Agar avval botning eski versiyasi (xonalar bilan) ishlatilgan bo'lsa, eski `bot.db` faylini
> o'chirib yuborish tavsiya etiladi.

---

## 2. Admin 👑

Admin `/start` bosganda 3 ta tugma chiqadi: **➕ Yangi test**, **📋 Testlar**, **⚙️ Sozlamalar**.

### 2.1. Bir marta kiritiladigan sozlama — kanal

Birinchi marta **➕ Yangi test** bosilganda bot kanalingizni so'raydi (masalan `@xodiyevacademy`).
Bot uni **eslab qoladi** va keyin boshqa so'ramaydi. Kanal kartaning pastida chiqadi:

* «Testni maksimal darajada tarqatib yuboring» — kanalni ulashish havolasi;
* `✈️ @kanal` — kanal nomi.

Bot havolasi (`Javob yuborish uchun : @bot`) esa **avtomatik** qo'yiladi — uni kiritish shart emas.

Kanalni keyin **⚙️ Sozlamalar → ✏️ Kanalni o'zgartirish** orqali almashtirish mumkin.
Kanal kerak bo'lmasa `-` yuboriladi.

### 2.2. Yangi test yaratish

**➕ Yangi test** bosilganda ikki variant chiqadi:

#### 🆕 Noldan yaratish
Bot avval **bo'sh karta namunasini** ko'rsatadi (hamma ma'lumotlar o'rnida `________`),
keyin maydonlarni birma-bir so'raydi:

| № | Maydon | Misol | Majburiymi |
|---|--------|-------|------------|
| 1 | 🏆 Sarlavha | `2-MILLIY SERTIFIKAT DIAGNOSTIK TEST TOPSHIRIQLARI KITOBI (RASH MODELIDA)` | ✅ ha |
| 2 | ☑️ Fan / til | `Til: Qoraqalpoq tili` | yo'q |
| 3 | #️⃣ Heshteglar | `#MOCKEXAM #RASH` | yo'q |
| 4 | 📌 Kichik sarlavha | `Bilimni baholash agentligi formatida 🔴` | yo'q |
| 5 | 💬 Yakuniy matn | `Hammaga omad🚀 Test yakunlangach natijalar ... e'lon qilinadi` | yo'q |
| 6 | 📅 Sana | `12.07.2026` | ✅ ha |
| 7 | 🕙 Boshlanish vaqti | `10:00` | ✅ ha |
| 8 | 🕧 Tugash vaqti | `12:30` | ✅ ha |
| 9 | 🔑 Test kodi | `mock002` | ✅ ha |
| 10 | 📎 Test fayli | PDF yoki rasm | yo'q |
| 11 | ✅ To'g'ri javoblar | `1A 2B 3C ...` | ✅ ha |

Majburiy bo'lmagan maydonlarni **⏭ O'tkazib yuborish** tugmasi bilan tashlab ketish mumkin —
ular kartada ko'rinmaydi.

⚠️ To'g'ri javoblarni bot **bitta matnli xabarda** yuborishni so'raydi (rasm emas!),
chunki o'quvchilarni shu matn bo'yicha avtomatik tekshiradi. Masalan:
```
1 C
2 A
3 B
```

Hammasi kiritilgach, bot **tayyor kartani** (fayl bilan birga) ko'rsatadi, savollar sonini
va to'g'ri javoblarni yozadi va so'raydi:
* **✅ Saqlash** — test saqlanadi;
* **✏️ O'zgartirish** — istalgan maydonni tanlab, qayta kiritasiz.

#### ♻️ Oldingi testdan
Avval yaratilgan testlar ro'yxati chiqadi. Birini tanlasangiz, bot undan **nusxa oladi**
(sarlavha, matnlar, fayl, javoblar — hammasi saqlanadi) va faqat quyidagilarni qaytadan so'raydi:

1. 📅 Sana
2. 🕙 Boshlanish vaqti
3. 🕧 Tugash vaqti
4. 🔑 Yangi test kodi

Keyin karta ko'rsatiladi va kerak bo'lsa **✏️ O'zgartirish** orqali boshqa narsalarni
(masalan, yangi PDF yoki yangi javoblar) almashtirish mumkin.

### 2.3. Test kodi — eng muhim qism 🔑

* O'quvchi testga **faqat kod orqali** kiradi.
* Har bir testning kodi **takrorlanmas** bo'lishi kerak — bot bir xil kodni ikki marta bermaydi.
* Kod katta-kichik harfga sezgir emas: `mock002`, `MOCK002`, `Mock002` — bir xil.
* Kod faqat lotin harflari, raqamlar, `-` va `_` dan iborat (2–32 belgi).
* Kartadagi `@bot` havolasi ichida ham kod bor (`t.me/bot?start=mock002`) —
  o'quvchi uni bossa, kod yozmasdan to'g'ridan-to'g'ri testga kiradi.

### 2.4. Vaqt: boshlanish va tugash ⏰

* **Boshlanish vaqtigacha** o'quvchi kodni yuborsa: *«Test hali boshlanmagan. Boshlanish vaqti: …»*.
* **Boshlanish va tugash orasida** — test ochiq, javoblar qabul qilinadi.
* **Tugash vaqtidan keyin** bot javob **qabul qilmaydi**: *«Test yakunlangan»*.
  Hatto o'quvchi javobni yozib, «Ha» tugmasini kech bossa ham — qabul qilinmaydi.
* Test tugashi bilan bot adminga avtomatik xabar yuboradi:
  *«⏰ mock002 testi yakunlandi! Javob berganlar: 120 ta»* va **📊 Natijalarni ochish** tugmasi.

### 2.5. 📋 Testlar — natijalar

Barcha testlar ro'yxati (eng yangisi tepada). Har birining yonida holati:
⏳ — hali boshlanmagan, 🟢 — davom etmoqda, 🔴 — yakunlangan; kodi, sanasi va nechta odam javob bergani.

Test tanlanganda:

* **O'quvchilar ro'yxati — avtomatik tartiblangan**: eng ko'p to'g'ri javob bergan tepada,
  eng kami pastda. Har bir ism yonida natija:
  ```
  🥇 1. Valiyev Vali — 35/35
  🥈 2. Aliyev Ali — 33/35
  🥉 3. Karimova Malika — 30/35
  4. ...
  ```
  (Natijasi teng bo'lsa — kim oldin yuborgan bo'lsa, o'sha yuqorida.)
  Natijasi yuborilgan o'quvchilar yonida 📨 belgisi turadi.
* **O'quvchi ismiga bosilsa** — batafsil: foiz, o'rni va har bir savol:
  ```
  ✅ 1. A
  ❌ 2. B (to'g'ri: C)
  ✅ 3. D
  ```
* **📤 Natijalarni o'quvchilarga yuborish** (ro'yxat oxirida) — har bir o'quvchiga shaxsan
  **o'zining natijasi** boradi: nechta to'g'ri, foizi va qaysi savollarda xato qilgani.
  Bu tugma **test tugagandan keyin** ishlaydi. Qayta bosilsa — faqat hali natija olmaganlarga yuboradi.
* **👁 Kartani ko'rish** — kartani o'zingizga yuboradi (uni kanalga o'zingiz forward qilishingiz mumkin).
* **📢 Kanalga joylash** — kartani to'g'ridan-to'g'ri kanalga joylaydi.
  Buning uchun botni kanalga **admin** qilib qo'shish kerak.
* **✏️ O'zgartirish** — saqlangan testning istalgan maydonini o'zgartirish
  (sana, vaqt, kod, fayl, javoblar, matnlar). To'g'ri javoblar o'zgartirilsa —
  barcha o'quvchilarning natijasi **avtomatik qayta hisoblanadi**.
* **♻️ Nusxa olish** — shu test asosida yangi test yaratish (2.2-bo'limga qarang).
* **🗑 O'chirish** — test va uning barcha natijalarini o'chirish (tasdiqlash so'raladi).

---

## 3. O'quvchi 🎓

1. O'quvchi kanalda kartani ko'radi va botga kiradi (yoki kartadagi `@bot` havolasini bosadi).
2. Bot: *«Testga kirish uchun test kodini yuboring»*. O'quvchi kodni yozadi: `mock002`.
3. Bot kodni tekshiradi:
   * kod noto'g'ri — *«Bunday kodli test topilmadi»*;
   * test hali boshlanmagan yoki tugagan — shu haqida aytadi;
   * o'quvchi bu testga allaqachon javob bergan — *«Siz allaqachon javob yuborgansiz»*.
4. Hammasi joyida bo'lsa: *«✅ Siz mock002 testiga kirdingiz!»*.
5. Botdan birinchi marta foydalanayotgan o'quvchidan **ism-familiya** so'raladi
   (adminning ro'yxatida aynan shu ism chiqadi). Keyingi testlarda qayta so'ralmaydi.
   O'zgartirish uchun — `/ism` buyrug'i.
6. Bot test faylini (PDF) yuboradi va qoidani aytadi: savollar soni, javoblarni
   **bitta xabarda** yuborish kerakligi, **qaysi soatgacha** qabul qilinishi va namuna: `1A 2B 3C 4D`.
7. O'quvchi barcha javoblarni bitta xabarda yozadi.
8. Tushunmovchilik bo'lmasligi uchun bot o'quvchi yozgan javoblarni qaytarib ko'rsatadi va so'raydi:
   *«Barcha javoblarni yubordingizmi va namunadagidek to'g'ri yozdingizmi?»* — **✅ Ha / ❌ Yo'q**.
   Javobsiz qolgan savollar bo'lsa, bot buni ham ogohlantiradi.
9. «Ha» bosilgach: *«✅ Javoblaringiz qabul qilindi! Natijangiz test tugagandan keyin yuboriladi»*.
10. Admin «Natijalarni yuborish» bosgach, o'quvchiga natija keladi:
    ```
    📊 mock002 testi natijasi
    Siz 35 ta savoldan 30 tasiga to'g'ri javob berdingiz (85.7%).
    ❌ Xato qilingan savollar:
    4-savol (sizning javobingiz: B)
    ...
    ```
    (To'g'ri javoblar o'quvchilarga ko'rsatilmaydi.)

Bitta o'quvchi bitta testga **faqat bir marta** javob yubora oladi.

---

## 4. Javoblar qanday tekshiriladi?

Bot matndan **«raqam + harf»** juftliklarini qidiradi. Quyidagilarning hammasi tushuniladi:

```
1A 2B 3C
1 A, 2 B, 3 C
1-A 2-B 3-C
1)A 2.B 3:C
1A2B3C
```
yoki har bir javob alohida qatorda.

* Katta-kichik harf farq qilmaydi (`1a` = `1A`).
* Kirill harflari lotinchaga aylantiriladi: **А→A, Б→B, С→C, Д→D, Е→E**
  (o'quvchi `1А 2Б` deb kirillda yozsa ham to'g'ri tekshiriladi).
* Bitta savol ikki marta yozilsa — oxirgisi hisobga olinadi.
* Javob yozilmagan savol — xato hisoblanadi.
* Natija = to'g'ri javoblar soni / jami savollar soni va foizi.

---

## 5. Loyiha tuzilishi (dasturchilar uchun)

```
test-bot/
├── .env.example          — sozlamalar namunasi
├── requirements.txt      — kutubxonalar (aiogram 3, aiosqlite, python-dotenv, tzdata)
└── bot/
    ├── main.py           — botni ishga tushiruvchi fayl
    ├── config.py         — .env dan sozlamalarni o'qish
    ├── db.py             — SQLite ma'lumotlar bazasi
    ├── answers.py        — javoblarni matndan ajratish va tekshirish
    ├── form.py           — test maydonlari: savollari va tekshiruvi
    ├── card.py           — kanal kartasini yasash va yuborish
    ├── timeutils.py      — sana/vaqt, test holati (boshlanmagan/ochiq/tugagan)
    ├── scheduler.py      — test tugaganda adminga xabar beruvchi fon vazifasi
    ├── texts.py          — botning barcha matnlari
    ├── keyboards.py      — tugmalar
    ├── filters.py        — adminni aniqlash
    ├── utils.py          — yordamchi funksiyalar
    └── handlers/
        ├── common.py     — /start, /cancel, /ism
        ├── admin.py      — admin paneli: test yaratish, tahrirlash, natijalar
        └── student.py    — o'quvchi: kod, ism, javob yuborish
```

### Ma'lumotlar bazasi (`bot.db`)

| Jadval | Nima saqlanadi |
|--------|----------------|
| `users` | Botdan foydalanganlar va o'quvchilar kiritgan ism-familiya |
| `settings` | Bir marta kiritiladigan sozlamalar (kanal) |
| `tests` | Testlar: kod, karta matnlari, sana, boshlanish/tugash vaqti, fayl, to'g'ri javoblar |
| `test_results` | O'quvchilar javoblari, to'g'ri javoblar soni, natija yuborilganmi |

### Muhim eslatmalar
* Bot qayta ishga tushirilsa, **jarayon o'rtasidagi** holatlar (masalan, test yaratayotgan admin
  yoki javob yozayotgan o'quvchi) unutiladi — `/start` bosib qaytadan boshlash kerak.
  Saqlangan testlar, sozlamalar va yuborilgan javoblar bazada qoladi.
* `bot.db` faylining zaxira nusxasini vaqti-vaqti bilan oling — barcha ma'lumotlar shu faylda.
* Botning matnlarini o'zgartirish uchun `bot/texts.py`, karta ko'rinishini o'zgartirish uchun
  `bot/card.py` faylini tahrirlang.
* Bot hozircha faqat **harfli javoblarni** (A, B, C, D …) tekshiradi. Natija «to'g'ri/jami»
  ko'rinishida hisoblanadi (RASH ball emas).
