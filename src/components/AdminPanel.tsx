import React, { useState, useEffect } from 'react';
import { Settings as SettingsType, Order, Channel } from '../types';
import { 
  TrendingUp, Users, ShoppingCart, DollarSign, Settings as SettingsIcon, 
  Trash2, Plus, Download, Check, X, RotateCcw, Link as LinkIcon, Image as ImageIcon, ShieldCheck
} from 'lucide-react';

interface AdminPanelProps {
  settings: SettingsType;
  orders: Order[];
  onRefresh: () => void;
  onUpdateSettings: (newSettings: Partial<SettingsType>) => void;
}

export default function AdminPanel({ settings, orders, onRefresh, onUpdateSettings }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<'orders' | 'stats' | 'settings' | 'channels'>('orders');
  
  // Search State
  const [searchQuery, setSearchQuery] = useState('');

  // Settings Form State
  const [waterPrice, setWaterPrice] = useState(settings.water_price);
  const [manualPay, setManualPay] = useState(settings.manual_payment_status === '1');
  const [webActive, setWebActive] = useState(settings.web_site_status === '1');
  const [termsUz, setTermsUz] = useState(settings.terms_uz);
  const [termsRu, setTermsRu] = useState(settings.terms_ru);
  const [welcomeUz, setWelcomeUz] = useState(settings.welcome_msg_uz || "👋 Assalomu alaykum! **iWater** xizmatiga xush kelibsiz.\n✨ Toza va sifatli 19L suv yetkazib berish.\n\n👇 Davom etish uchun tilni tanlang:");
  const [welcomeRu, setWelcomeRu] = useState(settings.welcome_msg_ru || "👋 Здравствуйте! Добро пожаловать в сервис **iWater**.\n✨ Доставка чистой и качественной 19л воды.\n\n👇 Для продолжения выберите язык:");
  
  // Channels Management State
  const [channels, setChannels] = useState<Channel[]>([]);
  const [newChId, setNewChId] = useState('');
  const [newChName, setNewChName] = useState('');
  const [newChLink, setNewChLink] = useState('');

  // Rejection Reason Modal/Input
  const [rejectionTargetId, setRejectionTargetId] = useState<number | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  // Fetch Channels
  const fetchChannels = async () => {
    try {
      const res = await fetch('/api/channels');
      const data = await res.json();
      setChannels(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchChannels();
  }, []);

  // Update Settings in bulk
  const saveSettings = async () => {
    try {
      const response = await fetch('/api/settings/bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          water_price: waterPrice,
          manual_payment_status: manualPay ? '1' : '0',
          web_site_status: webActive ? '1' : '0',
          terms_uz: termsUz,
          terms_ru: termsRu,
          welcome_msg_uz: welcomeUz,
          welcome_msg_ru: welcomeRu,
        })
      });
      const data = await response.json();
      if (data.success) {
        onUpdateSettings(data.settings);
        alert('Sozlamalar muvaffaqiyatli saqlandi!');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Add Telegram Channel
  const handleAddChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newChId || !newChName || !newChLink) return;

    try {
      const res = await fetch('/api/channels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: newChId, name: newChName, invite_link: newChLink })
      });
      const data = await res.json();
      if (data.success) {
        setChannels(data.channels);
        setNewChId('');
        setNewChName('');
        setNewChLink('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Delete Telegram Channel
  const handleDeleteChannel = async (id: string) => {
    try {
      const res = await fetch(`/api/channels/${id.replace('@', '')}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.success) {
        setChannels(data.channels);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Update Order Status
  const handleUpdateOrderStatus = async (
    orderId: number, 
    newStatus: Order['status'], 
    reason?: string
  ) => {
    try {
      const response = await fetch(`/api/orders/${orderId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          admin_name: 'Super Admin',
          rejection_reason: reason
        })
      });
      const data = await response.json();
      if (data.success) {
        onRefresh();
        setRejectionTargetId(null);
        setRejectionReason('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Reset Demo Orders
  const handleResetDemo = async () => {
    if (!confirm('Haqiqatdan ham barcha buyurtmalarni tozalab boshlang\'ich holatga qaytarmoqchimisiz?')) return;
    try {
      await fetch('/api/orders/reset', { method: 'POST' });
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  // CSV/Excel Export simulation
  const handleExportCSV = () => {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Buyurtma ID,Mijoz,Telefon,Mahsulotlar,Umumiy Narxi,Manzil,Status,To'lov turi,Yaratilgan Sana\n";
    
    orders.forEach(o => {
      csvContent += `${o.id},"${o.full_name}","${o.phone}","${o.items}",${o.total_price},"${o.address}",${o.status},${o.payment_type},${o.created_at}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `iwater_orders_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Statistics calculation
  const totalRevenue = orders
    .filter(o => o.status === 'delivered' || o.status === 'accepted' || o.status === 'on_the_way')
    .reduce((sum, o) => sum + o.total_price, 0);

  const completedOrders = orders.filter(o => o.status === 'delivered').length;
  const avgOrderValue = completedOrders > 0 ? Math.round(totalRevenue / completedOrders) : 0;
  const uniqueCustomers = new Set(orders.map(o => o.phone)).size;

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-3xl overflow-hidden shadow-2xl flex flex-col h-[650px]">
      {/* Top Banner / Tab Selector */}
      <div className="bg-zinc-950 border-b border-zinc-850 p-4 flex flex-wrap gap-2 items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600/10 p-1.5 rounded-lg border border-blue-500/20 text-blue-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <span className="font-bold text-white text-base">iWater Admin Console</span>
        </div>
        
        <div className="flex gap-1.5 bg-zinc-900 p-1 rounded-xl border border-zinc-800">
          {(['orders', 'stats', 'settings', 'channels'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all uppercase tracking-wider ${
                activeTab === tab 
                  ? 'bg-blue-600 text-white shadow-md' 
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              {tab === 'orders' && 'Buyurtmalar'}
              {tab === 'stats' && 'Statistika'}
              {tab === 'settings' && 'Sozlamalar'}
              {tab === 'channels' && 'Kanallar'}
            </button>
          ))}
        </div>
      </div>

      {/* Main Tab Content */}
      <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-zinc-800">
        
        {/* ORDERS TAB */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div className="space-y-0.5">
                <h3 className="text-lg font-bold text-white">Faol buyurtmalar</h3>
                <p className="text-xs text-zinc-500">Mijozlardan kelib tushayotgan yangi buyurtmalarni boshqarish</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleExportCSV}
                  className="px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-semibold rounded-lg text-xs flex items-center gap-1.5 border border-zinc-700 transition-all"
                >
                  <Download className="w-3.5 h-3.5" />
                  Excel hisobot
                </button>
                <button
                  onClick={handleResetDemo}
                  className="px-3 py-1.5 bg-red-950/30 hover:bg-red-950/50 text-red-400 font-semibold rounded-lg text-xs flex items-center gap-1.5 border border-red-500/10 transition-all"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Tozalash
                </button>
              </div>
            </div>

            {/* Search Box */}
            <div className="bg-zinc-950/20 p-1 rounded-2xl border border-zinc-850">
              <input
                type="text"
                placeholder="Buyurtmalarni ID, telefon yoki mijoz ismi orqali qidirish..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-blue-500 transition-all"
              />
            </div>

            {/* List */}
            {orders.length === 0 ? (
              <div className="text-center py-12 text-zinc-500 text-sm">Hozircha buyurtmalar yo'q.</div>
            ) : (() => {
              const filteredOrders = orders.filter(o => 
                o.id.toString().includes(searchQuery) ||
                o.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                o.phone.includes(searchQuery) ||
                o.address.toLowerCase().includes(searchQuery.toLowerCase())
              );

              if (filteredOrders.length === 0) {
                return <div className="text-center py-12 text-zinc-500 text-sm">Mos keladigan buyurtmalar topilmadi.</div>;
              }

              return (
                <div className="space-y-3">
                  {filteredOrders.map(o => (
                  <div key={o.id} className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-2xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:border-zinc-800 transition-all">
                    <div className="space-y-2 max-w-md">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-mono font-bold text-zinc-500 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded-md">
                          #{o.id}
                        </span>
                        <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                          o.status === 'new' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/10' :
                          o.status === 'accepted' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/10' :
                          o.status === 'on_the_way' ? 'bg-purple-500/10 text-purple-400 border border-purple-500/10' :
                          o.status === 'delivered' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/10' :
                          o.status === 'pending_payment' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/10' :
                          'bg-zinc-800 text-zinc-400 border border-zinc-700/50'
                        }`}>
                          {o.status === 'new' && 'Yangi'}
                          {o.status === 'accepted' && 'Qabul qilingan'}
                          {o.status === 'on_the_way' && 'Yo\'lda'}
                          {o.status === 'delivered' && 'Yetkazilgan'}
                          {o.status === 'pending_payment' && 'To\'lov kutilmoqda'}
                          {o.status === 'rejected' && 'Rad etilgan'}
                        </span>
                        <span className="text-zinc-500 text-xs font-medium">
                          {o.user_id === 0 ? '🌐 Veb-sayt' : '🤖 Telegram'}
                        </span>
                      </div>
                      <div className="space-y-1 text-sm">
                        <p className="font-semibold text-white">{o.full_name}</p>
                        <p className="text-zinc-400 font-medium text-xs">📞 {o.phone}</p>
                        <p className="text-zinc-400 font-medium text-xs">📍 {o.address}</p>
                        <p className="text-zinc-300 font-semibold text-xs mt-1">
                          📦 {o.items} | <span className="text-blue-400">{o.total_price.toLocaleString()} so'm</span> | 💳 {o.payment_type}
                        </p>
                        {o.rejection_reason && (
                          <p className="text-red-400 font-semibold text-xs mt-1 bg-red-500/5 border border-red-500/10 p-2 rounded-lg">
                            ⚠️ Sabab: {o.rejection_reason}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1.5 flex-wrap">
                      {o.status === 'new' && (
                        <>
                          <button
                            onClick={() => handleUpdateOrderStatus(o.id, 'accepted')}
                            className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-xl transition-all active:scale-95 text-xs font-semibold flex items-center gap-1"
                            title="Qabul qilish"
                          >
                            <Check className="w-4 h-4" /> Qabul qilish
                          </button>
                          <button
                            onClick={() => setRejectionTargetId(o.id)}
                            className="bg-red-950/20 hover:bg-red-950/40 text-red-400 border border-red-500/10 p-2 rounded-xl transition-all active:scale-95 text-xs font-semibold flex items-center gap-1"
                            title="Rad etish"
                          >
                            <X className="w-4 h-4" /> Rad etish
                          </button>
                        </>
                      )}

                      {o.status === 'pending_payment' && (
                        <div className="flex flex-col gap-2 items-end">
                          {o.payment_check_file_id && (
                            <a href={o.payment_check_file_id} target="_blank" rel="noreferrer" className="text-xs text-blue-400 hover:underline flex items-center gap-1 font-semibold mb-1">
                              <ImageIcon className="w-3.5 h-3.5" /> Chekni ko'rish
                            </a>
                          )}
                          <div className="flex gap-1.5">
                            <button
                              onClick={() => handleUpdateOrderStatus(o.id, 'accepted')}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-xl transition-all text-xs font-semibold"
                            >
                              To'lovni tasdiqlash
                            </button>
                            <button
                              onClick={() => setRejectionTargetId(o.id)}
                              className="bg-red-950/30 text-red-400 px-3 py-1.5 rounded-xl transition-all text-xs font-semibold border border-red-500/15"
                            >
                              Rad etish
                            </button>
                          </div>
                        </div>
                      )}

                      {o.status === 'accepted' && (
                        <button
                          onClick={() => handleUpdateOrderStatus(o.id, 'on_the_way')}
                          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl transition-all active:scale-95 text-xs font-semibold"
                        >
                          Yo'lga chiqarish 🚚
                        </button>
                      )}

                      {o.status === 'on_the_way' && (
                        <button
                          onClick={() => handleUpdateOrderStatus(o.id, 'delivered')}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl transition-all active:scale-95 text-xs font-semibold"
                        >
                          Topshirildi! 🏁
                        </button>
                      )}

                      {rejectionTargetId === o.id && (
                        <div className="bg-zinc-950 border border-zinc-800 p-3 rounded-xl space-y-2 mt-2 w-full max-w-xs">
                          <input
                            type="text"
                            placeholder="Rad etish sababini kiriting..."
                            value={rejectionReason}
                            onChange={(e) => setRejectionReason(e.target.value)}
                            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-red-500"
                          />
                          <div className="flex gap-2 justify-end">
                            <button
                              onClick={() => setRejectionTargetId(null)}
                              className="px-2.5 py-1 text-[10px] text-zinc-400"
                            >
                              Bekor qilish
                            </button>
                            <button
                              onClick={() => handleUpdateOrderStatus(o.id, 'rejected', rejectionReason)}
                              className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded-lg text-[10px] font-bold"
                            >
                              Tasdiqlash
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  ))}
                </div>
              );
            })()}
          </div>
        )}

        {/* STATISTICS TAB */}
        {activeTab === 'stats' && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-white">Tizim Statistikasi</h3>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-zinc-950 border border-zinc-850 p-4 rounded-2xl space-y-1">
                <div className="flex items-center justify-between text-zinc-500">
                  <span className="text-xs font-medium">Barcha buyurtmalar</span>
                  <ShoppingCart className="w-4 h-4" />
                </div>
                <p className="text-2xl font-bold text-white">{orders.length}</p>
              </div>

              <div className="bg-zinc-950 border border-zinc-850 p-4 rounded-2xl space-y-1">
                <div className="flex items-center justify-between text-zinc-500">
                  <span className="text-xs font-medium">Jami tushum</span>
                  <DollarSign className="w-4 h-4 text-emerald-400" />
                </div>
                <p className="text-2xl font-bold text-emerald-400">{totalRevenue.toLocaleString()} sum</p>
              </div>

              <div className="bg-zinc-950 border border-zinc-850 p-4 rounded-2xl space-y-1">
                <div className="flex items-center justify-between text-zinc-500">
                  <span className="text-xs font-medium">Mijozlar soni</span>
                  <Users className="w-4 h-4 text-blue-400" />
                </div>
                <p className="text-2xl font-bold text-white">{uniqueCustomers}</p>
              </div>

              <div className="bg-zinc-950 border border-zinc-850 p-4 rounded-2xl space-y-1">
                <div className="flex items-center justify-between text-zinc-500">
                  <span className="text-xs font-medium">O'rtacha buyurtma</span>
                  <TrendingUp className="w-4 h-4 text-purple-400" />
                </div>
                <p className="text-2xl font-bold text-white">{avgOrderValue.toLocaleString()} sum</p>
              </div>
            </div>

            {/* Quick Chart Simulation / Logs */}
            <div className="bg-zinc-950/40 border border-zinc-850 p-6 rounded-3xl space-y-4">
              <h4 className="text-sm font-bold text-white">Yillik hisobotlar diagrammasi (Faol)</h4>
              <div className="h-40 flex items-end gap-3 pt-6 border-b border-zinc-800">
                <div className="flex-1 bg-blue-500/20 hover:bg-blue-500/30 rounded-t-lg transition-all h-[30%] relative group">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 border border-zinc-800 text-[10px] text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    30%
                  </div>
                </div>
                <div className="flex-1 bg-blue-500/30 hover:bg-blue-500/40 rounded-t-lg transition-all h-[45%] relative group">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 border border-zinc-800 text-[10px] text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    45%
                  </div>
                </div>
                <div className="flex-1 bg-blue-500/40 hover:bg-blue-500/50 rounded-t-lg transition-all h-[60%] relative group">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 border border-zinc-800 text-[10px] text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    60%
                  </div>
                </div>
                <div className="flex-1 bg-blue-500 hover:bg-blue-600 rounded-t-lg transition-all h-[95%] relative group">
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2 bg-zinc-900 border border-zinc-800 text-[10px] text-white px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity">
                    95%
                  </div>
                </div>
              </div>
              <div className="flex text-[10px] text-zinc-500 font-mono font-bold justify-between">
                <span>Mart</span>
                <span>Aprel</span>
                <span>May</span>
                <span>Iyun/Iyul</span>
              </div>
            </div>
          </div>
        )}

        {/* SETTINGS TAB */}
        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h3 className="text-lg font-bold text-white">Bot Sozlamalari</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Suv narxi (so'mda)</label>
                  <input
                    type="number"
                    value={waterPrice}
                    onChange={(e) => setWaterPrice(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-sm text-white"
                  />
                </div>

                <div className="space-y-3">
                  <label className="flex items-center gap-2.5 bg-zinc-950/40 border border-zinc-850 p-3.5 rounded-xl cursor-pointer hover:border-zinc-800 transition-all">
                    <input
                      type="checkbox"
                      checked={manualPay}
                      onChange={(e) => setManualPay(e.target.checked)}
                      className="w-4 h-4 rounded text-blue-600 bg-zinc-950 border-zinc-800 focus:ring-blue-500/20 focus:ring-2"
                    />
                    <div>
                      <p className="text-sm font-bold text-white">Manual Karta To'lovi (Chek yuborish)</p>
                      <p className="text-xs text-zinc-500">Mijozlar to'lov cheki rasmini yuborish imkoniyatini yoqish</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-2.5 bg-zinc-950/40 border border-zinc-850 p-3.5 rounded-xl cursor-pointer hover:border-zinc-800 transition-all">
                    <input
                      type="checkbox"
                      checked={webActive}
                      onChange={(e) => setWebActive(e.target.checked)}
                      className="w-4 h-4 rounded text-blue-600 bg-zinc-950 border-zinc-800 focus:ring-blue-500/20 focus:ring-2"
                    />
                    <div>
                      <p className="text-sm font-bold text-white">Veb-sayt Rejimi (Landing Page)</p>
                      <p className="text-xs text-zinc-500">Saytdan buyurtma olishni faollashtirish (aks holda Texnik Xizmat ko'rsatiladi)</p>
                    </div>
                  </label>
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Foydalanish shartlari (Uzbek)</label>
                  <textarea
                    value={termsUz}
                    onChange={(e) => setTermsUz(e.target.value)}
                    rows={2}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-white focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Условия использования (Russian)</label>
                  <textarea
                    value={termsRu}
                    onChange={(e) => setTermsRu(e.target.value)}
                    rows={2}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-white focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Kutib olish start matni (Uzbek)</label>
                  <textarea
                    value={welcomeUz}
                    onChange={(e) => setWelcomeUz(e.target.value)}
                    rows={3}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-white focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-sm font-medium text-zinc-300">Приветственный текст start (Russian)</label>
                  <textarea
                    value={welcomeRu}
                    onChange={(e) => setWelcomeRu(e.target.value)}
                    rows={3}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-xl p-3 text-xs text-white focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-zinc-850 flex justify-end">
              <button
                onClick={saveSettings}
                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-xl transition-all active:scale-95 text-xs flex items-center gap-1.5 shadow-lg shadow-blue-500/10"
              >
                <SettingsIcon className="w-4 h-4" />
                Sozlamalarni saqlash
              </button>
            </div>
          </div>
        )}

        {/* CHANNELS TAB */}
        {activeTab === 'channels' && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white">Majburiy obuna kanallari</h3>
              <p className="text-xs text-zinc-500">Mijoz botdan foydalanishi uchun a'zo bo'lishi talab qilinadigan Telegram kanallari ro'yxati</p>
            </div>

            <form onSubmit={handleAddChannel} className="bg-zinc-950/40 border border-zinc-850 p-4 rounded-2xl grid grid-cols-1 md:grid-cols-3 gap-3 items-end">
              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold text-zinc-500 uppercase">Kanal ID / Username</label>
                <input
                  type="text"
                  required
                  placeholder="Masalan: @iwater_official"
                  value={newChId}
                  onChange={(e) => setNewChId(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-xs text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold text-zinc-500 uppercase">Kanal nomi</label>
                <input
                  type="text"
                  required
                  placeholder="Masalan: iWater Rasmiy Kanali"
                  value={newChName}
                  onChange={(e) => setNewChName(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-xs text-white"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block text-[10px] font-bold text-zinc-500 uppercase">Taklif havolasi (Link)</label>
                <input
                  type="url"
                  required
                  placeholder="https://t.me/joinchat/..."
                  value={newChLink}
                  onChange={(e) => setNewChLink(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 text-xs text-white"
                />
              </div>

              <button
                type="submit"
                className="md:col-span-3 bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 px-4 rounded-lg transition-all text-xs flex items-center justify-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Kanal qo'shish
              </button>
            </form>

            <div className="space-y-2">
              {channels.map(ch => (
                <div key={ch.id} className="bg-zinc-950/40 border border-zinc-850 p-3 px-4 rounded-xl flex justify-between items-center hover:border-zinc-800 transition-all">
                  <div className="space-y-0.5 text-sm">
                    <p className="font-bold text-white">{ch.name}</p>
                    <p className="text-zinc-500 text-xs flex items-center gap-1">
                      <LinkIcon className="w-3 h-3 text-zinc-600" /> {ch.invite_link}
                    </p>
                  </div>
                  <button
                    onClick={() => handleDeleteChannel(ch.id)}
                    className="p-2 bg-red-950/10 hover:bg-red-950/30 text-red-400 border border-red-500/10 rounded-lg transition-all active:scale-95"
                    title="Kanalni o'chirish"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
