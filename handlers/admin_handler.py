from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from database import get_order, update_order, get_all_orders
from keyboards import admin_ready_keyboard, admin_second_check_keyboard
from config import ADMIN_GROUP_ID, CARD_NUMBER, CARD_OWNER

admin_router = Router()

# ========== CHEKNI QABUL QILISH ==========

@admin_router.callback_query(F.data.startswith("accept_check:"))
async def accept_check(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])

    update_order(order_id, "status", "⚙️ Ish jarayonida")
    order = get_order(order_id)
    order_type = "🔬 Scopus" if order.get("type") == "scopus" else "📝 Maqola"

    # Adminga tasdiqlash
    await call.message.edit_caption(
        caption=call.message.caption + "\n\n✅ <b>Chek qabul qilindi!</b>",
        reply_markup=admin_ready_keyboard(order_id, user_id),
        parse_mode="HTML"
    )

    # Foydalanuvchiga xabar
    await bot.send_message(
        user_id,
        f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
        f"📌 Buyurtma turi: {order_type}\n"
        f"🆔 Buyurtma: #{order_id[:8]}\n\n"
        f"⚙️ Maqolangiz <b>ish jarayonida</b>!\n"
        f"⏱ Tayyor bo'lishiga <b>30 daqiqadan 1 soatgacha</b> vaqt ketishi mumkin.\n\n"
        f"Maqola tayyor bo'lganda sizga bot orqali xabar yuboriladi.",
        parse_mode="HTML"
    )

# ========== CHEKNI RAD ETISH ==========

@admin_router.callback_query(F.data.startswith("reject_check:"))
async def reject_check(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])

    update_order(order_id, "status", "❌ Chek rad etildi")

    await call.message.edit_caption(
        caption=call.message.caption + "\n\n❌ <b>Chek rad etildi.</b>",
        parse_mode="HTML"
    )

    await bot.send_message(
        user_id,
        f"❌ <b>Chekingiz qabul qilinmadi.</b>\n\n"
        f"Sabab: chek noto'g'ri yoki to'lov tasdiqlanmadi.\n"
        f"Iltimos, qayta to'lov qilib, to'g'ri chek yuboring yoki admin bilan bog'laning.",
        parse_mode="HTML"
    )

# ========== MAQOLA TAYYOR — FOYDALANUVCHIGA XABAR ==========

@admin_router.callback_query(F.data.startswith("article_ready:"))
async def article_ready(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])

    update_order(order_id, "status", "💳 Qolgan to'lov kutilmoqda")
    order = get_order(order_id)

    await call.message.edit_caption(
        caption=call.message.caption + "\n\n📢 <b>Foydalanuvchiga xabar yuborildi.</b>",
        parse_mode="HTML"
    )

    # Foydalanuvchiga 2-to'lov haqida xabar
    from keyboards import second_payment_keyboard
    await bot.send_message(
        user_id,
        f"🎉 <b>Maqolangiz tayyor!</b>\n\n"
        f"Maqolani olish uchun qolgan <b>50% to'lovni</b> amalga oshiring:\n\n"
        f"💳 Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"Karta egasi: <b>{CARD_OWNER}</b>\n\n"
        f"To'lovni amalga oshirgach, chek rasmini yuboring.",
        reply_markup=second_payment_keyboard(),
        parse_mode="HTML"
    )

# ========== IKKINCHI CHEK — FOYDALANUVCHIDAN ==========

@admin_router.message(F.photo & F.chat.type == "private")
async def handle_second_check(message: Message, bot: Bot):
    # Bu handler faqat state yo'q holda kelgan rasmlar uchun
    # Ikkinchi to'lov chekini boshqaradi
    pass

# Foydalanuvchi "Qolgan 50% to'lovni qildim" bosadi
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@admin_router.callback_query(F.data == "second_paid")
async def second_paid_clicked(call: CallbackQuery):
    await call.message.edit_text(
        "📸 Iltimos, qolgan 50% to'lov cheki rasmini yuboring:"
    )

    # user_id ni saqlash uchun state ishlatmaslik — callback orqali order topamiz
    from database import get_all_orders
    orders = get_all_orders()
    for oid, o in orders.items():
        if o.get("user_id") == call.from_user.id and o.get("status") == "💳 Qolgan to'lov kutilmoqda":
            update_order(oid, "awaiting_second_check", True)
            break

