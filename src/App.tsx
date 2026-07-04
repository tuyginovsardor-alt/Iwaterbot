import React, { useState, useEffect } from 'react';
import { Droplet, Bot, Shield, ArrowRight, RefreshCw } from 'lucide-react';
import { Settings, Order } from './types';
import LandingPage from './components/LandingPage';
import BotSimulator from './components/BotSimulator';
import AdminPanel from './components/AdminPanel';

export default function App() {
  const [activeView, setActiveView] = useState<'landing' | 'bot' | 'admin'>('landing');
  const [settings, setSettings] = useState<Settings>({
    water_price: '15000',
    manual_payment_status: '1',
    web_site_status: '1',
    terms_uz: 'Rasmiy iWater foydalanish shartlari: toza va sifatli 19L suv yetkazib berish.',
    terms_ru: 'Официальные правила использования iWater: быстрая доставка чистой воды 19л.',
    warehouse_lat: '41.2995',
    warehouse_lon: '69.2401'
  });
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSettingsAndOrders = async () => {
    try {
      // Fetch settings
      const settingsRes = await fetch('/api/settings');
      const settingsData = await settingsRes.json();
      setSettings(settingsData);

      // Fetch orders
      const ordersRes = await fetch('/api/orders');
      const ordersData = await ordersRes.json();
      setOrders(ordersData);
    } catch (err) {
      console.error('Failed to sync settings or orders:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSettingsAndOrders();
  }, []);

  const handleUpdateSettingsLocally = (newSettings: Partial<Settings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return (
    <div className="min-h-screen bg-[#07080d] text-zinc-300 font-sans selection:bg-blue-500/30 flex flex-col">
      {/* Fixed Ambient Background glow */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[5%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[140px]" />
        <div className="absolute -bottom-[10%] -right-[5%] w-[40%] h-[40%] bg-emerald-900/10 rounded-full blur-[140px]" />
      </div>

      {/* Main Container */}
      <div className="relative z-10 flex-1 flex flex-col">
        {/* Workspace Utility Rail Header */}
        <header className="bg-zinc-950/80 backdrop-blur-md sticky top-0 z-50 border-b border-zinc-900 px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600/10 p-2.5 rounded-2xl border border-blue-500/20 text-blue-400">
              <Droplet className="w-6 h-6 fill-current animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-1.5">
                iWater Hub
              </h1>
              <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">
                Full-Stack Delivery Platform
              </p>
            </div>
          </div>

          {/* Core View Switcher buttons */}
          <div className="flex bg-zinc-900 p-1 rounded-2xl border border-zinc-800">
            <button
              onClick={() => setActiveView('landing')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeView === 'landing'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              <Droplet className="w-4 h-4" />
              Mijoz Sayti (Landing)
            </button>
            <button
              onClick={() => setActiveView('bot')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 ${
                activeView === 'bot'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              <Bot className="w-4 h-4" />
              TG Bot (Simulator)
            </button>
            <button
              onClick={() => setActiveView('admin')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 relative ${
                activeView === 'admin'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50'
              }`}
            >
              <Shield className="w-4 h-4" />
              Admin Panel
              {orders.filter(o => o.status === 'new' || o.status === 'pending_payment').length > 0 && (
                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-amber-500 border border-zinc-950 animate-ping" />
              )}
            </button>
          </div>

          {/* Sync status indicator */}
          <button
            onClick={fetchSettingsAndOrders}
            className="p-2 hover:bg-zinc-900 rounded-xl transition-all border border-transparent hover:border-zinc-800 text-zinc-500 hover:text-zinc-300 flex items-center gap-2 text-xs font-medium"
            title="Sync Database"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Sync
          </button>
        </header>

        {/* Dynamic Inner Layout Body */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col justify-center">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 space-y-4">
              <RefreshCw className="w-10 h-10 text-blue-500 animate-spin" />
              <p className="text-sm text-zinc-500">iWater bazasi sinxronizatsiya qilinmoqda...</p>
            </div>
          ) : (
            <div className="w-full">
              {activeView === 'landing' && (
                <LandingPage settings={settings} onOrderSuccess={fetchSettingsAndOrders} />
              )}
              {activeView === 'bot' && (
                <BotSimulator settings={settings} onOrderSuccess={fetchSettingsAndOrders} />
              )}
              {activeView === 'admin' && (
                <AdminPanel 
                  settings={settings} 
                  orders={orders} 
                  onRefresh={fetchSettingsAndOrders} 
                  onUpdateSettings={handleUpdateSettingsLocally} 
                />
              )}
            </div>
          )}
        </main>

        {/* Bottom footer bar explaining the workspace layout */}
        <footer className="border-t border-zinc-900 bg-zinc-950/40 py-6 px-6 text-center text-xs text-zinc-600 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span className="font-medium">Full-Stack Database Local Sync: Connected</span>
          </div>
          <div className="flex gap-4">
            <span className="hover:text-zinc-400 transition-colors">Uzbekistan Region</span>
            <span>•</span>
            <span className="hover:text-zinc-400 transition-colors">19L Toza iWater</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
