import re

with open("handlers/client.py", "r") as f:
    content = f.read()

old_notify = """    # Notify admins
    admin_messages = await db.get_order_messages(order_id)
    for admin_id, msg_id in admin_messages:
        try:
            await bot.send_message(admin_id, f"⚠️ YANGILANISH! Mijoz #{order_id:06d} buyurtmani tahrirladi:\\n\\nYangi miqdor: {items_text}\\nYangi summa: {new_total} so'm", reply_to_message_id=msg_id)
        except Exception:
            try:
                await bot.send_message(admin_id, f"⚠️ YANGILANISH! Mijoz #{order_id:06d} buyurtmani tahrirladi:\\n\\nYangi miqdor: {items_text}\\nYangi summa: {new_total} so'm")
            except Exception:
                pass"""

new_notify = """    # Rebuild admin message
    user_db = await db.get_user(order[1])
    recent_orders = await db.get_recent_active_orders(order[1], hours=2)
    linked_orders_text = ""
    if order_id in recent_orders:
        recent_orders.remove(order_id)
    if recent_orders:
        linked_ids_str = ", ".join([f"#{oid:06d}" for oid in recent_orders])
        linked_orders_text = f"\\n\\n🔗 **DIQQAT! Mijozning oxirgi 2 soat ichida yana {len(recent_orders)} ta faol buyurtmasi bor! Bularni birga yetkazish mumkin.**\\nBog'langan ID: {linked_ids_str}"

    username = user_db[1]
    profile_link = f"[@{username}](https://t.me/{username})" if username else f"[Lichka](tg://user?id={order[1]})"
    
    # Notify admins
    admin_messages = await db.get_order_messages(order_id)
    for admin_id, msg_id in admin_messages:
        try:
            if order[9] == 'cash':
                text = MESSAGES['uz']['new_order_admin'].format(
                    id=f"{order_id:06d}", name=user_db[2], profile_link=profile_link, phone=user_db[3],
                    quantity=new_qty, total=new_total, address=order[4], payment=order[9]
                ) + linked_orders_text
                await bot.edit_message_text(text, chat_id=admin_id, message_id=msg_id, reply_markup=inline.get_admin_order_kb(order_id), parse_mode="Markdown")
            else:
                text = MESSAGES['uz']['check_request_admin'].format(
                    id=f"{order_id:06d}", name=user_db[2], total=new_total
                ) + linked_orders_text
                await bot.edit_message_caption(chat_id=admin_id, message_id=msg_id, caption=text, reply_markup=inline.get_admin_order_kb(order_id, status='pending_payment'), parse_mode="Markdown")
                
            await bot.send_message(admin_id, f"⚠️ YANGILANISH! Mijoz #{order_id:06d} buyurtmani tahrirladi:\\n\\nYangi miqdor: {items_text}\\nYangi summa: {new_total} so'm", reply_to_message_id=msg_id)
        except Exception:
            try:
                await bot.send_message(admin_id, f"⚠️ YANGILANISH! Mijoz #{order_id:06d} buyurtmani tahrirladi:\\n\\nYangi miqdor: {items_text}\\nYangi summa: {new_total} so'm")
            except Exception:
                pass"""

content = content.replace(old_notify, new_notify)

with open("handlers/client.py", "w") as f:
    f.write(content)
