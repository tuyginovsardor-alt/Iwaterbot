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
        return int(user_id) in ADMIN_IDS
    except:
        return False

@router.message(Command("admin"))
async def admin_cmd(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    await message.answer("Admin paneliga xush kelibsiz!", reply_markup=reply.get_admin_menu_kb())

@router.message(F.text == MESSAGES['uz']['admin_stats_btn'])
async def show_stats(message: types.Message):
    if not await is_admin(message.from_user.id):
        return
    users, orders = await db.get_stats()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=MESSAGES['uz']['admin_excel_btn'], callback_data="export_excel")]
    ])
    await message.answer(
        f"📊 Statistika:\n\n👥 Foydalanuvchilar: {users}\n📦 Jami buyurtmalar: {orders}",
        reply_markup=kb
    )

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
        reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on),
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
    await call.message.edit_reply_markup(reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on))
    await call.answer(f"Veb-sayt rejimi {'yoqildi' if web_on else 'o‘chirildi'}!")

@router.callback_query(F.data == "toggle_payment")
async def toggle_payment(call: types.CallbackQuery):
    if not await is_admin(call.from_user.id): return
    current = await db.get_setting('manual_payment_status')
    new_status = '1' if current == '0' else '0'
    await db.set_setting('manual_payment_status', new_status)
    
    manual_on = new_status == '1'
    web_on = (await db.get_setting('web_site_status')) == '1'
    await call.message.edit_reply_markup(reply_markup=inline.get_admin_settings_kb('uz', manual_on, web_on))
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
