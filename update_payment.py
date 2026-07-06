import re

with open("handlers/client.py", "r") as f:
    content = f.read()

# Cash payment
old_cash = """    final_msg = (bonus_text + "\n\n" if bonus_text else "") + MESSAGES[lang]['order_received'].format(id=f"{order_id:06d}")
    await call.message.answer(final_msg, reply_markup=reply.get_main_menu_kb(lang), parse_mode="Markdown")"""

new_cash = """    final_msg = (bonus_text + "\n\n" if bonus_text else "") + MESSAGES[lang]['order_received'].format(id=f"{order_id:06d}")
    await call.message.answer(final_msg, reply_markup=inline.get_order_client_kb(order_id, lang), parse_mode="Markdown")
    await call.message.answer(MESSAGES[lang]['main_menu'], reply_markup=reply.get_main_menu_kb(lang))"""

content = content.replace(old_cash, new_cash)

# Manual payment
old_manual = """    await message.answer(MESSAGES[lang]['check_received'], reply_markup=reply.get_main_menu_kb(lang), parse_mode="Markdown")"""

new_manual = """    await message.answer(MESSAGES[lang]['check_received'], reply_markup=inline.get_order_client_kb(order_id, lang), parse_mode="Markdown")
    await message.answer(MESSAGES[lang]['main_menu'], reply_markup=reply.get_main_menu_kb(lang))"""

content = content.replace(old_manual, new_manual)

with open("handlers/client.py", "w") as f:
    f.write(content)
