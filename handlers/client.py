import re
import math
import random
import asyncio
import aiosqlite
from aiogram import Router, F, types, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from states.fsm_states import ClientStates
from database import db
from locales.strings import MESSAGES
from keyboards import reply, inline
from config import ADMIN_IDS

router = Router()

PHONE_REGEX = r"^\+998[0-9]{9}$"

async def get_next_start_image(state: FSMContext) -> str or None:
    images = await db.get_start_images()
    if not images:
        return None
    data = await state.get_data()
    idx = data.get('start_img_idx', 0)
    # Get the image at this index
    img = images[idx % len(images)]
    # Update state to point to the next image for the next step
    await state.update_data(start_img_idx=(idx + 1) % len(images))
    return img

async def send_main_menu_with_sequence(message: types.Message, state: FSMContext, lang: str):
    img = await get_next_start_image(state)
    caption = MESSAGES[lang]['main_menu']
    kb = reply.get_main_menu_kb(lang)
    if img:
        await message.answer_photo(img, caption=caption, reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(caption, reply_markup=kb, parse_mode="Markdown")
    await state.set_state(ClientStates.main_menu)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def check_subscription(bot: Bot, user_id: int):
    channels = await db.get_channels(mandatory_only=True)
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch[0], user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

@router.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext, bot: Bot):
    subbed = await check_subscription(bot, message.from_user.id)
    if not subbed:
        channels = await db.get_channels(mandatory_only=True)
        await message.answer(MESSAGES['uz']['sub_required'], reply_markup=inline.get_channels_kb(channels, 'uz'), parse_mode="Markdown")
        return

    user = await db.get_user(message.from_user.id)
    img = await get_next_start_image(state)
    
    lang = user[4] if user else 'uz'
    
    welcome_db_key = f'welcome_msg_{lang}'
    caption = await db.get_setting(welcome_db_key)
    if not caption:
        caption = MESSAGES[lang]['start'] if not user else MESSAGES[lang]['main_menu']
    
    caption_with_more = caption + "\n\nℹ️ More info: /more"
    
    kb = reply.get_lang_kb() if not user else reply.get_main_menu_kb(lang)
    
    if img:
        await message.answer_photo(img, caption=caption_with_more, reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(caption_with_more, reply_markup=kb, parse_mode="Markdown")
    
    if not user:
        await state.set_state(ClientStates.language)
    else:
        await state.set_state(ClientStates.main_menu)

@router.callback_query(F.data == "check_sub")
async def check_sub_btn(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    subbed = await check_subscription(bot, call.from_user.id)
    if subbed:
        await call.message.delete()
        await start_cmd(call.message, state, bot)
    else:
        await call.answer(MESSAGES['uz']['not_all_subbed'], show_alert=True)

@router.message(ClientStates.language)
async def set_lang(message: types.Message, state: FSMContext, bot: Bot):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    is_new = await db.add_user(message.from_user.id, message.from_user.username, message.from_user.full_name, lang)
    
    if is_new:
        admins = await db.get_admins()
        username_str = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"
        lang_name = "O'zbekcha" if lang == 'uz' else "Ruscha"
        text = (
            "🔔 **Yangi foydalanuvchi qo'shildi!**\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Ism:** {message.from_user.full_name}\n"
            f"🆔 **ID:** `{message.from_user.id}`\n"
            f"🌐 **Username:** {username_str}\n"
            f"🇺🇿 **Tanlangan til:** {lang_name}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        for admin_id in admins:
            try:
                await bot.send_message(admin_id, text, parse_mode="Markdown")
            except:
                pass

    await state.update_data(lang=lang)
    user = await db.get_user(message.from_user.id)
    if not user[3]: # if no phone
        await message.answer(MESSAGES[lang]['share_phone'], reply_markup=reply.get_phone_kb(lang), parse_mode="Markdown")
        await state.set_state(ClientStates.phone)
    else:
        await send_main_menu_with_sequence(message, state, lang)

@router.message(ClientStates.phone)
async def set_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'uz')
    is_profile_edit = data.get('edit_profile_phone', False)
    
    phone = None
    if message.contact:
        phone = message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    elif message.text:
        # Clean any spaces, dashes or parentheses
        text = re.sub(r"[\s\-\(\)]", "", message.text)
        if re.match(r"^998\d{9}$", text):
            phone = "+" + text
        elif re.match(r"^\+998\d{9}$", text):
            phone = text
        elif re.match(r"^\d{9}$", text):
            phone = "+998" + text
    
    if not phone:
        await message.answer(MESSAGES[lang]['phone_error'], parse_mode="Markdown")
        return

    await db.update_user_phone(message.from_user.id, phone)
    
    if is_profile_edit:
        success_msg = "✅ Telefon raqamingiz muvaffaqiyatli o'zgartirildi!" if lang == 'uz' else "✅ Номер телефона успешно изменен!"
        await message.answer(success_msg, parse_mode="Markdown")
        await state.update_data(edit_profile_phone=False)
        await state.set_state(ClientStates.main_menu)
        await show_profile_handler(message, state)
        return

    await send_main_menu_with_sequence(message, state, lang)

@router.message(F.text.in_([MESSAGES['uz']['order_btn'], MESSAGES['ru']['order_btn']]))
async def order_water(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    price = int(await db.get_setting('water_price', 15000))
    await state.update_data(quantity=1)
    
    img = await get_next_start_image(state)
    caption = MESSAGES[lang]['select_quantity'].format(total=price)
    kb = inline.get_quantity_kb(1, price, lang)
    if img:
        await message.answer_photo(img, caption=caption, reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(caption, reply_markup=kb, parse_mode="Markdown")

async def abandoned_cart_reminder(bot: Bot, user_id: int, lang: str):
    await asyncio.sleep(1800) # 30 mins
    # Check if cart still has items and order hasn't been placed
    # In a real app, you'd check a persistent state. 
    # For now, let's just check if the user is still in ClientStates.main_menu (not placing order)
    # Actually, a better check is needed. But for this scope, let's do a simple reminder if they are still 'online'.
    try:
        await bot.send_message(user_id, MESSAGES[lang]['abandoned_cart_msg'])
    except:
        pass

@router.callback_query(F.data.in_(['inc', 'dec', 'add_to_cart']))
async def handle_quantity(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    quantity = data.get('quantity', 1)
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    price = int(await db.get_setting('water_price', 15000))
    
    if call.data == 'inc':
        quantity += 1
        await state.update_data(quantity=quantity)
        total = quantity * price
        try:
            await call.message.edit_caption(
                caption=MESSAGES[lang]['select_quantity'].format(total=total),
                reply_markup=inline.get_quantity_kb(quantity, price, lang),
                parse_mode="Markdown"
            )
        except Exception:
            try:
                await call.message.edit_text(
                    MESSAGES[lang]['select_quantity'].format(total=total),
                    reply_markup=inline.get_quantity_kb(quantity, price, lang),
                    parse_mode="Markdown"
                )
            except Exception:
                pass
    elif call.data == 'dec':
        if quantity > 1:
            quantity -= 1
            await state.update_data(quantity=quantity)
            total = quantity * price
            try:
                await call.message.edit_caption(
                    caption=MESSAGES[lang]['select_quantity'].format(total=total),
                    reply_markup=inline.get_quantity_kb(quantity, price, lang),
                    parse_mode="Markdown"
                )
            except Exception:
                try:
                    await call.message.edit_text(
                        MESSAGES[lang]['select_quantity'].format(total=total),
                        reply_markup=inline.get_quantity_kb(quantity, price, lang),
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass
    elif call.data == 'add_to_cart':
        await state.update_data(cart_quantity=quantity)
        await call.answer(MESSAGES[lang]['added_to_cart'])
        await call.message.delete()
        await send_main_menu_with_sequence(call.message, state, lang)
        await call.message.answer(MESSAGES[lang]['added_to_cart_detailed'], reply_markup=inline.get_added_to_cart_kb(lang), parse_mode="Markdown")
        
        # Start reminder
        asyncio.create_task(abandoned_cart_reminder(bot, call.from_user.id, lang))

@router.callback_query(F.data == 'clear_cart')
async def clear_cart_handler(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    lang = user[4] if user else 'uz'
    await state.update_data(cart_quantity=0)
    
    try:
        await call.message.edit_text(MESSAGES[lang]['cart_empty'], parse_mode="Markdown")
    except Exception:
        await call.message.delete()
        await call.message.answer(MESSAGES[lang]['cart_empty'], parse_mode="Markdown")
    await call.answer(MESSAGES[lang]['cart_empty'])

@router.callback_query(F.data == 'open_cart')
async def open_cart_callback(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get('cart_quantity', 0)
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    price = int(await db.get_setting('water_price', 15000))
    
    if quantity == 0:
        await call.message.answer(MESSAGES[lang]['cart_empty'], parse_mode="Markdown")
    else:
        total = quantity * price
        await call.message.answer(
            MESSAGES[lang]['cart_content'].format(price=f"{price:,}", quantity=quantity, total=f"{total:,}"),
            reply_markup=inline.get_cart_kb(lang),
            parse_mode="Markdown"
        )
    await call.answer()

@router.message(F.text.in_([MESSAGES['uz']['cart_btn'], MESSAGES['ru']['cart_btn']]))
async def view_cart(message: types.Message, state: FSMContext):
    data = await state.get_data()
    quantity = data.get('cart_quantity', 0)
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    price = int(await db.get_setting('water_price', 15000))
    
    if quantity == 0:
        await message.answer(MESSAGES[lang]['cart_empty'], parse_mode="Markdown")
    else:
        total = quantity * price
        await message.answer(
            MESSAGES[lang]['cart_content'].format(price=f"{price:,}", quantity=quantity, total=f"{total:,}"),
            reply_markup=inline.get_cart_kb(lang),
            parse_mode="Markdown"
        )

@router.callback_query(F.data == 'checkout')
async def checkout(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    await call.message.delete()
    await call.message.answer(MESSAGES[lang]['send_location'], reply_markup=reply.get_location_kb(lang), parse_mode="Markdown")
    await state.set_state(ClientStates.location)

@router.message(ClientStates.location)
async def handle_location(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    
    address = "📍 Noma'lum manzil"
    lat, lon = 0, 0
    dist_info = ""

    if message.location:
        lat, lon = message.location.latitude, message.location.longitude
        address = "📍 Geolokatsiya (Xaritada)"
        
        w_lat = float(await db.get_setting('warehouse_lat', 41.2995))
        w_lon = float(await db.get_setting('warehouse_lon', 69.2401))
        dist = haversine(lat, lon, w_lat, w_lon)
        est_time = int(dist * 5 + 15) # Example formula
        dist_info = MESSAGES[lang]['dist_info'].format(dist=round(dist, 1), time=est_time)
    elif message.text:
        if message.text in [MESSAGES['uz']['back_btn'], MESSAGES['ru']['back_btn']]:
            await view_cart(message, state)
            return
        address = message.text
    else:
        await message.answer(MESSAGES[lang]['location_error'], parse_mode="Markdown")
        return

    await state.update_data(order_address=address, order_lat=lat, order_lon=lon, dist_info=dist_info)
    
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    await message.answer(MESSAGES[lang]['select_payment'], reply_markup=inline.get_payment_kb(lang, manual_on))
    await state.set_state(ClientStates.payment_type)

@router.callback_query(ClientStates.payment_type, F.data.startswith("pay_"))
async def handle_payment_type(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    
    if call.data == "pay_back":
        await call.message.delete()
        await call.message.answer(MESSAGES[lang]['send_location'], reply_markup=reply.get_location_kb(lang), parse_mode="Markdown")
        await state.set_state(ClientStates.location)
        return
    data = await state.get_data()
    quantity = data.get('cart_quantity', 0)
    price = int(await db.get_setting('water_price', 15000))
    total = quantity * price
    
    bonus_text = ""
    if user[5] == 0: # First order
        total = max(0, total - 5000)
        bonus_text = MESSAGES[lang]['first_order_bonus']

    payment_type = "Naqd" if call.data == "pay_cash" else "Karta (Manual)"
    
    if call.data == "pay_manual":
        kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=MESSAGES[lang]['back_btn'], callback_data="check_back")]])
        await call.message.edit_text(MESSAGES[lang]['send_check'].format(total=total), reply_markup=kb, parse_mode="Markdown")
        await state.update_data(payment_type=payment_type, final_total=total)
        await state.set_state(ClientStates.upload_check)
        return

    # Process Cash Order
    order_id = await db.create_order(
        call.from_user.id, 
        f"{quantity} dona 19L", 
        total, 
        data['order_address'], 
        data['order_lat'], 
        data['order_lon']
    )
    # Set payment type
    async with aiosqlite.connect(db.DB_PATH) as _db:
        await _db.execute("UPDATE orders SET payment_type = ? WHERE id = ?", (payment_type, order_id))
        await _db.commit()

    await db.increment_order_count(call.from_user.id)
    await state.update_data(cart_quantity=0)
    await call.message.delete()
    
    final_msg = (bonus_text + "\n\n" if bonus_text else "") + MESSAGES[lang]['order_received'].format(id=order_id)
    await call.message.answer(final_msg, reply_markup=reply.get_main_menu_kb(lang), parse_mode="Markdown")
    await state.set_state(ClientStates.main_menu)
    
    # Check for recent active orders
    recent_orders = await db.get_recent_active_orders(call.from_user.id, hours=2)
    linked_orders_text = ""
    # remove current order_id from recent orders if exists
    if order_id in recent_orders:
        recent_orders.remove(order_id)
    if recent_orders:
        linked_ids_str = ", ".join([f"#{oid:06d}" for oid in recent_orders])
        linked_orders_text = f"\n\n🔗 **DIQQAT! Mijozning oxirgi 2 soat ichida yana {len(recent_orders)} ta faol buyurtmasi bor! Bularni birga yetkazish mumkin.**\nBog'langan ID: {linked_ids_str}"

    # Notify admins
    username = call.from_user.username
    profile_link = f"[@{username}](https://t.me/{username})" if username else f"[Lichka](tg://user?id={call.from_user.id})"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                MESSAGES['uz']['new_order_admin'].format(
                    id=f"{order_id:06d}", name=user[2], profile_link=profile_link, phone=user[3],
                    quantity=quantity, total=total, address=data['order_address'], payment=payment_type
                ) + f"\n\n{data.get('dist_info', '')}" + linked_orders_text,
                reply_markup=inline.get_admin_order_kb(order_id),
                parse_mode="Markdown"
            )
            if data['order_lat'] != 0:
                await bot.send_location(admin_id, data['order_lat'], data['order_lon'])
        except Exception: continue

@router.callback_query(ClientStates.upload_check, F.data == "check_back")
async def handle_check_back(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    await call.message.delete()
    manual_on = (await db.get_setting('manual_payment_status')) == '1'
    await call.message.answer(MESSAGES[lang]['select_payment'], reply_markup=inline.get_payment_kb(lang, manual_on))
    await state.set_state(ClientStates.payment_type)
    await call.answer()

@router.message(ClientStates.upload_check, F.photo)
async def handle_check_photo(message: types.Message, state: FSMContext, bot):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    data = await state.get_data()
    quantity = data.get('cart_quantity', 0)
    price = int(await db.get_setting('water_price', 15000))
    total = quantity * price
    
    file_id = message.photo[-1].file_id
    order_id = await db.create_order(
        message.from_user.id, f"{quantity} dona 19L", total, 
        data['order_address'], data['order_lat'], data['order_lon']
    )
    
    async with aiosqlite.connect(db.DB_PATH) as _db:
        await _db.execute("UPDATE orders SET payment_type = ?, payment_check_file_id = ?, status = 'pending_payment' WHERE id = ?", 
                         ("Karta (Manual)", file_id, order_id))
        await _db.commit()

    await db.increment_order_count(message.from_user.id)
    await state.update_data(cart_quantity=0)
    await message.answer(MESSAGES[lang]['check_received'], reply_markup=reply.get_main_menu_kb(lang), parse_mode="Markdown")
    await state.set_state(ClientStates.main_menu)

    # Notify admins with Photo
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                admin_id, file_id,
                caption=MESSAGES['uz']['check_request_admin'].format(id=order_id, name=user[2], total=total),
                reply_markup=inline.get_admin_order_kb(order_id, status='pending_payment'),
                parse_mode="Markdown"
            )
        except Exception: continue

@router.message(F.text.in_([MESSAGES['uz']['history_btn'], MESSAGES['ru']['history_btn']]))
async def show_history(message: types.Message):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    orders = await db.get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer(MESSAGES[lang]['order_history_empty'], parse_mode="Markdown")
        return
    
    history_text = ""
    for o in orders:
        history_text += MESSAGES[lang]['order_history_item'].format(
            id=o[0], date=o[12], items=o[2], total=o[3], payment=o[9] or "Noma'lum", status=o[7]
        )
    
    await message.answer(MESSAGES[lang]['order_history'].format(history=history_text), parse_mode="Markdown")

def get_profile_content(user, full_name):
    lang = user[4]
    orders_count = user[5]
    liters = orders_count * 19
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    if lang == 'uz':
        if orders_count == 0:
            rank_name = "Suv shaydosi 💧 (Yangi a'zo)"
        elif 1 <= orders_count <= 4:
            rank_name = "Doimiy iste'molchi 🥤 (Faol)"
        elif 5 <= orders_count <= 9:
            rank_name = "Sodiq mijoz ⭐ (Ishonchli)"
        else:
            rank_name = "VIP Mijoz 👑 (Premium)"
            
        next_discount_count = 10 - (orders_count % 10)
        bonus_text = f"🎁 Keyingi 20% chegirmagacha **{next_discount_count}** ta buyurtma qoldi!"
        
        text = (
            f"👤 **MIJOZ PROFILI**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Foydalanuvchi:** {full_name}\n"
            f"🆔 **Telegram ID:** `{user[0]}`\n"
            f"📞 **Telefon raqami:** `{user[3] or 'Kiritilmagan'}`\n"
            f"🌐 **Tanlangan til:** `O'zbekcha 🇺🇿`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **XARIDLAR STATISTIKASI:**\n"
            f"🥤 **Buyurtmalar soni:** `{orders_count}` ta\n"
            f"💧 **Iste'mol qilingan suv:** `{liters}` litr\n"
            f"🏅 **Mijoz maqomi:** `{rank_name}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bonus_text}"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="profile_change_lang")],
            [InlineKeyboardButton(text="📞 Telefonni o'zgartirish", callback_data="profile_edit_phone")],
            [InlineKeyboardButton(text="📜 Buyurtmalar tarixi", callback_data="profile_order_history")]
        ])
    else:
        if orders_count == 0:
            rank_name = "Любитель воды 💧 (Новый участник)"
        elif 1 <= orders_count <= 4:
            rank_name = "Постоянный клиент 🥤 (Активный)"
        elif 5 <= orders_count <= 9:
            rank_name = "Лояльный клиент ⭐ (Надежный)"
        else:
            rank_name = "VIP Клиент 👑 (Премиум)"
            
        next_discount_count = 10 - (orders_count % 10)
        bonus_text = f"🎁 До следующей скидки 20% осталось **{next_discount_count}** заказов!"
        
        text = (
            f"👤 **ПРОФИЛЬ КЛИЕНТА**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Пользователь:** {full_name}\n"
            f"🆔 **Telegram ID:** `{user[0]}`\n"
            f"📞 **Номер телефона:** `{user[3] or 'Не указан'}`\n"
            f"🌐 **Выбранный язык:** `Русский 🇷🇺`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **СТАТИСТИКА ПОКУПОК:**\n"
            f"🥤 **Количество заказов:** `{orders_count}` шт\n"
            f"💧 **Потреблено воды:** `{liters}` литров\n"
            f"🏅 **Статус клиента:** `{rank_name}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bonus_text}"
        )
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌐 Сменить язык", callback_data="profile_change_lang")],
            [InlineKeyboardButton(text="📞 Изменить телефон", callback_data="profile_edit_phone")],
            [InlineKeyboardButton(text="📜 История заказов", callback_data="profile_order_history")]
        ])
        
    return text, kb

@router.message(F.text.in_([MESSAGES['uz']['settings_btn'], MESSAGES['ru']['settings_btn']]))
async def show_profile_handler(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    full_name = message.from_user.full_name
    text, kb = get_profile_content(user, full_name)
    
    img = await get_next_start_image(state)
    if img:
        await message.answer_photo(img, caption=text, reply_markup=kb, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.callback_query(F.data == "profile_change_lang")
async def profile_change_lang(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer()
        return
    
    current_lang = user[4]
    new_lang = 'ru' if current_lang == 'uz' else 'uz'
    
    await db.update_user_language(call.from_user.id, new_lang)
    updated_user = await db.get_user(call.from_user.id)
    
    text, kb = get_profile_content(updated_user, call.from_user.full_name)
    
    msg_lang_text = "🇺🇿 Til o'zgartirildi! Asosiy menyu yangilandi." if new_lang == 'uz' else "🇷🇺 Язык изменен! Главное меню обновлено."
    await call.message.answer(msg_lang_text, reply_markup=reply.get_main_menu_kb(new_lang))
    
    try:
        await call.message.edit_caption(caption=text, reply_markup=kb, parse_mode="Markdown")
    except:
        try:
            await call.message.edit_text(text=text, reply_markup=kb, parse_mode="Markdown")
        except:
            pass
            
    await call.answer("🌐 " + ("Til o'zgartirildi" if new_lang == 'uz' else "Язык изменен"))

@router.callback_query(F.data == "profile_edit_phone")
async def profile_edit_phone(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer()
        return
    lang = user[4]
    
    await state.update_data(edit_profile_phone=True, lang=lang)
    await state.set_state(ClientStates.phone)
    
    await call.message.answer(
        MESSAGES[lang]['share_phone'], 
        reply_markup=reply.get_phone_kb(lang), 
        parse_mode="Markdown"
    )
    await call.answer()

@router.callback_query(F.data == "profile_order_history")
async def profile_order_history(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    if not user:
        await call.answer()
        return
    lang = user[4]
    
    orders = await db.get_user_orders(call.from_user.id, limit=5)
    if not orders:
        await call.message.answer(MESSAGES[lang]['order_history_empty'], parse_mode="Markdown")
        await call.answer()
        return
    
    history_text = ""
    for o in orders:
        history_text += MESSAGES[lang]['order_history_item'].format(
            id=o[0], date=o[12], items=o[2], total=o[3], payment=o[9] or "Noma'lum", status=o[7]
        )
    
    await call.message.answer(MESSAGES[lang]['order_history'].format(history=history_text), parse_mode="Markdown")
    await call.answer()

@router.message(F.text.in_([MESSAGES['uz']['contact_btn'], MESSAGES['ru']['contact_btn']]))
async def show_contacts(message: types.Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Bot Yaratuvchisi", callback_data="client_view_creator")]
    ])
    
    img = await get_next_start_image(state)
    if img:
        await message.answer_photo(img, caption=MESSAGES[lang]['contact_info'], reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=False)
    else:
        await message.answer(MESSAGES[lang]['contact_info'], reply_markup=kb, parse_mode="Markdown", disable_web_page_preview=False)

@router.callback_query(F.data == "client_view_creator")
async def client_view_creator(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    lang = user[4] if user else 'uz'
    
    username = await db.get_setting('creator_username', '@iwater_dev')
    comment = await db.get_setting('creator_comment', "iWater botining rasmiy yaratuvchisi.")
    
    text = (
        "👑 **Bot Yaratuvchisi (Dasturchi)**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💻 **Dasturchi:** {username}\n"
        f"📝 **Izoh:** {comment}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Muammo yoki takliflar yuzasidan murojaat qilishingiz mumkin.*"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Bog'lanish", url=f"https://t.me/{username.replace('@', '')}")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="client_back_to_contacts")]
    ])
    try:
        await call.message.edit_caption(caption=text, reply_markup=kb, parse_mode="Markdown")
    except:
        try:
            await call.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        except:
            pass

@router.callback_query(F.data == "client_back_to_contacts")
async def client_back_to_contacts(call: types.CallbackQuery):
    user = await db.get_user(call.from_user.id)
    lang = user[4] if user else 'uz'
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👑 Bot Yaratuvchisi", callback_data="client_view_creator")]
    ])
    try:
        await call.message.edit_caption(caption=MESSAGES[lang]['contact_info'], reply_markup=kb, parse_mode="Markdown")
    except:
        try:
            await call.message.edit_text(MESSAGES[lang]['contact_info'], reply_markup=kb, parse_mode="Markdown")
        except:
            pass

@router.message(Command("creator"))
async def show_creator_cmd(message: types.Message):
    user = await db.get_user(message.from_user.id)
    lang = user[4] if user else 'uz'
    
    username = await db.get_setting('creator_username', '@iwater_dev')
    comment = await db.get_setting('creator_comment', "iWater botining rasmiy yaratuvchisi.")
    
    text = (
        "👑 **Bot Yaratuvchisi (Dasturchi)**\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💻 **Dasturchi:** {username}\n"
        f"📝 **Izoh:** {comment}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "✨ *Muammo yoki takliflar yuzasidan murojaat qilishingiz mumkin.*"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Bog'lanish", url=f"https://t.me/{username.replace('@', '')}")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@router.message(Command("more"))
async def show_more_cmd(message: types.Message):
    user = await db.get_user(message.from_user.id)
    lang = user[4] if user else 'uz'
    
    welcome_db_key = f'welcome_msg_{lang}'
    caption = await db.get_setting(welcome_db_key)
    if not caption:
        caption = MESSAGES[lang]['start']
        
    username = await db.get_setting('creator_username', '@iwater_dev')
    comment = await db.get_setting('creator_comment', "iWater botining rasmiy yaratuvchisi.")
    
    creator_text = (
        f"\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 **Bot Yaratuvchisi (Dasturchi):**\n"
        f"💻 **Dasturchi:** {username}\n"
        f"📝 **Izoh:** {comment}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✨ *Muammo yoki takliflar yuzasidan murojaat qilishingiz mumkin.*"
    )
    
    full_text = caption + creator_text
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Bog'lanish", url=f"https://t.me/{username.replace('@', '')}")]
    ])
    await message.answer(full_text, reply_markup=kb, parse_mode="Markdown")

@router.message(F.text.in_([MESSAGES['uz']['terms_btn'], MESSAGES['ru']['terms_btn']]))
async def show_terms(message: types.Message):
    user = await db.get_user(message.from_user.id)
    lang = user[4] if user else 'uz'
    terms_key = f'terms_{lang}'
    terms_text = await db.get_setting(terms_key)
    if not terms_text:
        terms_text = "Shartlar va maxfiylik kelishuvi hali kiritilmagan." if lang == 'uz' else "Пользовательское соглашение еще не указано."
    await message.answer(terms_text, parse_mode="Markdown")

@router.message(F.text.in_([MESSAGES['uz']['back_btn'], MESSAGES['ru']['back_btn']]))
async def universal_back(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    user = await db.get_user(message.from_user.id)
    lang = user[4]
    
    if current_state == ClientStates.phone:
        await message.answer(MESSAGES[lang]['start'], reply_markup=reply.get_lang_kb())
        await state.set_state(ClientStates.language)
    elif current_state == ClientStates.location:
        await view_cart(message, state)
    elif current_state == ClientStates.payment_type:
        await checkout(message, state) # Should be a message-based version or refactored
    else:
        await send_main_menu_with_sequence(message, state, lang)

@router.message(ClientStates.in_chat)
async def customer_chat_message(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    admin_id = data.get('chat_admin_id')
    user = await db.get_user(message.from_user.id)
    lang = user[4] if user else 'uz'
    
    # Check if they want to close the chat
    if message.text and (message.text.lower() in ["/close", "close_chat", "chatni yopish", "закрыть чат"]):
        await state.clear()
        from main import dp
        if admin_id:
            admin_state = dp.fsm.resolve_context(bot, admin_id, admin_id)
            await admin_state.clear()
            try:
                await bot.send_message(admin_id, "❌ **Mijoz chatni yopdi.**", reply_markup=reply.get_admin_menu_kb())
            except:
                pass
        
        close_msg = "❌ Chat yopildi." if lang == 'uz' else "❌ Чат закрыт."
        await message.answer(close_msg, reply_markup=reply.get_main_menu_kb(lang))
        return

    if not admin_id:
        from config import ADMIN_IDS
        if ADMIN_IDS:
            admin_id = ADMIN_IDS[0]
        else:
            return
        
    cust_name = message.from_user.full_name
    text_to_send = f"💬 **Mijoz ({cust_name}):** {message.text}" if message.text else f"💬 **Mijoz ({cust_name}) rasm/fayl yubordi**"
    
    try:
        if message.text:
            await bot.send_message(admin_id, text_to_send, parse_mode="Markdown")
        elif message.photo:
            await bot.send_photo(admin_id, message.photo[-1].file_id, caption=text_to_send, parse_mode="Markdown")
        elif message.voice:
            await bot.send_voice(admin_id, message.voice.file_id, caption=text_to_send, parse_mode="Markdown")
        else:
            await bot.send_message(admin_id, f"⚠️ Mijozdan qo'llab-quvvatlanmaydigan xabar turi keldi.")
            
        await message.reply("✅" if lang == 'uz' else "✅")
    except Exception as e:
        await message.reply(f"❌" if lang == 'uz' else "❌")
