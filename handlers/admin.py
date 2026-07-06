from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from states.fsm_states import AdminStates
from database import db
from locales.strings import MESSAGES
from keyboards import reply, inline
from config import ADMIN_IDS

router = Router()

# Middleware-like check for admin
async def is_admin(user_id):
    try:
        admins = await db.get_admins()
        return int(user_id) in admins
    except:
        return False

@router.message(StateFilter("*"), F.text.in_([
    "⬅️ Mijoz menyusi", "⬅️ Orqaga", "/start", "/admin", "Mijoz menyusi", "Orqaga"
]))
async def cancel_state_navigation(message: types.Message, state: FSMContext, bot):
    await state.clear()
    if message.text == "/admin":
        await admin_cmd(message)
    elif message.text in ["⬅️ Mijoz menyusi", "Mijoz menyusi", "/start"]:
        from handlers.client import start_cmd
        await start_cmd(message, state, bot)
    else:
        if await is_admin(message.from_user.id):
            await admin_cmd(message)
        else:
            from handlers.client import start_cmd
            await start_cmd(message, state, bot)

@router.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Admin paneliga xush kelibsiz!", reply_markup=reply.get_admin_menu_kb())

@router.message(F.text == MESSAGES['uz']['admin_stats_btn'])
async def show_stats(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    stats = await db.get_stats()
    
    text = (
        "📊 **iWater — Bot Analitikasi va Statistikasi**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 **Jami foydalanuvchilar:** {stats['total_users']:,} ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📦 **Buyurtmalar ko'rsatkichlari:**\n"
        f"  🔹 Jami buyurtmalar: {stats['total_orders']:,} ta\n"
        f"  📅 Bugungi buyurtmalar: {stats['today_orders']:,} ta\n"
        f"  🏁 Yetkazib berilgan: {stats['delivered_orders']:,} ta\n"
        f"  ❌ Rad etilgan: {stats['rejected_orders']:,} ta\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💰 **Moliyaviy ko'rsatkichlar:**\n"
        f"  💳 Jami savdo summasi: **{stats['total_sales']:,}** so'm\n"
        f"  💵 Bugungi savdo summasi: **{stats['today_sales']:,}** so'm\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Barcha ma'lumotlar real vaqt rejimida taqdim etilmoqda.*"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=MESSAGES['uz']['admin_excel_btn'], callback_data="export_excel")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "export_excel")
async def export_excel(call: types.CallbackQuery, bot):
    if not await is_admin(call.from_user.id): return
    
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Buyurtmalar"
    ws.append(["ID", "Foydalanuvchi ID", "Mahsulot", "Summa", "Manzil", "Status", "To'lov", "Sana"])
    
    orders = await db.get_all_orders()
    for o in orders:
        ws.append([o[0], o[1], o[2], o[3], o[4], o[7], o[9], o[12]])
    
    file_path = "orders_report.xlsx"
    wb.save(file_path)
    
    from aiogram.types import FSInputFile
    await call.message.answer_document(FSInputFile(file_path), caption="📊 Barcha buyurtmalar hisoboti")
    await call.answer()

@router.callback_query(F.data == "admin_channels")
async def admin_channels(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    channels = await db.get_channels()
    await call.message.edit_text("📢 Kanallar ro'yxati:", reply_markup=inline.get_admin_channels_list_kb(channels))

@router.callback_query(F.data == "add_channel")
async def add_channel_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_channel_data'], parse_mode="Markdown")
    await state.set_state(AdminStates.add_channel)

@router.message(AdminStates.add_channel)
async def add_channel_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    try:
        parts = message.text.split("|")
        ch_id = parts[0].strip()
        name = parts[1].strip()
        link = parts[2].strip()
        await db.add_channel(ch_id, name, link)
        await message.answer(MESSAGES['uz']['channel_added'])
        await state.clear()
        await admin_cmd(message)
    except:
        await message.answer("Xato format! Iltimos, `@username | Nomi | Link` ko'rinishida yuboring.")

@router.callback_query(F.data.startswith("del_channel_"))
async def del_channel(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    ch_id = call.data.replace("del_channel_", "")
    await db.delete_channel(ch_id)
    await call.answer(MESSAGES['uz']['channel_deleted'])
    await admin_channels(call)

@router.callback_query(F.data == "admin_images")
async def admin_images(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Rasm qo'shish", callback_data="add_image")],
        [InlineKeyboardButton(text="🗑 Hammasini o'chirish", callback_data="clear_images")]
    ])
    await call.message.edit_text("🖼️ Start rasmlarini boshqarish:", reply_markup=kb)

@router.callback_query(F.data == "add_image")
async def add_image_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['send_start_image'])
    await state.set_state(AdminStates.add_image)

