import re

with open("handlers/client.py", "r") as f:
    content = f.read()

replacement = """async def checkout(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    
    # 1-hour order limit
    from datetime import datetime
    last_order_str = await db.get_last_order_time(call.from_user.id)
    if last_order_str:
        # Expected format: "2023-10-27 10:20:30"
        try:
            last_order = datetime.strptime(last_order_str, "%Y-%m-%d %H:%M:%S")
            diff = (datetime.utcnow() - last_order).total_seconds()
            if diff < 3600:
                mins_left = int((3600 - diff) // 60)
                msg = f"⏳ Kechirasiz, siz yana {mins_left} daqiqadan keyin yangi buyurtma bera olasiz." if lang == 'uz' else f"⏳ Извините, вы сможете сделать новый заказ через {mins_left} минут."
                await call.answer(msg, show_alert=True)
                return
        except Exception as e:
            pass
            
    await call.message.delete()"""

content = content.replace("""async def checkout(call: types.CallbackQuery, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    lang = user[4]
    await call.message.delete()""", replacement)

with open("handlers/client.py", "w") as f:
    f.write(content)
