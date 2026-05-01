import uuid
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from states import ArticleStates
from keyboards import (
    main_menu, language_keyboard, course_keyboard, skip_keyboard,
    confirm_keyboard, paid_keyboard, second_payment_keyboard, back_to_menu
)
from database import add_order, update_order, get_order
from config import ADMIN_GROUP_ID, CARD_NUMBER, CARD_OWNER

user_router = Router()

LANG_LABELS = {
    "lang_uzb": "🇺🇿 O'zbek",
    "lang_rus": "🇷🇺 Русский",
    "lang_eng": "🇬🇧 English",
    "lang_all": "🌐 O'zbek + Русский + English (3 tilda)",
}

# ==================== START ====================

@user_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "Maqola yozish xizmatiga xush kelibsiz.\n"
        "Quyidagi xizmatlardan birini tanlang:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@user_router.callback_query(F.data == "back_to_menu")
async def back_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "👋 <b>Bosh menyu</b>\n\nXizmat turini tanlang:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@user_router.callback_query(F.data == "contact")
async def contact_info(call: CallbackQuery):
    await call.message.edit_text(
        "📞 <b>Bog'lanish uchun:</b>\n\n"
        "Admin: @zxcva179\n"
        "Ish vaqti: 08:00 - 23:00",
        reply_markup=back_to_menu(),
        parse_mode="HTML"
    )

@user_router.callback_query(F.data == "my_orders")
async def my_orders(call: CallbackQuery):
    from database import get_all_orders
    orders = get_all_orders()
    user_orders = {k: v for k, v in orders.items() if v.get("user_id") == call.from_user.id}

    if not user_orders:
        await call.message.edit_text(
            "📋 Sizda hozircha buyurtmalar yo'q.",
            reply_markup=back_to_menu()
        )
        return

    text = "📋 <b>Sizning buyurtmalaringiz:</b>\n\n"
    for oid, o in user_orders.items():
        status = o.get("status", "noma'lum")
        otype = "📝 Maqola" if o.get("type") == "article" else "🔬 Scopus"
        text += f"{otype} | #{oid[:8]}\n🔄 Holat: {status}\n\n"

    await call.message.edit_text(text, reply_markup=back_to_menu(), parse_mode="HTML")

# ==================== ODDIY MAQOLA ====================

@user_router.callback_query(F.data == "article_order")
async def article_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(ArticleStates.article_title)
    await call.message.edit_text(
        "📝 <b>Maqola yozdirish</b>\n\n"
        "1️⃣ Maqolaning nomi yoki mavzusini kiriting:\n\n"
        "<i>Masalan: Sun'iy intellektning ta'limdagi o'rni</i>",
        parse_mode="HTML"
    )

@user_router.message(ArticleStates.article_title)
async def article_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(ArticleStates.article_language)
    await message.answer(
        "2️⃣ Maqola qaysi tilda yozilsin?",
        reply_markup=language_keyboard()
    )

@user_router.callback_query(ArticleStates.article_language, F.data.startswith("lang_"))
async def article_language(call: CallbackQuery, state: FSMContext):
    lang = LANG_LABELS.get(call.data, call.data)
    await state.update_data(language=lang)
    await state.set_state(ArticleStates.article_fullname)
    await call.message.edit_text(
        f"✅ Til tanlandi: {lang}\n\n"
        "3️⃣ F.I.SH ingizni kiriting:\n"
        "<i>Masalan: Karimov Jasur Aliyevich</i>",
        parse_mode="HTML"
    )

