
import json
from pathlib import Path

class MockLLM:
    async def generate_content(self, *args, **kwargs):
        return "export default function Page() { return <div>Test</div> }"

class AICoder:
    def __init__(self):
        self.llm = MockLLM()

    def _create_fallback_page(self, screen_name: str, screen_key: str, description: str) -> str:
        """Create a premium, design-aware fallback page component when LLM generation fails"""
        screen_lower = screen_name.lower()
        
        # Landing Page Template
        if 'landing' in screen_lower or screen_key == '' or screen_key == 'landing':
            return f'''import React from 'react';
import Link from 'next/link';
import {{ ArrowRight, Globe, Shield, Zap }} from 'lucide-react';
import {{ motion }} from 'framer-motion';

export default function LandingPage() {{
  return (
    <div className="min-h-screen bg-background text-foreground">
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
          <motion.div 
            initial={{{{ opacity: 0, y: 20 }}}}
            animate={{{{ opacity: 1, y: 0 }}}}
            transition={{{{ duration: 0.8 }}}}
          >
            <h2 className="text-7xl font-black mb-8 leading-[1.1] tracking-tight">
              Welcome <span className="text-gradient">Platform</span>
            </h2>
            <p className="text-xl text-foreground/60 mb-12 max-w-lg leading-relaxed">
              {description}
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
          </motion.div>

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
}}'''
        
        # Auth Pages (Login/Register)
        elif 'login' in screen_lower or 'register' in screen_lower:
            is_register = 'register' in screen_lower
            title = "Create Account" if is_register else "Welcome Back"
            button_text = "Sign Up" if is_register else "Sign In"
            switch_text = "Already have an account?" if is_register else "Don't have an account?"
            switch_link = "login" if is_register else "register"
            switch_button = "Sign In" if is_register else "Sign Up"
            
            confirm_password_field = f'''
          <div className="space-y-2">
            <label className="text-[11px] font-black uppercase tracking-widest opacity-50">Confirm Password</label>
            <input type="password"  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:border-primary outline-none transition-all" placeholder="••••••••" />
          </div>''' if is_register else ''
            
            return f'''import React from 'react';
import Link from 'next/link';

export default function {screen_name.replace(" ", "")}Page() {{
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[20%] left-[20%] w-[500px] h-[500px] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[20%] right-[20%] w-[500px] h-[500px] bg-accent/10 blur-[120px] rounded-full" />
      </div>
      
      <div className="max-w-md w-full card-premium p-12 relative z-10 backdrop-blur-2xl">
        <div className="text-center mb-10">
          <div className="w-12 h-12 bg-primary rounded-xl mx-auto mb-6 shadow-lg shadow-primary/40" />
          <h1 className="text-4xl font-black tracking-tight mb-2">{title}</h1>
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
          </div>{confirm_password_field}
          <button type="submit" className="w-full bg-primary text-white py-4 rounded-2xl font-bold hover:brightness-110 transition-all shadow-xl shadow-primary/20">
            {button_text}
          </button>
        </form>
        
        <p className="text-center text-sm mt-8 opacity-60">
          {switch_text}{{' '}}
          <Link href="/{switch_link}" className="text-primary font-black hover:underline">
            {switch_button}
          </Link>
        </p>
      </div>
    </div>
  );
}}'''
        
        # Dashboard/App Pages
        else:
            return f'''import React from 'react';
import {{ LayoutDashboard, Users, FileText, Settings, Plus, Bell }} from 'lucide-react';

export default function {screen_name.replace(" ", "")}Page() {{
  return (
    <div className="min-h-screen bg-background flex text-foreground">
      {{/* Sidebar */}}
      <aside className="w-72 border-r border-white/5 p-8 flex flex-col fixed h-full bg-background/50 backdrop-blur-xl">
        <div className="flex items-center gap-3 mb-12">
          <div className="w-8 h-8 bg-primary rounded-lg shadow-lg shadow-primary/30" />
          <h1 className="text-xl font-black tracking-tighter">APP...</h1>
        </div>
        
        <nav className="flex-1 space-y-2">
          <div className="p-4 bg-primary/10 text-primary rounded-2xl flex items-center gap-3 font-bold">
            <LayoutDashboard size={20} /> {screen_name}
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

      {{/* Main Content */}}
      <main className="flex-1 ml-72">
        <header className="h-20 border-b border-white/5 px-12 flex items-center justify-between sticky top-0 bg-background/80 backdrop-blur-lg z-10">
          <h2 className="text-2xl font-black">{screen_name}</h2>
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
                Content for {screen_name} is being synchronized from the edge nodes. 
                Full visualization available in real-time.
              </p>
              <div className="mt-8 space-y-4">
                {{[1,2,3].map(i => (
                  <div key={{i}} className="flex items-center gap-4 p-4 border border-white/5 rounded-2xl bg-white/5">
                    <div className="w-10 h-10 bg-white/5 rounded-xl" />
                    <div className="flex-1">
                      <div className="font-bold text-sm">System Update Process #{{i}}</div>
                      <div className="text-xs opacity-40">Processed 2 mins ago</div>
                    </div>
                  </div>
                ))}}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}}'''

coder = AICoder()
print("TESTING LANDING PAGE FALLBACK...")
try:
    print(coder._create_fallback_page("Landing", "landing", "test"))
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")

print("\nTESTING LOGIN FALLBACK...")
try:
    print(coder._create_fallback_page("Login", "login", "test"))
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")

print("\nTESTING DASHBOARD FALLBACK...")
try:
    print(coder._create_fallback_page("Dashboard", "dashboard", "test"))
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
