import React from 'react';
import Link from 'next/link';

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[20%] left-[20%] w-[500px] h-[500px] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[20%] right-[20%] w-[500px] h-[500px] bg-accent/10 blur-[120px] rounded-full" />
      </div>
      
      <div className="max-w-md w-full card-premium p-12 relative z-10 backdrop-blur-2xl">
        <div className="text-center mb-10">
          <div className="w-12 h-12 bg-primary rounded-xl mx-auto mb-6 shadow-lg shadow-primary/40" />
          <h1 className="text-4xl font-black tracking-tight mb-2">Create Account</h1>
          <p className="opacity-50 text-sm">Secure access to your professional workspace</p>
        </div>
        
        <form className="space-y-6">
          <div className="space-y-2">
            <label className="text-[11px] font-black uppercase tracking-widest opacity-50">Email Address</label>
            <input type="email" className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:border-primary outline-none transition-all" placeholder="name@domain.com" />
          </div>
          <div className="space-y-2">
            <label className="text-[11px] font-black uppercase tracking-widest opacity-50">Password</label>
            <input type="password" className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:border-primary outline-none transition-all" placeholder="••••••••" />
          </div>
          <div className="space-y-2">
            <label className="text-[11px] font-black uppercase tracking-widest opacity-50">Confirm Password</label>
            <input type="password"  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:border-primary outline-none transition-all" placeholder="••••••••" />
          </div>
          <button type="submit" className="w-full bg-primary text-white py-4 rounded-2xl font-bold hover:brightness-110 transition-all shadow-xl shadow-primary/20">
            Sign Up
          </button>
        </form>
        
        <p className="text-center text-sm mt-8 opacity-60">
          Already have an account?
          <Link href="/login" className="text-primary font-black hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}