import os
import sys
from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from aiogram import Bot
from dotenv import load_dotenv

# Add project root to path to import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import db
from config import BOT_TOKEN, SUPER_ADMIN_ID

load_dotenv()

app = FastAPI(title="iWater Web Order System")
templates = Jinja2Templates(directory="web/templates")
bot = Bot(token=BOT_TOKEN)

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    site_status = await db.get_setting('web_site_status', '1')
    price = await db.get_setting('water_price', '15000')
    bot_user = await bot.get_me()
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "price": price, 
        "site_status": site_status,
        "bot_username": bot_user.username
    })

async def notify_admins_of_web_order(order_id: int, name: str, phone: str, quantity: int, total: int, address: str):
    from database.db import get_admins
    from config import SUPER_ADMIN_ID
    
    message_text = (
        f"🌐 **Veb-saytdan yangi buyurtma tushdi!**\n\n"
        f"🆔 Buyurtma raqami: #{order_id}\n"
        f"👤 Mijoz: {name}\n"
        f"📞 Tel: {phone}\n"
        f"📦 Miqdori: {quantity} dona\n"
        f"💰 Jami: {total} so'm\n"
        f"📍 Manzil: {address}\n"
        f"💳 To'lov: Naqd (Sayt orqali)"
    )
    
    # Inline keyboard for admins
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"order_accept_{order_id}")],
        [InlineKeyboardButton(text="❌ Rad etish", callback_data=f"order_reject_{order_id}")]
    ])

    admins = await get_admins()
    all_admin_ids = set(admins + [int(SUPER_ADMIN_ID)])

    for admin_id in all_admin_ids:
        try:
            await bot.send_message(admin_id, message_text, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

@app.post("/order")
async def create_web_order(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    phone: str = Form(...),
    quantity: int = Form(...),
    address: str = Form(...)
):
    site_status = await db.get_setting('web_site_status', '1')
    if site_status == '0':
        return {"status": "error", "message": "Website is in maintenance mode"}

    price_str = await db.get_setting('water_price', '15000')
    price = int(price_str)
    total = quantity * price
    
    # Create order in database
    order_id = await db.create_order(
        user_id=0, # 0 means from web
        items=f"{quantity} dona 19L (Web)",
        total_price=total,
        address=address,
        lat=0,
        lon=0
    )
    
    # Update payment type and name/phone for the record
    # Since db.py is built for TG users, we'll just handle the record update manually here or extend db.py
    # For now, let's just make sure the basic order is created.
    # In a real scenario, we might want a separate table for guest web orders or handle user_id=0 specially.
    
    background_tasks.add_task(notify_admins_of_web_order, order_id, name, phone, quantity, total, address)
    
    return {"status": "success", "order_id": order_id}
