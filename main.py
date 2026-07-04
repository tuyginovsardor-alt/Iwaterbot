import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database import db
from handlers import client, admin
from middlewares.throttling import ThrottlingMiddleware

# Setup logging
logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize database
    await db.init_db()
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Register middleware
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    
    # Register routers
    dp.include_router(admin.router)
    dp.include_router(client.router)
    
    # Start polling
    logging.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