@user_router.message(ArticleStates.article_fullname)
async def article_fullname(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    await state.set_state(ArticleStates.article_university)
    await message.answer("4️⃣ Universitet nomini kiriting:")

@user_router.message(ArticleStates.article_university)
async def article_university(message: Message, state: FSMContext):
    await state.update_data(university=message.text)
    await state.set_state(ArticleStates.article_faculty)
    await message.answer("5️⃣ Fakultet nomini kiriting:")

@user_router.message(ArticleStates.article_faculty)
async def article_faculty(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await state.set_state(ArticleStates.article_direction)
    await message.answer("6️⃣ Yo'nalishni kiriting:")

@user_router.message(ArticleStates.article_direction)
async def article_direction(message: Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(ArticleStates.article_course)
    await message.answer("7️⃣ Kursni tanlang:", reply_markup=course_keyboard())

@user_router.callback_query(ArticleStates.article_course, F.data.startswith("course_"))
async def article_course(call: CallbackQuery, state: FSMContext):
    course = call.data.replace("course_", "") + "-kurs"
    await state.update_data(course=course)
    await state.set_state(ArticleStates.article_supervisor)
    await call.message.edit_text("8️⃣ Ilmiy rahbar F.I.SH ini kiriting:")

@user_router.message(ArticleStates.article_supervisor)
async def article_supervisor(message: Message, state: FSMContext):
    await state.update_data(supervisor=message.text)
    await state.set_state(ArticleStates.article_contact)
    await message.answer(
        "9️⃣ Telefon raqamingiz (ixtiyoriy):",
        reply_markup=skip_keyboard()
    )

@user_router.callback_query(ArticleStates.article_contact, F.data == "skip")
async def skip_contact(call: CallbackQuery, state: FSMContext):
    await state.update_data(contact="—")
    await state.set_state(ArticleStates.article_email)
    await call.message.edit_text(
        "🔟 Email manzilingiz (ixtiyoriy):",
        reply_markup=skip_keyboard()
    )

@user_router.message(ArticleStates.article_contact)
async def article_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(ArticleStates.article_email)
    await message.answer(
        "🔟 Email manzilingiz (ixtiyoriy):",
        reply_markup=skip_keyboard()
    )

@user_router.callback_query(ArticleStates.article_email, F.data == "skip")
async def skip_email(call: CallbackQuery, state: FSMContext):
    await state.update_data(email="—")
    await show_article_confirm(call.message, state, call.from_user.id)

@user_router.message(ArticleStates.article_email)
async def article_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await show_article_confirm(message, state, message.from_user.id)

async def show_article_confirm(msg, state, user_id):
    data = await state.get_data()
    await state.set_state(ArticleStates.article_confirm)
    text = (
        "📋 <b>Ariza ma'lumotlari — tekshiring:</b>\n\n"
        f"📌 <b>Maqola mavzusi:</b> {data.get('title')}\n"
        f"🌐 <b>Til:</b> {data.get('language')}\n"
        f"👤 <b>F.I.SH:</b> {data.get('fullname')}\n"
        f"🏛 <b>Universitet:</b> {data.get('university')}\n"
        f"🏫 <b>Fakultet:</b> {data.get('faculty')}\n"
        f"📚 <b>Yo'nalish:</b> {data.get('direction')}\n"
        f"🎓 <b>Kurs:</b> {data.get('course')}\n"
        f"👨‍🏫 <b>Ilmiy rahbar:</b> {data.get('supervisor')}\n"
        f"📞 <b>Telefon:</b> {data.get('contact')}\n"
        f"📧 <b>Email:</b> {data.get('email')}\n"
    )
    await msg.answer(text, reply_markup=confirm_keyboard(), parse_mode="HTML")

@user_router.callback_query(ArticleStates.article_confirm, F.data == "confirm_order")
async def article_confirmed(call: CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    order_id = str(uuid.uuid4())

    add_order(order_id, {
        "type": "article",
        "user_id": call.from_user.id,
        "username": call.from_user.username or "—",
        "status": "⏳ To'lov kutilmoqda",
        **data
    })

    await state.update_data(order_id=order_id)
    await state.set_state(ArticleStates.article_check)

    await call.message.edit_text(
        f"✅ <b>Arizangiz qabul qilindi!</b>\n\n"
        f"💳 <b>Maqola yozilishini boshlash uchun oldindan 50% to'lovni amalga oshiring.</b>\n\n"
        f"Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirgach, <b>chek rasmini</b> yuboring.",
        reply_markup=paid_keyboard(),
        parse_mode="HTML"
    )

@user_router.callback_query(F.data == "i_paid")
async def user_i_paid(call: CallbackQuery):
    await call.message.edit_text(
        "📸 Iltimos, to'lov cheki rasmini yuboring (screenshot yoki foto):"
    )

@user_router.message(ArticleStates.article_check, F.photo)
async def article_check_received(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    order_id = data.get("order_id")
    update_order(order_id, "status", "🧾 Chek tekshirilmoqda")

    from keyboards import admin_check_keyboard
    caption = (
        f"🧾 <b>YANGI BUYURTMA — Chek keldi!</b>\n\n"
        f"📌 Tur: 📝 Maqola\n"
        f"🆔 Order ID: <code>{order_id}</code>\n"
        f"👤 Foydalanuvchi: @{message.from_user.username or '—'} (ID: {message.from_user.id})\n\n"
        f"📚 <b>Mavzu:</b> {data.get('title')}\n"
        f"🌐 <b>Til:</b> {data.get('language')}\n"
        f"👤 <b>F.I.SH:</b> {data.get('fullname')}\n"
        f"🏛 <b>Universitet:</b> {data.get('university')}\n"
        f"🏫 <b>Fakultet:</b> {data.get('faculty')}\n"
        f"📚 <b>Yo'nalish:</b> {data.get('direction')}\n"
        f"🎓 <b>Kurs:</b> {data.get('course')}\n"
        f"👨‍🏫 <b>Ilmiy rahbar:</b> {data.get('supervisor')}\n"
        f"📞 <b>Telefon:</b> {data.get('contact')}\n"
        f"📧 <b>Email:</b> {data.get('email')}\n"
    )

    photo_id = message.photo[-1].file_id
    await bot.send_photo(
        ADMIN_GROUP_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=admin_check_keyboard(order_id, message.from_user.id),
        parse_mode="HTML"
    )

    await message.answer(
        "⏳ <b>Chekingiz adminga yuborildi!</b>\n\n"
        "Admin tekshirgandan so'ng sizga xabar beriladi.\n"
        "Maqola yozilishi <b>30 daqiqadan 1 soatgacha</b> davom etishi mumkin.",
        parse_mode="HTML"
    )
    await state.clear()

# ==================== SCOPUS MAQOLA ====================

@user_router.callback_query(F.data == "scopus_order")
async def scopus_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(ArticleStates.scopus_fullname)
    await call.message.edit_text(
        "🔬 <b>Scopus maqola yozdirish</b>\n\n"
        "Muallif haqida ma'lumotlarni to'ldiring:\n\n"
        "1️⃣ F.I.SH ingizni kiriting:\n"
        "<i>Masalan: Karimov Jasur Aliyevich</i>",
        parse_mode="HTML"
    )

@user_router.message(ArticleStates.scopus_fullname)
async def scopus_fullname(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    await state.set_state(ArticleStates.scopus_university)
    await message.answer("2️⃣ Universitet nomini kiriting:")

@user_router.message(ArticleStates.scopus_university)
async def scopus_university(message: Message, state: FSMContext):
    await state.update_data(university=message.text)
    await state.set_state(ArticleStates.scopus_faculty)
    await message.answer("3️⃣ Fakultet yoki bo'lim nomini kiriting:")

@user_router.message(ArticleStates.scopus_faculty)
async def scopus_faculty(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await state.set_state(ArticleStates.scopus_city_country)
    await message.answer(
        "4️⃣ Shahar va davlatni kiriting:\n"
        "<i>Masalan: Termiz, O'zbekiston</i>",
        parse_mode="HTML"
    )

@user_router.message(ArticleStates.scopus_city_country)
async def scopus_city(message: Message, state: FSMContext):
    await state.update_data(city_country=message.text)
    await state.set_state(ArticleStates.scopus_email)
    await message.answer("5️⃣ Email manzilingizni kiriting:")

@user_router.message(ArticleStates.scopus_email)
async def scopus_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(ArticleStates.scopus_orcid)
    await message.answer(
        "6️⃣ ORCID ID ingizni kiriting:\n"
        "<i>Masalan: 0000-0002-1825-0097</i>\n"
        "(Mavjud bo'lmasa ro'yxatdan o'ting: https://orcid.org/)",
        reply_markup=skip_keyboard(),
        parse_mode="HTML"
    )

@user_router.callback_query(ArticleStates.scopus_orcid, F.data == "skip")
async def skip_orcid(call: CallbackQuery, state: FSMContext):
    await state.update_data(orcid="Yo'q")
    await show_scopus_confirm(call.message, state, call.from_user.id)

@user_router.message(ArticleStates.scopus_orcid)
async def scopus_orcid(message: Message, state: FSMContext):
    await state.update_data(orcid=message.text)
    await show_scopus_confirm(message, state, message.from_user.id)

async def show_scopus_confirm(msg, state: FSMContext, user_id: int):
    data = await state.get_data()
    await state.set_state(ArticleStates.scopus_confirm)
    text = (
        "📋 <b>Scopus ariza — tekshiring:</b>\n\n"
        f"👤 <b>F.I.SH:</b> {data.get('fullname')}\n"
        f"🏛 <b>Universitet:</b> {data.get('university')}\n"
        f"🏫 <b>Fakultet/Bo'lim:</b> {data.get('faculty')}\n"
        f"📍 <b>Shahar, Davlat:</b> {data.get('city_country')}\n"
        f"📧 <b>Email:</b> {data.get('email')}\n"
        f"🔬 <b>ORCID ID:</b> {data.get('orcid')}\n"
    )
    await msg.answer(text, reply_markup=confirm_keyboard(), parse_mode="HTML")

@user_router.callback_query(ArticleStates.scopus_confirm, F.data == "confirm_order")
async def scopus_confirmed(call: CallbackQuery, state: FSMContext, bot):
    data = await state.get_data()
    order_id = str(uuid.uuid4())

    add_order(order_id, {
        "type": "scopus",
        "user_id": call.from_user.id,
        "username": call.from_user.username or "—",
        "status": "⏳ To'lov kutilmoqda",
        **data
    })

    await state.update_data(order_id=order_id)
    await state.set_state(ArticleStates.scopus_check)

    await call.message.edit_text(
        f"✅ <b>Scopus arizangiz qabul qilindi!</b>\n\n"
        f"💳 <b>Maqola yozilishini boshlash uchun oldindan 50% to'lovni amalga oshiring.</b>\n\n"
        f"Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirgach, <b>chek rasmini</b> yuboring.",
        reply_markup=paid_keyboard(),
        parse_mode="HTML"
    )

@user_router.message(ArticleStates.scopus_check, F.photo)
async def scopus_check_received(message: Message, state: FSMContext, bot):
    data = await state.get_data()
    order_id = data.get("order_id")
    update_order(order_id, "status", "🧾 Chek tekshirilmoqda")

    from keyboards import admin_check_keyboard
    caption = (
        f"🧾 <b>YANGI BUYURTMA — Chek keldi!</b>\n\n"
        f"📌 Tur: 🔬 Scopus Maqola\n"
        f"🆔 Order ID: <code>{order_id}</code>\n"
        f"👤 Foydalanuvchi: @{message.from_user.username or '—'} (ID: {message.from_user.id})\n\n"
        f"👤 <b>F.I.SH:</b> {data.get('fullname')}\n"
        f"🏛 <b>Universitet:</b> {data.get('university')}\n"
        f"🏫 <b>Fakultet/Bo'lim:</b> {data.get('faculty')}\n"
        f"📍 <b>Shahar, Davlat:</b> {data.get('city_country')}\n"
        f"📧 <b>Email:</b> {data.get('email')}\n"
        f"🔬 <b>ORCID ID:</b> {data.get('orcid')}\n"
    )

    photo_id = message.photo[-1].file_id
    await bot.send_photo(
        ADMIN_GROUP_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=admin_check_keyboard(order_id, message.from_user.id),
        parse_mode="HTML"
    )

    await message.answer(
        "⏳ <b>Chekingiz adminga yuborildi!</b>\n\n"
        "Admin tekshirgandan so'ng sizga xabar beriladi.\n"
        "Maqola yozilishi <b>30 daqiqadan 1 soatgacha</b> davom etishi mumkin.",
        parse_mode="HTML"
    )
    await state.clear()

# Bekor qilish
@user_router.callback_query(F.data == "cancel_order")
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(
        "❌ Ariza bekor qilindi.\n\nBosh menyuga qaytdingiz.",
        reply_markup=main_menu()
    )
