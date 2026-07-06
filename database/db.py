import aiosqlite
import os

DB_PATH = "database/iwater.db"

async def init_db():
    if not os.path.exists("database"):
        os.makedirs("database")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                language TEXT DEFAULT 'uz',
                order_count INTEGER DEFAULT 0
            )
        """)
        
        # Orders table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                items TEXT,
                total_price INTEGER,
                address TEXT,
                latitude REAL,
                longitude REAL,
                status TEXT DEFAULT 'new',
                admin_id INTEGER,
                payment_type TEXT,
                payment_check_file_id TEXT,
                rejection_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Settings table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Initial settings
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('water_price', '15000')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('manual_payment_status', '0')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('web_site_status', '1')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('terms_uz', 'Rasmiy shartlar matni (UZ)')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('terms_ru', 'Официальный текст условий (RU)')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('welcome_msg_uz', '👋 Assalomu alaykum! **iWater** xizmatiga xush kelibsiz.\n✨ Toza va sifatli 19L suv yetkazib berish.\n\n👇 Davom etish uchun tilni tanlang:')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('welcome_msg_ru', '👋 Здравствуйте! Добро пожаловать в сервис **iWater**.\n✨ Доставка чистой и качественной 19л воды.\n\n👇 Для продолжения выберите язык:')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('warehouse_lat', '41.2995')")
        await db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('warehouse_lon', '69.2401')")
        
        # Channels table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS channels (
                id TEXT PRIMARY KEY,
                name TEXT,
                invite_link TEXT,
                is_mandatory INTEGER DEFAULT 1
            )
        """)

        # Start images table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS start_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT
            )
        """)
        
        await db.commit()

async def get_setting(key, default=None):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default

async def set_setting(key, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        await db.commit()

async def get_user_orders(user_id, limit=5):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", 
            (user_id, limit)
        ) as cursor:
            return await cursor.fetchall()

async def get_all_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM orders ORDER BY created_at DESC") as cursor:
            return await cursor.fetchall()

async def update_order_rejection(order_id, reason):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = 'rejected', rejection_reason = ? WHERE id = ?", (reason, order_id))
        await db.commit()

async def update_order_payment_check(order_id, file_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET payment_check_file_id = ?, status = 'pending_payment' WHERE id = ?", (file_id, order_id))
        await db.commit()

# Channel helpers
async def add_channel(channel_id, name, link, is_mandatory=1):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO channels (id, name, invite_link, is_mandatory) VALUES (?, ?, ?, ?)",
            (channel_id, name, link, is_mandatory)
        )
        await db.commit()

async def get_channels(mandatory_only=False):
    async with aiosqlite.connect(DB_PATH) as db:
        query = "SELECT * FROM channels"
        if mandatory_only:
            query += " WHERE is_mandatory = 1"
        async with db.execute(query) as cursor:
            return await cursor.fetchall()

async def delete_channel(channel_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        await db.commit()

# Image helpers
async def add_start_image(file_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO start_images (file_id) VALUES (?)", (file_id,))
        await db.commit()

async def get_start_images():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT file_id FROM start_images") as cursor:
            return [row[0] for row in await cursor.fetchall()]

async def clear_start_images():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM start_images")
        await db.commit()

async def add_user(user_id, username, full_name, language):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name, language) VALUES (?, ?, ?, ?)",
            (user_id, username, full_name, language)
        )
        await db.commit()

async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_language(user_id, language):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()

async def update_user_phone(user_id, phone):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        await db.commit()

async def create_order(user_id, items, total_price, address, lat, lon):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO orders (user_id, items, total_price, address, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, items, total_price, address, lat, lon)
        )
        order_id = cursor.lastrowid
        await db.commit()
        return order_id

async def update_order_status(order_id, status, admin_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ?, admin_id = ? WHERE id = ?", (status, admin_id, order_id))
        await db.commit()

async def get_order(order_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)) as cursor:
            return await cursor.fetchone()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM orders") as cursor:
            total_orders = (await cursor.fetchone())[0]
        return total_users, total_orders

async def increment_order_count(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET order_count = order_count + 1 WHERE user_id = ?", (user_id,))
        await db.commit()

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            return await cursor.fetchall()

async def get_admins():
    from config import ADMIN_IDS
    return ADMIN_IDS
