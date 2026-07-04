# 🪐 iWater — Advanced Telegram Bot & FastAPI Web System

[O'zbek tilidagi qo'llanma](#uz-ozbekcha) | [English Guide](#en-english)

---

<a name="uz-ozbekcha"></a>
## 🇺🇿 O'zbekcha

**iWater** — bu 19 litrlik toza ichimlik suvi yetkazib berish biznesini avtomatlashtirish uchun mo'ljallangan mukammal tizim. U o'z ichiga Telegram bot (Mijozlar va Adminlar uchun) hamda zamonaviy Veb-saytni (Landing page) oladi.

### ✨ Asosiy Imkoniyatlar:
- 🛒 **Savat Tizimi**: Foydalanuvchilar Telegram bot yoki Veb-sayt orqali buyurtma bera oladilar.
- 🌐 **FastAPI Web**: Zamonaviy, tezkor va mobil qurilmalarga moslangan Landing sahifa.
- ⚙️ **Admin Panel**: Narxlarni o'zgartirish, bot sozlamalari, kanallarni boshqarish va statistika.
- 💳 **To'lov Turlari**: Naqd pul yoki Karta orqali (chek yuborish tizimi bilan).
- 📍 **Geolokatsiya**: Mijoz manzili va masofani hisoblash (Haversine).
- 📢 **Majburiy Obuna**: Botdan foydalanish uchun kanallarga a'zo bo'lishni talab qilish.
- ⏰ **Eslatmalar**: Tashlab ketilgan savat haqida avtomatik bildirishnomalar.
- 📊 **Eksport**: Barcha ma'lumotlarni Excel formatida yuklab olish.

### 🚀 Serverga o'rnatish:
1. Repozitoriyani yuklab oling:
   ```bash
   git clone https://github.com/USER_NAME/Iwaterbot.git
   cd Iwaterbot
   ```
2. O'rnatish skriptini ishga tushiring:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Skript so'ragan ma'lumotlarni (`BOT_TOKEN`, `SUPER_ADMIN_ID`, `DOMAIN`) kiriting.

---

<a name="en-english"></a>
## 🇺🇿 English

**iWater** — is a complete automation system for 19L drinking water delivery businesses. It features a powerful Telegram bot (for Customers and Admins) and a modern FastAPI-based Landing Page.

### ✨ Key Features:
- 🛒 **Cart System**: Multi-platform ordering via Telegram or Web.
- 🌐 **FastAPI Web**: Modern, responsive landing page with direct order integration.
- ⚙️ **Admin Dashboard**: Real-time price updates, system settings, channel management, and analytics.
- 💳 **Flexible Payment**: Cash on delivery or manual card payment with receipt verification.
- 📍 **Geolocation**: Precise delivery tracking and distance calculation.
- 📢 **Subscription Lock**: Mandatory channel join requirement for users.
- ⏰ **Smart Reminders**: Automated abandoned cart notifications.
- 📊 **Data Export**: Professional reporting in Excel format.

### 🚀 Installation Guide:
1. Clone the repository:
   ```bash
   git clone https://github.com/USER_NAME/Iwaterbot.git
   cd Iwaterbot
   ```
2. Run the automated setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
3. Provide the required credentials (`BOT_TOKEN`, `SUPER_ADMIN_ID`, `DOMAIN`) when prompted.

---
*Developed with ❤️ for iWater Delivery*
