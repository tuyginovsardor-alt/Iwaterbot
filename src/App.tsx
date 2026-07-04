import React from 'react';
import { Bot, Server, Terminal, Shield, Globe } from 'lucide-react';
import { motion } from 'motion/react';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0c] text-zinc-300 font-sans selection:bg-blue-500/30">
      {/* Background decoration */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] bg-blue-900/10 rounded-full blur-[120px]" />
        <div className="absolute -bottom-[20%] -right-[10%] w-[50%] h-[50%] bg-emerald-900/10 rounded-full blur-[120px]" />
      </div>

      <main className="relative z-10 max-w-4xl mx-auto px-6 py-20">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-12"
        >
          {/* Header */}
          <header className="flex flex-col items-center text-center space-y-4">
            <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-2xl">
              <Bot className="w-12 h-12 text-blue-400" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
              iWater Bot Backend
            </h1>
            <p className="text-lg text-zinc-400 max-w-xl">
              Production-ready Telegram bot infrastructure for 19L water delivery services.
              Optimized for performance, reliability, and automated deployment.
            </p>
          </header>

          {/* Status Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <StatusCard 
              icon={<Server className="w-5 h-5" />}
              title="Deployment Ready"
              description="Automated Bash scripts for Ubuntu/Debian server setup."
              status="Online"
              color="text-emerald-400"
            />
            <StatusCard 
              icon={<Shield className="w-5 h-5" />}
              title="Admin Security"
              description="Protected admin panel with order state synchronization."
              status="Active"
              color="text-blue-400"
            />
            <StatusCard 
              icon={<Globe className="w-5 h-5" />}
              title="Multilingual"
              description="Native support for Uzbek (UZ) and Russian (RU) interfaces."
              status="Ready"
              color="text-purple-400"
            />
            <StatusCard 
              icon={<Terminal className="w-5 h-5" />}
              title="Async Backend"
              description="Powered by aiogram 3.x and aiosqlite for high concurrency."
              status="Live"
              color="text-amber-400"
            />
          </div>

          {/* Project Structure Summary */}
          <section className="bg-zinc-900/50 border border-zinc-800 rounded-2xl p-8 space-y-6">
            <h2 className="text-xl font-semibold text-white flex items-center gap-2">
              <Terminal className="w-5 h-5 text-zinc-500" />
              Core Architecture
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-y-4 text-sm font-mono">
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Handlers</span>
                <span className="text-zinc-300">Client / Admin</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Persistence</span>
                <span className="text-zinc-300">aiosqlite (Local)</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Deployment</span>
                <span className="text-zinc-300">systemd / Bash</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">State Mgmt</span>
                <span className="text-zinc-300">aiogram FSM</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Localization</span>
                <span className="text-zinc-300">Multi-string Map</span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-zinc-500">Automation</span>
                <span className="text-zinc-300">CI/CD Ready</span>
              </div>
            </div>
          </section>

          {/* Footer Instruction */}
          <footer className="text-center text-sm text-zinc-500 pt-10">
            <p>Deploy to your server using <code>chmod +x setup.sh && ./setup.sh</code></p>
          </footer>
        </motion.div>
      </main>
    </div>
  );
}

function StatusCard({ icon, title, description, status, color }: { 
  icon: React.ReactNode, 
  title: string, 
  description: string, 
  status: string,
  color: string 
}) {
  return (
    <div className="p-6 bg-zinc-900/30 border border-zinc-800/50 rounded-2xl hover:border-zinc-700 transition-colors group">
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-zinc-800/50 rounded-lg text-zinc-400 group-hover:text-white transition-colors">
          {icon}
        </div>
        <div className={`flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-full bg-zinc-800/50 ${color}`}>
          <div className={`w-1.5 h-1.5 rounded-full bg-current`} />
          {status}
        </div>
      </div>
      <h3 className="text-lg font-medium text-white mb-1">{title}</h3>
      <p className="text-sm text-zinc-500 leading-relaxed">{description}</p>
    </div>
  );
}
