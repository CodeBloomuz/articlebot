# 📝 Maqola Yozdirish Bot — O'rnatish Qo'llanmasi

## Fayl tuzilmasi
```
article_bot/
├── bot.py              # Asosiy fayl
├── config.py           # Token va sozlamalar
├── states.py           # FSM holatlari
├── keyboards.py        # Barcha tugmalar
├── database.py         # Ma'lumotlar bazasi (JSON)
├── requirements.txt    # Kutubxonalar
├── Procfile            # Railway uchun
└── handlers/
    ├── __init__.py
    ├── user_handler.py  # Foydalanuvchi handlerlari
    └── admin_handler.py # Admin handlerlari
```

## 1. Sozlash

### config.py faylini tahrirlang:
```python
BOT_TOKEN = "7xxxxxxxxx:AAF..."      # @BotFather dan oling
ADMIN_GROUP_ID = -100123456789        # Admin guruh IDsi
CARD_NUMBER = "8600 xxxx xxxx xxxx"  # To'lov kartangiz
CARD_OWNER = "Ism Familiya"          # Karta egasi
```

### Admin guruh IDsini olish:
1. Botni guruhga qo'shing
2. Guruhga /start yozing
3. https://api.telegram.org/botTOKEN/getUpdates sahifasini oching
4. "chat":{"id": ...} qiymatini oling (manfiy son)

## 2. Lokal ishga tushirish
```bash
pip install -r requirements.txt
python bot.py
```

## 3. Railway ga deploy qilish
1. GitHub ga push qiling
2. railway.app ga kiring
3. "New Project" → "Deploy from GitHub repo"
4. Environment variables:
   - `BOT_TOKEN` = tokeningiz
   - `ADMIN_GROUP_ID` = guruh IDsi

## 4. Admin buyruqlari (faqat guruhda)

| Buyruq | Vazifa |
|--------|--------|
| `/stats` | Statistika ko'rish |
| `/send_to USER_ID` | Foydalanuvchiga maqola yuborish |

### Maqola yuborish jarayoni:
1. Maqolani guruhda yozing yoki fayl yuborting
2. O'sha xabarga reply qiling: `/send_to 123456789`
3. Bot foydalanuvchiga avtomatik yuboradi

## 5. Bot oqimi

```
Foydalanuvchi
    ↓
/start → Menyu
    ↓
📝 Maqola YOKI 🔬 Scopus tanlaydi
    ↓
Ma'lumotlarni kiritadi
    ↓
Tasdiqlaydi → 50% to'lov
    ↓
Chek yuboradi
    ↓ → Admin guruhga chek keladi
Admin "✅ Qabul" bosadi
    ↓ → Foydalanuvchiga "Ish jarayonida" xabari
Admin maqola yozadi
    ↓
Admin "📤 Maqola tayyor" bosadi
    ↓ → Foydalanuvchiga "Qolgan 50% to'lang" xabari
Foydalanuvchi to'laydi + chek yuboradi
    ↓ → Admin guruhga 2-chek keladi
Admin "✅ To'lovni qabul" bosadi
    ↓
Admin: /send_to USER_ID (maqola faylini reply qilib)
    ↓ → Foydalanuvchiga maqola yetkaziladi ✅
```