@router.message(AdminStates.add_image, F.photo)
async def add_image_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await db.add_start_image(message.photo[-1].file_id)
    await message.answer(MESSAGES['uz']['image_added'])
    await state.clear()
    await admin_cmd(message)

@router.callback_query(F.data == "clear_images")
async def clear_images(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    await db.clear_start_images()
    await call.answer(MESSAGES['uz']['images_cleared'])

@router.callback_query(F.data == "admin_terms")
async def admin_terms(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_terms_text'])
    await state.set_state(AdminStates.edit_terms)

@router.message(AdminStates.edit_terms)
async def edit_terms_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await db.set_setting('terms_uz', message.text)
    await message.answer(MESSAGES['uz']['terms_updated'])
    await state.clear()
    await admin_cmd(message)

@router.message(F.text == MESSAGES['uz']['admin_settings_btn'])
async def show_settings(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    web_on = (await db.get_setting('web_site_status')) == '1'
    price = await db.get_setting('water_price')
    await message.answer(
        f"⚙️ **Bot Sozlamalari**\n\n💰 Hozirgi narx: {price} so'm",
        reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on, user_id=message.from_user.id),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "toggle_web")
async def toggle_web(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    current = await db.get_setting('web_site_status')
    new_status = '1' if current == '0' else '0'
    await db.set_setting('web_site_status', new_status)
    
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    web_on = new_status == '1'
    await call.message.edit_reply_markup(reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on, user_id=call.from_user.id))
    await call.answer(f"Veb-sayt rejimi {'yoqildi' if web_on else 'o‘chirildi'}!")

@router.callback_query(F.data == "toggle_payment")
async def toggle_payment(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    current = await db.get_setting('manual_payment_status')
    new_status = '1' if current == '0' else '0'
    await db.set_setting('manual_payment_status', new_status)
    
    manual_on = new_status == '1'
    web_on = (await db.get_setting('web_site_status')) == '1'
    await call.message.edit_reply_markup(reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on, user_id=call.from_user.id))
    await call.answer(MESSAGES['uz']['payment_mode_updated'].format(status="ON" if manual_on else "OFF"))

@router.callback_query(F.data == "set_price")
async def set_price_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_new_price'])
    await state.set_state(AdminStates.change_price)

@router.message(AdminStates.change_price)
async def set_price_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting!")
        return
    
    await db.set_setting('water_price', message.text)
    await message.answer(MESSAGES['uz']['price_updated'].format(price=message.text))
    await state.clear()
    await admin_cmd(message)

@router.callback_query(F.data == "edit_welcome_uz_btn")
async def edit_welcome_uz_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_welcome_uz'])
    await state.set_state(AdminStates.edit_welcome_uz)
    await call.answer()

@router.message(AdminStates.edit_welcome_uz)
async def edit_welcome_uz_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await db.set_setting('welcome_msg_uz', message.text)
    await message.answer(MESSAGES['uz']['welcome_updated_uz'])
    await state.clear()
    await admin_cmd(message)

@router.callback_query(F.data == "edit_welcome_ru_btn")
async def edit_welcome_ru_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_welcome_ru'])
    await state.set_state(AdminStates.edit_welcome_ru)
    await call.answer()

@router.message(AdminStates.edit_welcome_ru)
async def edit_welcome_ru_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await db.set_setting('welcome_msg_ru', message.text)
    await message.answer(MESSAGES['uz']['welcome_updated_ru'])
    await state.clear()
    await admin_cmd(message)

@router.callback_query(F.data == "edit_terms_uz_btn")
async def edit_terms_uz_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_terms_text'])
    await state.set_state(AdminStates.edit_terms)
    await call.answer()

@router.callback_query(F.data == "edit_terms_ru_btn")
async def edit_terms_ru_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer(MESSAGES['uz']['enter_terms_ru'])
    await state.set_state(AdminStates.edit_terms_ru)
    await call.answer()

@router.message(AdminStates.edit_terms_ru)
async def edit_terms_ru_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await db.set_setting('terms_ru', message.text)
    await message.answer(MESSAGES['uz']['terms_updated_ru'])
    await state.clear()
    await admin_cmd(message)

@router.message(F.text == MESSAGES['uz']['admin_search_order_btn'])
async def search_order_start(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer(MESSAGES['uz']['enter_search_order_id'])
    await state.set_state(AdminStates.search_order)

@router.message(AdminStates.search_order)
async def search_order_finish(message: types.Message, state: FSMContext, bot):
    if not await is_admin(message.from_user.id): return
    order_id_str = message.text.replace("#", "").strip()
    if not order_id_str.isdigit():
        await message.answer("Iltimos, faqat buyurtma ID raqamini kiriting!")
        return
    
    order_id = int(order_id_str)
    order = await db.get_order(order_id)
    if not order:
        await message.answer(MESSAGES['uz']['order_not_found'])
        return
    
    user_id = order[1]
    user_data = await db.get_user(user_id)
    name = user_data[2] if user_data else "Veb-sayt foydalanuvchisi"
    phone = user_data[3] if user_data else "Kiritilmagan"
    
    status_emoji = {
        'new': '🆕 Yangi',
        'accepted': '✅ Qabul qilingan',
        'on_the_way': '🚚 Yo\'lda',
        'delivered': '🏁 Yetkazilgan',
        'pending_payment': '💳 To\'lov kutilmoqda',
        'rejected': '❌ Rad etilgan'
    }.get(order[7], order[7])

    pay_type_str = order[9] if order[9] else "Noma'lum"
    details = (
        f"🔍 **Qidiruv natijasi:**\n\n"
        f"🆔 Buyurtma #{order[0]}\n"
        f"👤 Mijoz: {name}\n"
        f"📞 Tel: {phone}\n"
        f"📦 Mahsulot: {order[2]}\n"
        f"💰 Jami: {order[3]:,} so'm\n"
        f"📍 Manzil: {order[4]}\n"
        f"💳 To'lov: {pay_type_str}\n"
        f"⏳ Status: **{status_emoji}**\n"
        f"📅 Sana: {order[12]}"
    )
    
    if order[11]:
        details += f"\n⚠️ Sababi: {order[11]}"
        
    await message.answer(
        details, 
        reply_markup=inline.get_admin_order_kb(order[0], status=order[7], admin_name="Admin"),
        parse_mode="Markdown"
    )
    
    if order[5] != 0:
        try:
            await bot.send_location(message.chat.id, order[5], order[6])
        except Exception:
            pass
            
    await state.clear()

@router.message(F.text == MESSAGES['uz']['admin_mailing_btn'])
async def start_mailing(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id):
        return
    await message.answer(MESSAGES['uz']['admin_mailing_btn'], reply_markup=reply.get_admin_menu_kb())
    await state.set_state(AdminStates.mailing)

@router.message(AdminStates.mailing)
async def handle_mailing(message: types.Message, state: FSMContext, bot):
    if not await is_admin(message.from_user.id):
        return
    
    users = await db.get_all_users()
    count = 0
    for user in users:
        try:
            await bot.copy_message(user[0], message.chat.id, message.message_id)
            count += 1
        except Exception:
            continue
    
    await message.answer(MESSAGES['uz']['mailing_done'].format(count=count))
    await state.clear()

@router.callback_query(F.data.startswith("order_"))
async def manage_order(call: types.CallbackQuery, state: FSMContext, bot):
    if not await is_admin(call.from_user.id):
        await call.answer("Siz admin emassiz!", show_alert=True)
        return
    
    data = call.data.split("_")
    action = data[1]
    order_id = int(data[2])
    
    order = await db.get_order(order_id)
    if not order:
        await call.answer("Buyurtma topilmadi!")
        return
    
    if action == "reject":
        await call.message.answer(MESSAGES['uz']['enter_rejection_reason'])
        await state.update_data(reject_order_id=order_id)
        await state.set_state(AdminStates.rejection_reason)
        await call.answer()
        return

    user_id = order[1]
    user_data = await db.get_user(user_id)
    lang = user_data[4]
    admin_name = call.from_user.full_name
    
    if action == "accept":
        await db.update_order_status(order_id, 'accepted', call.from_user.id)
        await call.message.edit_reply_markup(reply_markup=inline.get_admin_order_kb(order_id, 'accepted', admin_name))
        await bot.send_message(user_id, MESSAGES[lang]['order_status_accepted'].format(id=order_id))
        await call.answer("Qabul qilindi!")
    elif action == "way":
        await db.update_order_status(order_id, 'on_the_way', call.from_user.id)
        await call.message.edit_reply_markup(reply_markup=inline.get_admin_order_kb(order_id, 'on_the_way', admin_name))
        await bot.send_message(user_id, MESSAGES[lang]['order_status_on_the_way'].format(id=order_id))
        await call.answer("Yo'lga chiqdi!")
    elif action == "done":
        await db.update_order_status(order_id, 'delivered', call.from_user.id)
        await call.message.edit_reply_markup(reply_markup=inline.get_admin_order_kb(order_id, 'delivered', admin_name))
        await bot.send_message(user_id, MESSAGES[lang]['order_status_delivered'].format(id=order_id))
        await call.answer("Yetkazildi!")

@router.message(AdminStates.rejection_reason)
async def handle_rejection(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    order_id = data.get('reject_order_id')
    reason = message.text
    
    order = await db.get_order(order_id)
    user_id = order[1]
    user_data = await db.get_user(user_id)
    lang = user_data[4]
    
    await db.update_order_rejection(order_id, reason)
    await bot.send_message(user_id, MESSAGES[lang]['order_rejected_msg'].format(id=order_id, reason=reason))
    await message.answer(f"#{order_id} buyurtma rad etildi.")
    await state.clear()

@router.callback_query(F.data.startswith("check_"))
async def handle_check(call: types.CallbackQuery, state: FSMContext, bot):
    data = call.data.split("_")
    action = data[1]
    order_id = int(data[2])
    
    order = await db.get_order(order_id)
    user_id = order[1]
    user_data = await db.get_user(user_id)
    lang = user_data[4]
    
    if action == "confirm":
        await db.update_order_status(order_id, 'accepted', call.from_user.id)
        await bot.send_message(user_id, MESSAGES[lang]['payment_confirmed'])
        await call.message.edit_reply_markup(reply_markup=inline.get_admin_order_kb(order_id, 'accepted', call.from_user.full_name))
        await call.answer("To'lov tasdiqlandi!")
    elif action == "reject":
        await call.message.answer("Chekni rad etish sababini yozing:")
        await state.update_data(reject_check_order_id=order_id)
        await state.set_state(AdminStates.check_rejection_reason)
        await call.answer()

@router.message(AdminStates.check_rejection_reason)
async def handle_check_rejection(message: types.Message, state: FSMContext, bot):
    data = await state.get_data()
    order_id = data.get('reject_check_order_id')
    reason = message.text
    
    order = await db.get_order(order_id)
    user_id = order[1]
    user_data = await db.get_user(user_id)
    lang = user_data[4]
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Mijozga qo'ng'iroq", url=f"tel:{user_data[3]}")]
    ])
    
    await bot.send_message(user_id, MESSAGES[lang]['payment_rejected'].format(reason=reason))
    await message.answer(f"#{order_id} to'lovi rad etildi.", reply_markup=kb)
    await state.clear()

@router.message(F.text == "⬅️ Mijoz menyusi")
async def back_to_client(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    await message.answer(MESSAGES[lang]['main_menu'], reply_markup=reply.get_main_menu_kb(lang))
    await state.clear()

# --- Dynamic Admin Management ---
@router.callback_query(F.data == "admin_manage")
async def admin_manage_list(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    
    from config import ADMIN_IDS
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    admins = list(ADMIN_IDS)
    extra_str = await db.get_setting('extra_admins', '')
    if not extra_str:
        extra_str = ""
    extra_ids = []
    if extra_str:
        extra_ids = [int(i.strip()) for i in extra_str.split(",") if i.strip().isdigit()]
    
    text = (
        "👥 **Bot Administratorlari boshqaruvi**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "👑 **Asosiy adminlar (Tizimli .env orqali):**\n"
    )
    for aid in admins:
        text += f"  • `{aid}`\n"
        
    if extra_ids:
        text += "\n👥 **Qo'shimcha adminlar (Dinamik):**\n"
        for aid in extra_ids:
            text += f"  • `{aid}`\n"
    else:
        text += "\n*Hozircha qo'shimcha dinamik adminlar yo'q.*"
        
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n⚠️ *Qo'shimcha adminlarni pastda o'chirishingiz yoki yangi admin qo'shishingiz mumkin.*"
    
    kb_list = []
    for aid in extra_ids:
        kb_list.append([InlineKeyboardButton(text=f"🗑 O'chirish: {aid}", callback_data=f"del_extra_admin_{aid}")])
    kb_list.append([InlineKeyboardButton(text="➕ Yangi Admin qo'shish", callback_data="add_extra_admin_start")])
    kb_list.append([InlineKeyboardButton(text="⬅️ Sozlamalarga qaytish", callback_data="admin_back_to_settings")])
    
    kb = InlineKeyboardMarkup(inline_keyboard=kb_list)
    await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "admin_back_to_settings")
async def admin_back_to_settings(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    web_on = (await db.get_setting('web_site_status')) == '1'
    price = await db.get_setting('water_price')
    await call.message.edit_text(
        f"⚙️ **Bot Sozlamalari**\n\n💰 Hozirgi narx: {price} so'm",
        reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on, user_id=call.from_user.id),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("del_extra_admin_"))
async def del_extra_admin(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    aid_to_del = call.data.replace("del_extra_admin_", "")
    
    extra_str = await db.get_setting('extra_admins', '')
    if not extra_str:
        extra_str = ""
    ids = [i.strip() for i in extra_str.split(",") if i.strip()]
    if aid_to_del in ids:
        ids.remove(aid_to_del)
    await db.set_setting('extra_admins', ",".join(ids))
        
    await call.answer("Admin muvaffaqiyatli o'chirildi!", show_alert=True)
    await admin_manage_list(call)

@router.callback_query(F.data == "add_extra_admin_start")
async def add_extra_admin_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer("➕ **Yangi admin qo'shish**\n\nIltimos, yangi admin bo'ladigan foydalanuvchining **Telegram ID raqamini** (faqat raqam) yuboring:")
    await state.set_state(AdminStates.add_admin)
    await call.answer()

@router.message(AdminStates.add_admin)
async def add_extra_admin_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    val = message.text.strip()
    if not val.isdigit():
        await message.answer("⚠️ Noto'g'ri format! Iltimos, faqat Telegram ID raqamini yuboring:")
        return
    
    extra_str = await db.get_setting('extra_admins', '')
    if not extra_str:
        extra_str = ""
    ids = [i.strip() for i in extra_str.split(",") if i.strip()]
    if val not in ids:
        ids.append(val)
        await db.set_setting('extra_admins', ",".join(ids))
        await message.answer(f"✅ Foydalanuvchi `{val}` muvaffaqiyatli administrator qilib tayinlandi!")
    else:
        await message.answer(f"⚠️ Foydalanuvchi `{val}` allaqachon adminlar ro'yxatida mavjud!")
        
    await state.clear()
    await admin_cmd(message)

# --- Bot Creator / Developer Settings ---
@router.message(~StateFilter(AdminStates.edit_creator_auth), Command("setup1978", "creator_setup"))
@router.message(~StateFilter(AdminStates.edit_creator_auth), F.text == "1978")
async def admin_creator_settings_command(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    await message.answer("🔐 **Yaratuvchi ma'lumotlarini tahrirlash**\n\nIltimos, davom etish uchun maxsus **1978** parolini kiriting:")
    await state.set_state(AdminStates.edit_creator_auth)

@router.callback_query(F.data == "admin_creator_settings")
async def admin_creator_settings_start(call: types.CallbackQuery, state: FSMContext):
    if not await is_admin(call.from_user.id): return
    await call.message.answer("🔐 **Yaratuvchi ma'lumotlarini tahrirlash**\n\nIltimos, davom etish uchun maxsus **1978** parolini kiriting:")
    await state.set_state(AdminStates.edit_creator_auth)
    await call.answer()

@router.message(AdminStates.edit_creator_auth)
async def admin_creator_auth_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    if message.text.strip() == "1978":
        curr_username = await db.get_setting('creator_username', '@iwater_dev')
        curr_comment = await db.get_setting('creator_comment', "iWater botining rasmiy yaratuvchisi.")
        await message.answer(
            "🔓 **Muvaffaqiyatli autentifikatsiya!**\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💻 Joriy Yaratuvchi username: {curr_username}\n"
            f"📝 Joriy Yaratuvchi izoh/sharh: {curr_comment}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "✍️ Yangi ma'lumotlarni quyidagi formatda yuboring:\n"
            "`@username | Sharh` (Masalan: `@Sardor_dev | iWater botining professional dasturchisi`):"
        )
        await state.set_state(AdminStates.edit_creator_info)
    else:
        await message.answer("❌ Noto'g'ri parol! Amaliyot bekor qilindi.")
        await state.clear()
        await admin_cmd(message)

@router.message(AdminStates.edit_creator_info)
async def admin_creator_info_finish(message: types.Message, state: FSMContext):
    if not await is_admin(message.from_user.id): return
    parts = message.text.split("|")
    if len(parts) < 2:
        await message.answer("⚠️ Noto'g'ri format! Iltimos, `@username | Sharh` formatida yuboring:")
        return
    
    username = parts[0].strip()
    comment = parts[1].strip()
    
    if not username.startswith("@"):
        username = "@" + username
        
    await db.set_setting('creator_username', username)
    await db.set_setting('creator_comment', comment)
    
    await message.answer("✅ Yaratuvchi ma'lumotlari muvaffaqiyatli yangilandi!")
    await state.clear()
    await admin_cmd(message)

# --- Water Reminder (Friendly Ad) Broadcast ---
@router.callback_query(F.data == "admin_send_water_reminder")
async def admin_send_water_reminder_prompt(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, yuborilsin", callback_data="confirm_send_water_reminder"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_back_to_settings")
        ]
    ])
    await call.message.edit_text(
        "💧 **Suv eslatmasi (Reklama) yuborish**\n\n"
        "Haqiqatdan ham barcha foydalanuvchilarga suv buyurtma qilish bo'yicha chiroyli va hushmuomila eslatma yuborishni xohlaysizmi?",
        reply_markup=kb,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "confirm_send_water_reminder")
async def confirm_send_water_reminder(call: types.CallbackQuery, bot):
    if not await is_admin(call.from_user.id): return
    await call.message.edit_text("⏳ Eslatmalar barcha foydalanuvchilarga yuborilmoqda, iltimos kuting...")
    
    import asyncio
    users = await db.get_all_users()
    sent_count = 0
    
    uz_msg = (
        "💧 **Assalomu alaykum! Charchamayapsizmi?**\n\n"
        "Sog'ligingiz uchun kuniga kamida 2 litr toza va sifatli suv ichishni unutmang. 😊\n"
        "Uyingizda yoki ofisingizda suv tugab qolmadimi?\n\n"
        "Agar sizga suv kerak bo'lsa, quyidagi tugmani bosib, tezkor va oson buyurtma berishingiz mumkin! 🚚💨\n\n"
        "iWater xizmati har doim sizga xizmat qilishdan mamnun! 💙"
    )
    
    ru_msg = (
        "💧 **Здравствуйте! Как ваши дела?**\n\n"
        "Не забывайте пить не менее 2 литров чистой воды в день для вашего здоровья. 😊\n"
        "Не закончилась ли у вас вода дома или в офисе?\n\n"
        "Если вам нужна вода, нажмите на кнопку ниже, чтобы сделать заказ быстро и легко! 🚚💨\n\n"
        "Сервис iWater всегда рад служить вам! 💙"
    )
    
    for u in users:
        user_id = u[0]
        try:
            user_data = await db.get_user(user_id)
            lang = user_data[4] if user_data else 'uz'
            msg = uz_msg if lang == 'uz' else ru_msg
            
            await bot.send_message(
                user_id, 
                msg, 
                reply_markup=reply.get_main_menu_kb(lang),
                parse_mode="Markdown"
            )
            sent_count += 1
            await asyncio.sleep(0.05) # Rate limiting
        except:
            pass
            
    await call.message.answer(f"✅ Suv eslatmasi muvaffaqiyatli yakunlandi! {sent_count} ta foydalanuvchiga xabar yuborildi.")
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    web_on = (await db.get_setting('web_site_status')) == '1'
    price = await db.get_setting('water_price')
    await call.message.answer(
        f"⚙️ **Bot Sozlamalari**\n\n💰 Hozirgi narx: {price} so'm",
        reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on, user_id=call.from_user.id),
        parse_mode="Markdown"
    )
    await call.message.delete()
