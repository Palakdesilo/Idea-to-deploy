import React from 'react';
import Link from 'next/link';
import { ArrowRight, Globe, Shield, Zap } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden">
      <nav className="flex justify-between items-center p-6 max-w-7xl mx-auto border-b border-white/5">
        <h1 className="text-2xl font-black tracking-tighter text-primary">PROJECT...</h1>
        <div className="hidden md:flex space-x-8 text-sm font-medium">
          <Link href="/" className="opacity-70 hover:opacity-100 transition-opacity">Landing Page</Link>
          <Link href="/login" className="opacity-70 hover:opacity-100 transition-opacity">Login</Link>
          <Link href="/register" className="opacity-70 hover:opacity-100 transition-opacity">Register</Link>
          <Link href="/dashboard" className="opacity-70 hover:opacity-100 transition-opacity">Dashboard</Link>
        </div>
        <Link href="/register" className="px-6 py-2.5 bg-primary text-white rounded-xl font-bold hover:scale-105 transition-transform shadow-lg shadow-primary/20">
          Start Trial
        </Link>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-24">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div className="animate-in fade-in slide-in-from-bottom-5 duration-700">
            <h2 className="text-7xl font-black mb-8 leading-[1.1] tracking-tight">
              Welcome <span className="text-gradient">Platform</span>
            </h2>
            <p className="text-xl text-foreground/60 mb-12 max-w-lg leading-relaxed">
              Build an event management platform that allows organizers to create events, sell tickets, manage attendees, process payments, and allows users to discover events, purchase tickets, and receive notifications.


            </p>
            <div className="flex gap-4">
              <Link href="/register" className="px-8 py-4 bg-primary text-white rounded-2xl text-lg font-bold hover:brightness-110 transition-all flex items-center gap-2">
                Get Started <ArrowRight size={20} />
              </Link>
              <Link href="/dashboard" className="px-8 py-4 bg-white/5 border border-white/10 rounded-2xl text-lg font-bold hover:bg-white/10 transition-all">
                View Demo
              </Link>
            </div>
            <div className="mt-12 flex gap-8 text-[11px] font-black uppercase tracking-widest opacity-40">
                <span>★ 4.9/5 Rating</span>
                <span>✓ Free 14-Day Trial</span>
                <span>♥ Loved by Creators</span>
            </div>
          </div>

          <div className="relative">
            <div className="absolute -inset-4 bg-primary/20 blur-[100px] rounded-full" />
            <div className="grid grid-cols-2 gap-4 relative">
              <div className="card-premium p-8 h-48 flex items-end">
                <div className="w-12 h-12 bg-white/5 rounded-lg mb-4" />
              </div>
              <div className="card-premium p-8 h-48 translate-y-8">
                 <Zap className="text-primary mb-4" size={32} />
              </div>
              <div className="card-premium p-8 h-48 bg-primary shadow-2xl shadow-primary/40 flex items-center justify-center -rotate-3">
                 <h3 className="text-2xl font-black text-white">Welcome</h3>
              </div>
              <div className="card-premium p-8 h-48 translate-y-8">
                 <Shield className="text-accent mb-4" size={32}/>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}