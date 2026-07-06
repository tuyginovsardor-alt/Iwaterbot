from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from locales.strings import MESSAGES

def get_lang_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )

def get_phone_kb(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES[lang]['phone_btn'], request_contact=True)]
        ],
        resize_keyboard=True
    )

def get_main_menu_kb(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES[lang]['order_btn'])],
            [KeyboardButton(text=MESSAGES[lang]['cart_btn']), KeyboardButton(text=MESSAGES[lang]['history_btn'])],
            [KeyboardButton(text=MESSAGES[lang]['settings_btn']), KeyboardButton(text=MESSAGES[lang]['terms_btn'])],
            [KeyboardButton(text=MESSAGES[lang]['contact_btn'])]
        ],
        resize_keyboard=True
    )

def get_location_kb(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES[lang]['location_btn'], request_location=True)],
            [KeyboardButton(text=MESSAGES[lang]['back_btn'])]
        ],
        resize_keyboard=True
    )

def get_admin_menu_kb(lang='uz'):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES[lang]['stats_btn']), KeyboardButton(text=MESSAGES[lang]['mailing_btn'])],
            [KeyboardButton(text=MESSAGES[lang]['admin_settings_btn']), KeyboardButton(text=MESSAGES[lang]['admin_search_order_btn'])],
            [KeyboardButton(text="⬅️ Mijoz menyusi")]
        ],
        resize_keyboard=True
    )
