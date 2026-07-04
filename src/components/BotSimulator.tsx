import React, { useState, useEffect, useRef } from 'react';
import { Send, Smartphone, MapPin, CheckCircle, Info, Trash2, Camera, AlertTriangle } from 'lucide-react';
import { Settings, Channel } from '../types';

interface Message {
  id: number;
  sender: 'bot' | 'user';
  text: string;
  isPhoto?: boolean;
  photoUrl?: string;
  isLocation?: boolean;
  inlineButtons?: { text: string; action: string }[][];
}

interface BotSimulatorProps {
  settings: Settings;
  onOrderSuccess: () => void;
}

export default function BotSimulator({ settings, onOrderSuccess }: BotSimulatorProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [fsmState, setFsmState] = useState<'language' | 'phone' | 'main_menu' | 'select_qty' | 'location' | 'payment' | 'upload_check'>('language');
  const [lang, setLang] = useState<'uz' | 'ru'>('uz');
  const [userPhone, setUserPhone] = useState('');
  const [userOrdersCount, setUserOrdersCount] = useState(0);
  
  // Cart state
  const [cartQuantity, setCartQuantity] = useState(0);
  const [tempQuantity, setTempQuantity] = useState(1);
  const [orderAddress, setOrderAddress] = useState('');
  const [orderLat, setOrderLat] = useState(0);
  const [orderLon, setOrderLon] = useState(0);
  const [distInfo, setDistInfo] = useState('');

  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const price = parseInt(settings.water_price || '15000', 10);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initial greeting
  useEffect(() => {
    setMessages([
      {
        id: 1,
        sender: 'bot',
        text: "👋 Assalomu alaykum! **iWater** xizmatiga xush kelibsiz.\n✨ Toza va sifatli 19L suv yetkazib berish.\n\n👇 Davom etish uchun tilni tanlang:\n\n---\n\n👋 Здравствуйте! Добро пожаловать в сервис **iWater**.\n✨ Доставка чистой и качественной 19л воды.\n\n👇 Для продолжения выберите язык:"
      }
    ]);
  }, []);

  // Helper: bot replies with custom typing delay
  const botReply = (text: string, options?: Partial<Message>) => {
    setTimeout(() => {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          sender: 'bot',
          text,
          ...options
        }
      ]);
    }, 500);
  };

  const handleLanguageSelect = (selectedLang: 'uz' | 'ru') => {
    setLang(selectedLang);
    setMessages(prev => [
      ...prev,
      { id: Date.now(), sender: 'user', text: selectedLang === 'uz' ? "🇺🇿 O'zbekcha" : "🇷🇺 Русский" }
    ]);

    const greeting = selectedLang === 'uz' 
      ? "📱 Iltimos, **telefon raqamingizni** yuboring yoki quyidagi formatda yozing:\n`+998XXXXXXXXX`"
      : "📱 Пожалуйста, отправьте ваш **номер телефона** или напишите в формате:\n`+998XXXXXXXXX`";

    setFsmState('phone');
    botReply(greeting);
  };

  const handlePhoneSubmit = (phone: string) => {
    // Validate format
    const cleaned = phone.replace(/\s+/g, '');
    const phoneRegex = /^\+998\d{9}$/;
    if (!phoneRegex.test(cleaned)) {
      const errorMsg = lang === 'uz'
        ? "❌ Noto'g'ri format! Iltimos, raqamni quyidagicha yuboring: `+998901234567`"
        : "❌ Неверный формат! Пожалуйста, отправьте номер так: `+998901234567`";
      setMessages(prev => [
        ...prev,
        { id: Date.now(), sender: 'user', text: phone }
      ]);
      botReply(errorMsg);
      return;
    }

    setUserPhone(cleaned);
    setMessages(prev => [
      ...prev,
      { id: Date.now(), sender: 'user', text: cleaned }
    ]);

    const mainMenuMsg = lang === 'uz'
      ? "🏠 **Asosiy menyu**\nSizga qanday yordam bera olamiz?"
      : "🏠 **Главное меню**\nЧем мы можем вам помочь?";

    setFsmState('main_menu');
    botReply(mainMenuMsg);
  };

  const handleMainMenuAction = (action: string) => {
    const textUZ = {
      order: "💧 Suv buyurtma qilish",
      cart: "🛒 Savat",
      history: "📜 Buyurtmalarim",
      settings: "👤 Profil va Sozlamalar",
      terms: "📜 Shartlar va Maxfiylik",
      contact: "📞 Biz bilan aloqa"
    };
    const textRU = {
      order: "💧 Заказать воду",
      cart: "🛒 Корзина",
      history: "📜 Мои заказы",
      settings: "👤 Профиль и Настройки",
      terms: "📜 Условия и Конфиденциальность",
      contact: "📞 Контакты"
    };

    const displayText = lang === 'uz' ? textUZ[action as keyof typeof textUZ] : textRU[action as keyof typeof textRU];

    setMessages(prev => [
      ...prev,
      { id: Date.now(), sender: 'user', text: displayText }
    ]);

    if (action === 'order') {
      setTempQuantity(1);
      setFsmState('select_qty');
      const text = lang === 'uz'
        ? `🔢 Miqdorni tanlang:\n💰 Narxi: **${price}** so'm`
        : `🔢 Выберите количество:\n💰 Цена: **${price}** сум`;
      
      botReply(text, {
        inlineButtons: [
          [
            { text: '➖', action: 'qty_dec' },
            { text: `💧 ${tempQuantity}`, action: 'qty_noop' },
            { text: '➕', action: 'qty_inc' }
          ],
          [{ text: lang === 'uz' ? `✅ Savatga qo'shish (${price} so'm)` : `✅ Добавить в корзину (${price} сум)`, action: 'qty_add' }]
        ]
      });
    } else if (action === 'cart') {
      if (cartQuantity === 0) {
        const text = lang === 'uz' ? "📭 Savatingiz hozircha bo'sh." : "📭 Ваша корзина пока пуста.";
        botReply(text);
      } else {
        const total = cartQuantity * price;
        const text = lang === 'uz'
          ? `🛒 **Savat tarkibi:**\n\n📦 Mahsulot: 19L Suv\n🔢 Miqdori: ${cartQuantity} dona\n💰 Umumiy: **${total.toLocaleString()} so'm**\n\n👇 Davom etish uchun quyidagilardan birini tanlang:`
          : `🛒 **Состав корзины:**\n\n📦 Продукт: 19л Вода\n🔢 Кол-во: ${cartQuantity} шт.\n💰 Итого: **${total.toLocaleString()} сум**\n\n👇 Выберите действие:`;
        
        botReply(text, {
          inlineButtons: [
            [{ text: lang === 'uz' ? "🚀 Buyurtma berish" : "🚀 Оформить заказ", action: 'cart_checkout' }],
            [{ text: lang === 'uz' ? "🗑 Savatni tozalash" : "🗑 Очистить корзину", action: 'cart_clear' }]
          ]
        });
      }
    } else if (action === 'history') {
      const text = lang === 'uz'
        ? "📜 **Sizning oxirgi buyurtmalaringiz:**\n\nHozirgi buyurtmalarni o'ngdagi Admin panelda ko'rishingiz mumkin!"
        : "📜 **Ваши последние заказы:**\n\nТекущие заказы можно просмотреть на панели администратора справа!";
      botReply(text);
    } else if (action === 'settings') {
      const text = lang === 'uz'
        ? `👤 **Sizning profilingiz:**\n\n🆔 ID: \`69420817\`\n📞 Tel: \`${userPhone || "Noma'lum"}\`\n🏆 Buyurtmalar soni: ${userOrdersCount}\n🎁 *Har 10-buyurtmada maxsus chegirmaga ega bo'lasiz!*`
        : `👤 **Ваш профиль:**\n\n🆔 ID: \`69420817\`\n📞 Тел: \`${userPhone || "Неизвестно"}\`\n🏆 Кол-во заказов: ${userOrdersCount}\n🎁 *Каждый 10-й заказ со скидкой!*`;
      botReply(text);
    } else if (action === 'terms') {
      const text = lang === 'uz' ? settings.terms_uz : settings.terms_ru;
      botReply(text);
    } else if (action === 'contact') {
      const text = lang === 'uz'
        ? "📞 **Biz bilan bog'lanish:**\n\n🏢 Markaziy ofis: Toshkent sh., Chilonzor\n☎️ Call-markaz: +998 (71) 123-45-67\n⏰ Ish vaqti: 08:00 - 22:00"
        : "📞 **Связаться с нами:**\n\n🏢 Офис: г. Ташкент, Чиланзар\n☎️ Колл-центр: +998 (71) 123-45-67\n⏰ Время работы: 08:00 - 22:00";
      botReply(text);
    }
  };

  const handleInlineAction = (action: string) => {
    if (action === 'qty_noop') return;

    if (action === 'qty_inc') {
      const newQty = tempQuantity + 1;
      setTempQuantity(newQty);
      
      // Update the last bot message inline buttons and text
      setMessages(prev => {
        const copy = [...prev];
        const lastBotIdx = copy.map(m => m.sender === 'bot').lastIndexOf(true);
        if (lastBotIdx !== -1) {
          copy[lastBotIdx].text = lang === 'uz'
            ? `🔢 Miqdorni tanlang:\n💰 Narxi: **${(newQty * price).toLocaleString()}** so'm`
            : `🔢 Выберите количество:\n💰 Цена: **${(newQty * price).toLocaleString()}** сум`;
          copy[lastBotIdx].inlineButtons = [
            [
              { text: '➖', action: 'qty_dec' },
              { text: `💧 ${newQty}`, action: 'qty_noop' },
              { text: '➕', action: 'qty_inc' }
            ],
            [{ text: lang === 'uz' ? `✅ Savatga qo'shish (${(newQty * price).toLocaleString()} so'm)` : `✅ Добавить в корзину (${(newQty * price).toLocaleString()} сум)`, action: 'qty_add' }]
          ];
        }
        return copy;
      });
    } else if (action === 'qty_dec') {
      if (tempQuantity <= 1) return;
      const newQty = tempQuantity - 1;
      setTempQuantity(newQty);
      
      setMessages(prev => {
        const copy = [...prev];
        const lastBotIdx = copy.map(m => m.sender === 'bot').lastIndexOf(true);
        if (lastBotIdx !== -1) {
          copy[lastBotIdx].text = lang === 'uz'
            ? `🔢 Miqdorni tanlang:\n💰 Narxi: **${(newQty * price).toLocaleString()}** so'm`
            : `🔢 Выберите количество:\n💰 Цена: **${(newQty * price).toLocaleString()}** сум`;
          copy[lastBotIdx].inlineButtons = [
            [
              { text: '➖', action: 'qty_dec' },
              { text: `💧 ${newQty}`, action: 'qty_noop' },
              { text: '➕', action: 'qty_inc' }
            ],
            [{ text: lang === 'uz' ? `✅ Savatga qo'shish (${(newQty * price).toLocaleString()} so'm)` : `✅ Добавить в корзину (${(newQty * price).toLocaleString()} сум)`, action: 'qty_add' }]
          ];
        }
        return copy;
      });
    } else if (action === 'qty_add') {
      setCartQuantity(tempQuantity);
      setFsmState('main_menu');
      
      const successText = lang === 'uz'
        ? "✅ Savatga qo'shildi!\n\nAsosiy menyuga qaytdik."
        : "✅ Добавлено в корзину!\n\nВозвращаемся в главное меню.";
      botReply(successText);
    } else if (action === 'cart_clear') {
      setCartQuantity(0);
      setFsmState('main_menu');
      const text = lang === 'uz' ? "🗑 Savat muvaffaqiyatli tozalandi!" : "🗑 Корзина успешно очищена!";
      botReply(text);
    } else if (action === 'cart_checkout') {
      setFsmState('location');
      const text = lang === 'uz'
        ? "📍 Buyurtma qayerga yetkazilsin?\n\nIltimos, **geolokatsiyangizni** yuboring yoki manzilni matn ko'rinishida yozing:"
        : "📍 Куда доставить заказ?\n\nПожалуйста, отправьте вашу **геолокацию** или напишите адрес текстом:";
      botReply(text);
    }
  };

  const handleLocationSubmit = (addressStr: string, isGeo = false) => {
    setMessages(prev => [
      ...prev,
      { id: Date.now(), sender: 'user', text: isGeo ? "📍 Geolokatsiyani ulashdi" : addressStr }
    ]);

    setOrderAddress(addressStr);
    
    let dist = '';
    if (isGeo) {
      setOrderLat(41.2845);
      setOrderLon(69.2134);
      const randDist = (Math.random() * 8 + 1).toFixed(1);
      const randTime = Math.floor(Number(randDist) * 5 + 15);
      dist = lang === 'uz'
        ? `📍 Ombordan masofa: **${randDist} km**\n🕒 Taxminiy yetkazish vaqti: **${randTime} daqiqa**`
        : `📍 Расстояние со склада: **${randDist} км**\n🕒 Примерное время доставки: **${randTime} минут**`;
      setDistInfo(dist);
    } else {
      setOrderLat(0);
      setOrderLon(0);
      setDistInfo('');
    }

    setFsmState('payment');
    
    const paymentText = lang === 'uz' ? "💳 To'lov turini tanlang:" : "💳 Выберите тип оплаты:";
    const hasManual = settings.manual_payment_status === '1';

    const inlineButtons = [
      [{ text: lang === 'uz' ? "💵 Naqd pul" : "💵 Наличные", action: 'pay_cash' }]
    ];
    if (hasManual) {
      inlineButtons.push([{ text: lang === 'uz' ? "💳 Karta orqali (Chek yuborish)" : "💳 Картой (Отправить чек)", action: 'pay_card' }]);
    }

    botReply((dist ? dist + "\n\n" : "") + paymentText, { inlineButtons });
  };

  const handlePaymentSelect = (type: 'cash' | 'card') => {
    setMessages(prev => [
      ...prev,
      { id: Date.now(), sender: 'user', text: type === 'cash' ? (lang === 'uz' ? "💵 Naqd pul" : "💵 Наличные") : (lang === 'uz' ? "💳 Karta orqali" : "💳 Картой") }
    ]);

    const total = cartQuantity * price;

    if (type === 'card') {
      setFsmState('upload_check');
      const text = lang === 'uz'
        ? `💳 To'lov qilish uchun karta raqami:\n\`8600 0000 0000 0000\` (iWater MCHJ)\n\nIltimos, **${total.toLocaleString()}** so'm o'tkazib, to'lov chekini (rasmini) shu yerga yuboring:`
        : `💳 Номер карты для оплаты:\n\`8600 0000 0000 0000\` (ООО iWater)\n\nПожалуйста, переведите **${total.toLocaleString()}** сум и отправьте фото чека (скриншот) сюда:`;
      botReply(text);
    } else {
      // Create Cash Order
      createSimulatedOrder('Naqd');
    }
  };

  const handleCheckUpload = () => {
    // Replicate check receiving
    setMessages(prev => [
      ...prev,
      { 
        id: Date.now(), 
        sender: 'user', 
        text: 'Sent receipt image', 
        isPhoto: true, 
        photoUrl: 'https://images.unsplash.com/photo-1554415707-6e8cfc93fe23?q=80&w=300&auto=format&fit=crop' 
      }
    ]);

    const text = lang === 'uz'
      ? "✅ Chek qabul qilindi. Operator tasdiqlashini kuting."
      : "✅ Чек получен. Ожидайте подтверждения оператора.";
    
    botReply(text);
    createSimulatedOrder('Karta (Manual)', 'https://images.unsplash.com/photo-1554415707-6e8cfc93fe23?q=80&w=300&auto=format&fit=crop');
  };

  const createSimulatedOrder = async (paymentType: string, checkUrl?: string) => {
    const total = cartQuantity * price;
    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 69420817, // Static TG user ID
          username: 'tg_customer',
          full_name: 'Simulated TG Client',
          phone: userPhone || '+998901234567',
          items: `${cartQuantity} dona 19L (Bot)`,
          total_price: total,
          address: orderAddress || '📍 Toshkent, Yunusobod',
          latitude: orderLat,
          longitude: orderLon,
          status: paymentType.includes('Karta') ? 'pending_payment' : 'new',
          payment_type: paymentType,
          payment_check_file_id: checkUrl
        })
      });

      const result = await response.json();
      if (result.success) {
        setUserOrdersCount(prev => prev + 1);
        setCartQuantity(0);
        setFsmState('main_menu');
        
        if (!paymentType.includes('Karta')) {
          const successMsg = lang === 'uz'
            ? `🎉 **Rahmat! Buyurtmangiz qabul qilindi.**\n🆔 Buyurtma raqami: #${result.order.id}\n\nOperatorlarimiz tez orada siz bilan bog'lanishadi. 🕒`
            : `🎉 **Спасибо! Ваш заказ принят.**\n🆔 Номер заказа: #${result.order.id}\n\nНаши операторы свяжутся с вами в ближайшее время. 🕒`;
          botReply(successMsg);
        }
        onOrderSuccess();
      }
    } catch (err) {
      console.error('Failed to create bot order:', err);
    }
  };

  const handleSendText = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const val = inputText.trim();
    setInputText('');

    if (fsmState === 'phone') {
      handlePhoneSubmit(val);
    } else if (fsmState === 'location') {
      handleLocationSubmit(val, false);
    } else {
      // Standard message fallback or menu clicks typed in
      setMessages(prev => [
        ...prev,
        { id: Date.now(), sender: 'user', text: val }
      ]);
      
      const lowercase = val.toLowerCase();
      if (lowercase.includes('buyurtma') || lowercase.includes('заказ')) {
        handleMainMenuAction('order');
      } else if (lowercase.includes('savat') || lowercase.includes('корзин')) {
        handleMainMenuAction('cart');
      } else {
        const text = lang === 'uz'
          ? "Iltimos, quyidagi tugmalardan birini tanlang yoki buyurtma bering."
          : "Пожалуйста, используйте кнопки ниже для взаимодействия.";
        botReply(text);
      }
    }
  };

  return (
    <div className="bg-[#0f111a] rounded-3xl border border-zinc-800 shadow-2xl h-[650px] flex flex-col overflow-hidden max-w-md mx-auto">
      {/* Bot Header (Telegram Mock) */}
      <div className="bg-[#17212b] px-4 py-3 flex items-center gap-3 border-b border-zinc-800">
        <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-extrabold shadow-md">
          💧
        </div>
        <div>
          <h3 className="font-bold text-white text-sm">iWater Delivery Bot</h3>
          <p className="text-xs text-blue-400">bot • online</p>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#0e1621] scrollbar-thin scrollbar-thumb-zinc-800">
        {messages.map(m => (
          <div key={m.id} className={`flex ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-3.5 shadow-md text-sm ${
              m.sender === 'user' 
                ? 'bg-[#2b5278] text-white rounded-tr-none' 
                : 'bg-[#182533] text-zinc-100 rounded-tl-none border border-zinc-800'
            }`}>
              {m.isPhoto && m.photoUrl ? (
                <div className="space-y-2">
                  <img src={m.photoUrl} alt="Check" className="rounded-lg max-h-[160px] object-cover" />
                  <p className="text-xs text-zinc-400 italic">{m.text}</p>
                </div>
              ) : (
                <p className="whitespace-pre-line leading-relaxed">{m.text}</p>
              )}

              {/* Inline Buttons */}
              {m.inlineButtons && m.inlineButtons.length > 0 && (
                <div className="mt-3 space-y-1.5 border-t border-zinc-800/50 pt-2">
                  {m.inlineButtons.map((row, rIdx) => (
                    <div key={rIdx} className="flex gap-1.5 justify-center">
                      {row.map((btn, bIdx) => (
                        <button
                          key={bIdx}
                          onClick={() => handleInlineAction(btn.action)}
                          className="flex-1 bg-[#243647] hover:bg-[#2b3f52] active:scale-95 text-blue-400 py-2 px-3 rounded-lg text-xs font-bold transition-all border border-blue-500/10"
                        >
                          {btn.text}
                        </button>
                      ))}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Interactive Controls/Keyboard section */}
      <div className="bg-[#17212b] p-3 border-t border-zinc-800 space-y-3">
        {/* State Keyboard Buttons */}
        <div className="grid grid-cols-2 gap-2">
          {fsmState === 'language' && (
            <>
              <button
                onClick={() => handleLanguageSelect('uz')}
                className="bg-[#24303f] hover:bg-[#2e3b4e] text-white py-3 px-4 rounded-xl text-xs font-bold transition-all border border-zinc-800"
              >
                🇺🇿 O'zbekcha
              </button>
              <button
                onClick={() => handleLanguageSelect('ru')}
                className="bg-[#24303f] hover:bg-[#2e3b4e] text-white py-3 px-4 rounded-xl text-xs font-bold transition-all border border-zinc-800"
              >
                🇷🇺 Русский
              </button>
            </>
          )}

          {fsmState === 'phone' && (
            <button
              onClick={() => handlePhoneSubmit('+998901234567')}
              className="col-span-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
            >
              <Smartphone className="w-4 h-4" />
              {lang === 'uz' ? "📲 Raqamni ulashish (+998 90 123 45 67)" : "📲 Поделиться номером (+998 90 123 45 67)"}
            </button>
          )}

          {fsmState === 'main_menu' && (
            <div className="col-span-2 grid grid-cols-2 gap-2">
              <button
                onClick={() => handleMainMenuAction('order')}
                className="col-span-2 bg-[#202b36] hover:bg-[#293745] text-white py-2.5 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                💧 {lang === 'uz' ? "Suv buyurtma qilish" : "Заказать воду"}
              </button>
              <button
                onClick={() => handleMainMenuAction('cart')}
                className="bg-[#202b36] hover:bg-[#293745] text-white py-2.5 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                🛒 {lang === 'uz' ? "Savat" : "Корзина"} {cartQuantity > 0 ? `(${cartQuantity})` : ''}
              </button>
              <button
                onClick={() => handleMainMenuAction('history')}
                className="bg-[#202b36] hover:bg-[#293745] text-white py-2.5 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                📜 {lang === 'uz' ? "Buyurtmalarim" : "Мои заказы"}
              </button>
              <button
                onClick={() => handleMainMenuAction('settings')}
                className="bg-[#202b36] hover:bg-[#293745] text-white py-2.5 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                👤 {lang === 'uz' ? "Profil" : "Профиль"}
              </button>
              <button
                onClick={() => handleMainMenuAction('terms')}
                className="bg-[#202b36] hover:bg-[#293745] text-white py-2.5 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                📜 {lang === 'uz' ? "Shartlar" : "Условия"}
              </button>
              <button
                onClick={() => handleMainMenuAction('contact')}
                className="col-span-2 bg-[#202b36] hover:bg-[#293745] text-white py-2 px-3 rounded-xl text-xs font-semibold transition-all border border-zinc-800"
              >
                📞 {lang === 'uz' ? "Biz bilan aloqa" : "Контакты"}
              </button>
            </div>
          )}

          {fsmState === 'location' && (
            <>
              <button
                onClick={() => handleLocationSubmit('Toshkent sh., Chilonzor 12-daha', true)}
                className="bg-[#202b36] hover:bg-[#293745] text-white py-3 px-4 rounded-xl text-xs font-bold transition-all border border-zinc-800 flex items-center justify-center gap-1.5"
              >
                <MapPin className="w-3.5 h-3.5 text-blue-400" />
                📍 {lang === 'uz' ? "Lokatsiyani yuborish" : "Отправить гео"}
              </button>
              <button
                onClick={() => {
                  setFsmState('main_menu');
                  botReply(lang === 'uz' ? "Asosiy menyu" : "Главное меню");
                }}
                className="bg-[#24303f] hover:bg-[#2e3b4e] text-zinc-300 py-3 px-4 rounded-xl text-xs font-bold transition-all border border-zinc-800"
              >
                ⬅️ {lang === 'uz' ? "Orqaga" : "Назад"}
              </button>
            </>
          )}

          {fsmState === 'payment' && (
            <>
              <button
                onClick={() => handlePaymentSelect('cash')}
                className="bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 py-3 px-4 rounded-xl text-xs font-bold transition-all border border-emerald-500/15"
              >
                💵 {lang === 'uz' ? "Naqd pul" : "Наличные"}
              </button>
              {settings.manual_payment_status === '1' && (
                <button
                  onClick={() => handlePaymentSelect('card')}
                  className="bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 py-3 px-4 rounded-xl text-xs font-bold transition-all border border-blue-500/15"
                >
                  💳 {lang === 'uz' ? "Karta (Chek yuborish)" : "Карта (Отправить чек)"}
                </button>
              )}
            </>
          )}

          {fsmState === 'upload_check' && (
            <button
              onClick={handleCheckUpload}
              className="col-span-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2"
            >
              <Camera className="w-4 h-4" />
              🧾 {lang === 'uz' ? "Chek rasmini yuklash (Simulyatsiya)" : "Загрузить фото чека (Симуляция)"}
            </button>
          )}
        </div>

        {/* TextInput Box */}
        <form onSubmit={handleSendText} className="flex gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={fsmState === 'language' || fsmState === 'payment' || fsmState === 'upload_check'}
            placeholder={
              fsmState === 'phone' 
                ? (lang === 'uz' ? "Telefon raqam yozing..." : "Введите номер...") 
                : fsmState === 'location' 
                ? (lang === 'uz' ? "Yozma manzil kiriting..." : "Введите адрес текстом...")
                : (lang === 'uz' ? "Xabar yozing..." : "Напишите сообщение...")
            }
            className="flex-1 bg-[#24303f] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-blue-500 transition-all disabled:opacity-40"
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white p-2.5 rounded-xl transition-all disabled:opacity-50 active:scale-95 flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
