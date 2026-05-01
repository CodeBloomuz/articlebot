from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Maqola yozdirish", callback_data="article_order")],
        [InlineKeyboardButton(text="🔬 Scopus maqola yozdirish", callback_data="scopus_order")],
        [InlineKeyboardButton(text="📋 Buyurtmalarim", callback_data="my_orders")],
        [InlineKeyboardButton(text="📞 Bog'lanish", callback_data="contact")],
    ])

def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uzb")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_rus")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_eng")],
        [InlineKeyboardButton(text="🌐 UZB + RUS + ENG (3 tilda)", callback_data="lang_all")],
    ])

def course_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1-kurs", callback_data="course_1"),
            InlineKeyboardButton(text="2-kurs", callback_data="course_2"),
        ],
        [
            InlineKeyboardButton(text="3-kurs", callback_data="course_3"),
            InlineKeyboardButton(text="4-kurs", callback_data="course_4"),
        ],
    ])

def skip_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭ O'tkazib yuborish (ixtiyoriy)", callback_data="skip")],
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Tasdiqlash va yuborish", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")],
    ])

def paid_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 To'lov qildim — Chek yuboraman", callback_data="i_paid")],
    ])

def admin_check_keyboard(order_id: str, user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Chekni qabul qilish", callback_data=f"accept_check:{order_id}:{user_id}")],
        [InlineKeyboardButton(text="❌ Chekni rad etish", callback_data=f"reject_check:{order_id}:{user_id}")],
    ])

def admin_ready_keyboard(order_id: str, user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Maqola tayyor — Foydalanuvchiga xabar berish", callback_data=f"article_ready:{order_id}:{user_id}")],
    ])

def second_payment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Qolgan 50% to'lovni qildim", callback_data="second_paid")],
    ])

def admin_second_check_keyboard(order_id: str, user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ To'lovni qabul qilish va maqolani yuborish", callback_data=f"send_article:{order_id}:{user_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_second:{order_id}:{user_id}")],
    ])

def back_to_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")],
    ])
