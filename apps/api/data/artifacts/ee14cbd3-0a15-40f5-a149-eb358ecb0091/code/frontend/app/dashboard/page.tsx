import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Users, FileText, Settings, Plus, Bell } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background flex text-foreground">
      {/* Sidebar */}
      <aside className="w-72 border-r border-white/5 p-8 flex flex-col fixed h-full bg-background/50 backdrop-blur-xl">
        <div className="flex items-center gap-3 mb-12">
          <div className="w-8 h-8 bg-primary rounded-lg shadow-lg shadow-primary/30" />
          <h1 className="text-xl font-black tracking-tighter">APP...</h1>
        </div>
        
        <nav className="flex-1 space-y-2">
          <div className="p-4 bg-primary/10 text-primary rounded-2xl flex items-center gap-3 font-bold">
            <LayoutDashboard size={20} /> Dashboard
          </div>
          <div className="p-4 opacity-50 hover:opacity-100 flex items-center gap-3 transition-opacity">
            <Users size={20} /> Users
          </div>
          <div className="p-4 opacity-50 hover:opacity-100 flex items-center gap-3 transition-opacity">
            <FileText size={20} /> Documents
          </div>
          <div className="p-4 opacity-50 hover:opacity-100 flex items-center gap-3 transition-opacity">
            <Settings size={20} /> Settings
          </div>
        </nav>
        
        <div className="pt-8 border-t border-white/5 flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-primary to-accent" />
          <div>
            <div className="font-bold text-sm">User Profile</div>
            <div className="text-[11px] opacity-40 uppercase font-black">Pro Member</div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-72">
        <header className="h-20 border-b border-white/5 px-12 flex items-center justify-between sticky top-0 bg-background/80 backdrop-blur-lg z-10">
          <h2 className="text-2xl font-black">Dashboard</h2>
          <div className="flex items-center gap-6">
            <Bell className="opacity-40" />
            <button className="px-6 py-2.5 bg-primary text-white rounded-xl font-bold flex items-center gap-2 shadow-lg shadow-primary/20">
              <Plus size={18} /> New Entry
            </button>
          </div>
        </header>

        <div className="p-12 space-y-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="card-premium p-8">
              <h3 className="text-[11px] font-black uppercase tracking-widest opacity-40 mb-4">Total Capacity</h3>
              <p className="text-4xl font-black">12,402</p>
              <div className="mt-4 text-xs text-green-500 font-bold">+12% growth</div>
            </div>
            <div className="card-premium p-8">
              <h3 className="text-[11px] font-black uppercase tracking-widest opacity-40 mb-4">Active Nodes</h3>
              <p className="text-4xl font-black">842</p>
              <div className="mt-4 text-xs text-primary font-bold">Stable performance</div>
            </div>
            <div className="card-premium p-8">
              <h3 className="text-[11px] font-black uppercase tracking-widest opacity-40 mb-4">Security Status</h3>
              <p className="text-4xl font-black text-green-500">Secure</p>
              <div className="mt-4 text-xs opacity-40 font-bold">All systems nominal</div>
            </div>
          </div>

          <div className="card-premium overflow-hidden">
            <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/5">
              <h2 className="font-black">Recent Activity</h2>
              <button className="text-sm font-bold text-primary">View All</button>
            </div>
            <div className="p-8">
              <p className="opacity-50 leading-relaxed italic">
                Content for Dashboard is being synchronized from the edge nodes. 
                Full visualization available in real-time.
              </p>
              <div className="mt-8 space-y-4">
                {[1,2,3].map(i => (
                  <div key={i} className="flex items-center gap-4 p-4 border border-white/5 rounded-2xl bg-white/5">
                    <div className="w-10 h-10 bg-white/5 rounded-xl" />
                    <div className="flex-1">
                      <div className="font-bold text-sm">System Update Process #{i}</div>
                      <div className="text-xs opacity-40">Processed 2 mins ago</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}