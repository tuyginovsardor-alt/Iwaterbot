from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.strings import MESSAGES

def get_quantity_kb(quantity, price, lang):
    total = quantity * price
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data="dec"),
                InlineKeyboardButton(text=f"💧 {quantity}", callback_data="noop"),
                InlineKeyboardButton(text="➕", callback_data="inc")
            ],
            [InlineKeyboardButton(text=f"✅ {MESSAGES[lang]['added_to_cart']} ({total} so'm)", callback_data="add_to_cart")]
        ]
    )

def get_cart_kb(lang):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=MESSAGES[lang]['checkout_btn'], callback_data="checkout")],
            [InlineKeyboardButton(text=MESSAGES[lang]['clear_cart_btn'], callback_data="clear_cart")]
        ]
    )

def get_payment_kb(lang, manual_on=False):
    kb = [[InlineKeyboardButton(text=MESSAGES[lang]['payment_cash'], callback_data="pay_cash")]]
    if manual_on:
        kb.append([InlineKeyboardButton(text=MESSAGES[lang]['payment_card'], callback_data="pay_manual")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_order_kb(order_id, status='new', admin_name=None):
    if status == 'new':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Qabul qilish / Принять", callback_data=f"order_accept_{order_id}")],
                [InlineKeyboardButton(text="❌ Rad etish / Отказать", callback_data=f"order_reject_{order_id}")]
            ]
        )
    elif status == 'accepted':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"👨‍💻 {admin_name}", callback_data="noop")],
                [InlineKeyboardButton(text="🚚 Yo'lda / В пути", callback_data=f"order_way_{order_id}")],
                [InlineKeyboardButton(text="❌ Bekor qilish / Отмена", callback_data=f"order_reject_{order_id}")]
            ]
        )
    elif status == 'on_the_way':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"👨‍💻 {admin_name}", callback_data="noop")],
                [InlineKeyboardButton(text="🏁 Yetkazildi / Доставлено", callback_data=f"order_done_{order_id}")],
                [InlineKeyboardButton(text="❌ Bekor qilish / Отмена", callback_data=f"order_reject_{order_id}")]
            ]
        )
    elif status == 'pending_payment':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data=f"check_confirm_{order_id}")],
                [InlineKeyboardButton(text="❌ Chekni rad etish", callback_data=f"check_reject_{order_id}")]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"✅ {admin_name} yakunladi", callback_data="noop")]
            ]
        )

def get_admin_settings_kb(lang, manual_on=False, web_on=True):
    status_text = "✅ ON" if manual_on else "❌ OFF"
    web_status_text = "✅ ON" if web_on else "❌ OFF"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=MESSAGES[lang]['set_price_btn'], callback_data="set_price")],
            [InlineKeyboardButton(text=MESSAGES[lang]['toggle_payment_btn'].format(status=status_text), callback_data="toggle_payment")],
            [InlineKeyboardButton(text=MESSAGES[lang]['toggle_web_btn'].format(status=web_status_text), callback_data="toggle_web")],
            [InlineKeyboardButton(text=MESSAGES[lang]['admin_channels_btn'], callback_data="admin_channels")],
            [InlineKeyboardButton(text=MESSAGES[lang]['admin_images_btn'], callback_data="admin_images")],
            [InlineKeyboardButton(text=MESSAGES[lang]['admin_terms_btn'], callback_data="admin_terms")]
        ]
    )

def get_channels_kb(channels, lang):
    kb = []
    for ch in channels:
        kb.append([InlineKeyboardButton(text=f"📢 {ch[1]}", url=ch[2])])
    kb.append([InlineKeyboardButton(text=MESSAGES[lang]['sub_check_btn'], callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_admin_channels_list_kb(channels):
    kb = []
    for ch in channels:
        kb.append([InlineKeyboardButton(text=f"🗑 {ch[1]}", callback_data=f"del_channel_{ch[0]}")])
    kb.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    return InlineKeyboardMarkup(inline_keyboard=kb)
