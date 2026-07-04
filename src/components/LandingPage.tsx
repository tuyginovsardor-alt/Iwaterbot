import React, { useState } from 'react';
import { Droplet, Truck, ShieldCheck, Clock, CheckCircle2, Construction, Smartphone } from 'lucide-react';
import { Order, Settings } from '../types';

interface LandingPageProps {
  settings: Settings;
  onOrderSuccess: () => void;
}

export default function LandingPage({ settings, onOrderSuccess }: LandingPageProps) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [address, setAddress] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successOrder, setSuccessOrder] = useState<Order | null>(null);

  const price = parseInt(settings.water_price || '15000', 10);
  const total = quantity * price;

  const handleOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !phone || !address) return;

    setIsSubmitting(true);
    try {
      const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 0, // 0 indicates Web
          full_name: name,
          phone,
          items: `${quantity} dona 19L (Web)`,
          total_price: total,
          address,
          latitude: 0,
          longitude: 0,
          status: 'new',
          payment_type: 'Naqd'
        })
      });

      const result = await response.json();
      if (result.success) {
        setSuccessOrder(result.order);
        onOrderSuccess();
        setName('');
        setPhone('');
        setQuantity(1);
        setAddress('');
      }
    } catch (err) {
      console.error('Order submission failed:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (settings.web_site_status === '0') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <div className="bg-zinc-900 border border-zinc-800 rounded-3xl p-10 space-y-8 shadow-xl">
          <div className="bg-blue-500/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto text-blue-400">
            <Construction className="w-10 h-10" />
          </div>
          <div className="space-y-3">
            <h1 className="text-3xl font-bold text-white">Veb-sayt vaqtincha to'xtatilgan</h1>
            <p className="text-zinc-400 text-base max-w-md mx-auto">
              Hozirda veb-sayt orqali buyurtma qabul qilish vaqtincha to'xtatilgan. Iltimos, tez va oson buyurtma berish uchun bizning rasmiy Telegram botimizdan foydalaning:
            </p>
          </div>
          <div className="p-4 bg-zinc-800/30 rounded-2xl border border-zinc-800 flex items-center justify-center gap-3 max-w-sm mx-auto">
            <Smartphone className="text-blue-400 w-5 h-5" />
            <span className="font-semibold text-white text-lg">@iwater_official_bot</span>
          </div>
          <p className="text-xs text-zinc-500">
            Bot orqali 24/7 buyurtma berishingiz, to'lovni tasdiqlashingiz va buyurtmangiz holatini kuzatib borishingiz mumkin.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-16 py-8 px-4 max-w-6xl mx-auto">
      {/* Hero Section */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-7 space-y-6">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 px-4 py-2 rounded-full text-blue-400 text-sm font-medium">
            <Droplet className="w-4 h-4 fill-current" />
            Toza va minerallashgan ichimlik suvi
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Uyingizga toza suv <br />
            <span className="text-blue-500">bepul yetkaziladi!</span>
          </h1>
          <p className="text-lg text-zinc-400 max-w-xl">
            19 litrlik yuqori sifatli toza ichimlik suvi. Toshkent bo'ylab eng tez va sifatli yetkazib berish xizmati.
          </p>
          <div className="flex flex-wrap gap-4 pt-2">
            <div className="flex items-center gap-3 bg-zinc-900 border border-zinc-800 p-4 rounded-2xl">
              <div className="bg-emerald-500/15 p-2 rounded-xl text-emerald-400">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-zinc-500 font-medium">Yetkazib berish</p>
                <p className="font-bold text-white">45-60 daqiqa</p>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-zinc-900 border border-zinc-800 p-4 rounded-2xl">
              <div className="bg-blue-500/15 p-2 rounded-xl text-blue-400">
                <Truck className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-zinc-500 font-medium">Shahar ichida</p>
                <p className="font-bold text-white">Mutlaqo bepul</p>
              </div>
            </div>
          </div>
        </div>
        <div className="lg:col-span-5 relative">
          <div className="absolute inset-0 bg-blue-500/10 blur-[100px] rounded-full" />
          <img
            src="https://images.unsplash.com/photo-1548839140-29a749e1cf4d?q=80&w=1000&auto=format&fit=crop"
            alt="iWater Delivery 19L"
            className="rounded-[32px] border-4 border-zinc-800 shadow-2xl relative z-10 w-full object-cover max-h-[380px]"
          />
        </div>
      </section>

      {/* Main Order Box */}
      <section id="order" className="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 sm:p-10 shadow-2xl">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Price & Benefits Info */}
          <div className="lg:col-span-5 space-y-8 flex flex-col justify-between">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-white">Tezkor Buyurtma</h2>
              <p className="text-zinc-400 text-sm">
                Quyidagi so'rovnomani to'ldirishingiz bilan operatorlarimiz siz bilan aloqaga chiqadilar va eng yaqin omborimizdan suv yo'lga chiqadi.
              </p>
            </div>

            <div className="bg-zinc-950 border border-zinc-850 p-6 rounded-2xl text-center space-y-1">
              <p className="text-zinc-500 uppercase tracking-wider text-xs font-bold">1 dona idish narxi</p>
              <p className="text-4xl font-extrabold text-blue-400">
                {price.toLocaleString()} <span className="text-lg font-medium text-zinc-400">so'm</span>
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-3 p-4 rounded-xl bg-blue-500/5 border border-blue-500/10 text-blue-400">
                <ShieldCheck className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">Barcha laboratoriya sinovlaridan o'tgan</span>
              </div>
              <div className="flex items-center gap-3 p-4 rounded-xl bg-blue-500/5 border border-blue-500/10 text-blue-400">
                <Truck className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">Uyingiz eshigigacha bepul olib kirish</span>
              </div>
            </div>
          </div>

          {/* Form */}
          <div className="lg:col-span-7">
            {successOrder ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4 bg-zinc-950 rounded-2xl border border-zinc-850">
                <CheckCircle2 className="w-16 h-16 text-emerald-400 animate-bounce" />
                <div className="space-y-1">
                  <h3 className="text-xl font-bold text-white">Buyurtmangiz muvaffaqiyatli qabul qilindi!</h3>
                  <p className="text-zinc-400 text-sm">Buyurtma raqami: #{successOrder.id}</p>
                </div>
                <p className="text-sm text-zinc-500 max-w-sm">
                  Tez orada operatorimiz {successOrder.phone} raqamingizga bog'lanib, manzilingizni aniqlaydi.
                </p>
                <button
                  onClick={() => setSuccessOrder(null)}
                  className="mt-4 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors text-sm"
                >
                  Yangi buyurtma berish
                </button>
              </div>
            ) : (
              <form onSubmit={handleOrder} className="space-y-5">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Sizning ismingiz</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Masalan: Azizbek"
                    className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 text-white placeholder-zinc-600 transition-all text-sm"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Telefon raqamingiz</label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+998 90 123 45 67"
                    className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 text-white placeholder-zinc-600 transition-all text-sm"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Suv miqdori (19L idishlar soni)</label>
                  <div className="flex items-center gap-4 bg-zinc-950 p-1.5 rounded-xl border border-zinc-800 w-fit">
                    <button
                      type="button"
                      onClick={() => setQuantity(Math.max(1, quantity - 1))}
                      className="w-10 h-10 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center hover:bg-zinc-850 active:scale-95 text-white transition-all font-bold"
                    >
                      -
                    </button>
                    <span className="text-xl font-bold text-white px-4 min-w-[40px] text-center">{quantity}</span>
                    <button
                      type="button"
                      onClick={() => setQuantity(quantity + 1)}
                      className="w-10 h-10 rounded-lg bg-blue-600 hover:bg-blue-700 flex items-center justify-center active:scale-95 text-white transition-all font-bold"
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Batafsil yetkazib berish manzili</label>
                  <textarea
                    required
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Tuman, ko'cha nomi, uy raqami, xonadon, mo'ljal..."
                    rows={3}
                    className="w-full px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 text-white placeholder-zinc-600 transition-all text-sm"
                  />
                </div>

                <div className="pt-4 border-t border-zinc-850 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                  <div>
                    <p className="text-xs text-zinc-500">Umumiy to'lov (Naqd):</p>
                    <p className="text-2xl font-extrabold text-white">
                      {total.toLocaleString()} <span className="text-xs font-normal text-zinc-400">so'm</span>
                    </p>
                  </div>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full sm:w-auto px-8 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl transition-all hover:shadow-lg hover:shadow-blue-500/20 active:scale-95 disabled:opacity-50 text-sm flex items-center justify-center"
                  >
                    {isSubmitting ? 'Yuborilmoqda...' : 'Buyurtma Berish'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