@admin_router.message(F.photo & F.chat.type == "private")
async def second_check_photo(message: Message, bot: Bot):
    from database import get_all_orders
    orders = get_all_orders()

    target_order = None
    target_oid = None
    for oid, o in orders.items():
        if o.get("user_id") == message.from_user.id and o.get("awaiting_second_check"):
            target_order = o
            target_oid = oid
            break

    if not target_order:
        return

    update_order(target_oid, "status", "🧾 2-chek tekshirilmoqda")
    update_order(target_oid, "awaiting_second_check", False)

    order_type = "🔬 Scopus" if target_order.get("type") == "scopus" else "📝 Maqola"
    caption = (
        f"💳 <b>IKKINCHI TO'LOV — Chek keldi!</b>\n\n"
        f"📌 Tur: {order_type}\n"
        f"🆔 Order ID: <code>{target_oid}</code>\n"
        f"👤 Foydalanuvchi: @{message.from_user.username or '—'} (ID: {message.from_user.id})\n\n"
        f"✅ Qabul qilib maqolani yuboring."
    )

    photo_id = message.photo[-1].file_id
    await bot.send_photo(
        ADMIN_GROUP_ID,
        photo=photo_id,
        caption=caption,
        reply_markup=admin_second_check_keyboard(target_oid, message.from_user.id),
        parse_mode="HTML"
    )

    await message.answer(
        "⏳ <b>To'lovingiz tekshirilmoqda.</b>\n\n"
        "Tasdiqlanishi bilan maqolangiz sizga yuboriladi!",
        parse_mode="HTML"
    )

# ========== IKKINCHI TO'LOV TASDIQLASH VA MAQOLA YUBORISH ==========

@admin_router.callback_query(F.data.startswith("send_article:"))
async def send_article(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])

    update_order(order_id, "status", "✅ Tugallandi")

    await call.message.edit_caption(
        caption=call.message.caption + "\n\n📤 <b>Maqola yuborilmoqda...</b>",
        parse_mode="HTML"
    )

    await bot.send_message(
        user_id,
        "📤 <b>Maqolangiz yuborilmoqda...</b>\n\n"
        "Admin hozir maqolani sizga yuboradi. Bir ozdan so'ng qabul qilasiz.",
        parse_mode="HTML"
    )

    # Admin endi maqolani to'g'ridan-to'g'ri foydalanuvchiga yuborishi uchun
    await call.message.answer(
        f"✅ To'lov tasdiqlandi!\n\n"
        f"Endi maqolani foydalanuvchiga yuboring:\n"
        f"👤 User ID: <code>{user_id}</code>\n\n"
        f"Maqola faylini shu guruhda forward qiling va quyidagi buyruqdan foydalaning:\n"
        f"<code>/send_to {user_id}</code>",
        parse_mode="HTML"
    )

@admin_router.callback_query(F.data.startswith("reject_second:"))
async def reject_second(call: CallbackQuery, bot: Bot):
    parts = call.data.split(":")
    order_id = parts[1]
    user_id = int(parts[2])

    update_order(order_id, "status", "❌ 2-chek rad etildi")

    await call.message.edit_caption(
        caption=call.message.caption + "\n\n❌ <b>2-chek rad etildi.</b>",
        parse_mode="HTML"
    )

    await bot.send_message(
        user_id,
        "❌ <b>Ikkinchi to'lovingiz tasdiqlanmadi.</b>\n\n"
        "Iltimos, to'g'ri chek yuboring yoki admin bilan bog'laning.",
        parse_mode="HTML"
    )

# ========== ADMIN: FOYDALANUVCHIGA MAQOLA YUBORISH ==========

@admin_router.message(Command("send_to"), F.chat.id == ADMIN_GROUP_ID)
async def admin_send_to(message: Message, bot: Bot):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("Format: /send_to USER_ID\nKeyin maqola faylini reply sifatida yuboring.")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.reply("❌ Noto'g'ri user ID.")
        return

    # Reply bilan maqola yuborish
    if message.reply_to_message:
        reply = message.reply_to_message
        if reply.document:
            await bot.send_document(
                user_id,
                document=reply.document.file_id,
                caption="🎉 <b>Maqolangiz tayyor!</b>\n\nXizmatimizdan foydalanganingiz uchun rahmat! 🙏",
                parse_mode="HTML"
            )
        elif reply.text:
            await bot.send_message(
                user_id,
                f"🎉 <b>Maqolangiz tayyor!</b>\n\n{reply.text}",
                parse_mode="HTML"
            )
        await message.reply(f"✅ Maqola {user_id} ga muvaffaqiyatli yuborildi!")
    else:
        await message.reply(
            "ℹ️ Maqola faylini <b>reply</b> qiling va /send_to USER_ID buyrug'ini yuboring.",
            parse_mode="HTML"
        )

# ========== ADMIN STATISTIKA ==========

@admin_router.message(Command("stats"), F.chat.id == ADMIN_GROUP_ID)
async def admin_stats(message: Message):
    orders = get_all_orders()
    total = len(orders)
    completed = sum(1 for o in orders.values() if "Tugallandi" in o.get("status", ""))
    in_progress = sum(1 for o in orders.values() if "jarayonida" in o.get("status", ""))
    pending = sum(1 for o in orders.values() if "kutilmoqda" in o.get("status", ""))

    await message.answer(
        f"📊 <b>Statistika:</b>\n\n"
        f"📦 Jami buyurtmalar: {total}\n"
        f"✅ Tugallangan: {completed}\n"
        f"⚙️ Jarayonda: {in_progress}\n"
        f"⏳ Kutilmoqda: {pending}",
        parse_mode="HTML"
    )
