import re

with open("handlers/client.py", "r") as f:
    content = f.read()

old_notify_cash = """        try:
            await bot.send_message(
                admin_id,
                MESSAGES['uz']['new_order_admin'].format(
                    id=f"{order_id:06d}", name=user[2], profile_link=profile_link, phone=user[3],
                    quantity=quantity, total=total, address=data['order_address'], payment=payment_type
                ) + f"\n\n{data.get('dist_info', '')}" + linked_orders_text,
                reply_markup=inline.get_admin_order_kb(order_id),
                parse_mode="Markdown"
            )
        except Exception:
            pass"""

new_notify_cash = """        try:
            sent_msg = await bot.send_message(
                admin_id,
                MESSAGES['uz']['new_order_admin'].format(
                    id=f"{order_id:06d}", name=user[2], profile_link=profile_link, phone=user[3],
                    quantity=quantity, total=total, address=data['order_address'], payment=payment_type
                ) + f"\n\n{data.get('dist_info', '')}" + linked_orders_text,
                reply_markup=inline.get_admin_order_kb(order_id),
                parse_mode="Markdown"
            )
            await db.save_order_message(order_id, admin_id, sent_msg.message_id)
        except Exception as e:
            print(f"Error sending to admin {admin_id}: {e}")
            pass"""

content = content.replace(old_notify_cash, new_notify_cash)

old_notify_manual = """        try:
            await bot.send_photo(
                admin_id, file_id,
                caption=MESSAGES['uz']['check_request_admin'].format(id=f"{order_id:06d}", name=user[2], total=total) + linked_orders_text,
                reply_markup=inline.get_admin_order_kb(order_id, status='pending_payment'),
                parse_mode="Markdown"
            )
        except Exception:
            pass"""

new_notify_manual = """        try:
            sent_msg = await bot.send_photo(
                admin_id, file_id,
                caption=MESSAGES['uz']['check_request_admin'].format(id=f"{order_id:06d}", name=user[2], total=total) + linked_orders_text,
                reply_markup=inline.get_admin_order_kb(order_id, status='pending_payment'),
                parse_mode="Markdown"
            )
            await db.save_order_message(order_id, admin_id, sent_msg.message_id)
        except Exception:
            pass"""

content = content.replace(old_notify_manual, new_notify_manual)

with open("handlers/client.py", "w") as f:
    f.write(content)
