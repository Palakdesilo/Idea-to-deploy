import json
import zipfile
import shutil
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from .llm_service import LLMService
from .ai_prompts import (
    PAGE_CODE_PROMPT,
    COMPONENT_LIBRARY_PROMPT,
    FASTAPI_ROUTE_PROMPT,
    SQLALCHEMY_MODEL_PROMPT,
    AUTH_SETUP_PROMPT,
    PROJECT_CONFIG_PROMPT,
    README_TEMPLATE_PROMPT
)

from .project_manager import ARTIFACTS_DIR

class AICoder:
    """
    Main orchestrator for generating full-stack applications from design artifacts.
    Converts wireframes, UI contracts, and architecture docs into deployable code.
    """
    
    def __init__(self):
        self.llm = LLMService()
    
    async def generate_full_stack_app(self, project_id: str, project_name: str, description: str) -> str:
        """
        Main entry point for code generation.
        Returns path to generated ZIP file.
        """
        print(f"AICoder: Starting full-stack generation for project {project_id}")
        
        # Setup directories
        artifacts_dir = ARTIFACTS_DIR / project_id
        code_dir = artifacts_dir / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        
        # Load design artifacts
        wireframes = self._load_json(artifacts_dir / "docs" / "wireframes.json")
        ui_contracts = self._load_json(artifacts_dir / "docs" / "ui_contracts.json")
        ui_design = self._load_json(artifacts_dir / "docs" / "ui_design.json")
        
        if not wireframes or not ui_contracts:
            print("AICoder: Missing wireframes or UI contracts, using fallback generation")
            wireframes = self._create_fallback_wireframes(description)
            ui_contracts = self._create_fallback_contracts(description)
        
        # Generate project structure
        frontend_dir = code_dir / "frontend"
        backend_dir = code_dir / "backend"
        
        # Phase 1: Generate Frontend
        print("AICoder: Generating frontend...")
        await self.generate_nextjs_app(frontend_dir, wireframes, ui_contracts, ui_design, description, project_name)
        
        # Phase 2: Generate Backend
        print("AICoder: Generating backend...")
        await self.generate_fastapi_backend(backend_dir, ui_contracts, description, project_name)
        
        # Phase 3: Generate Configuration Files
        print("AICoder: Generating configuration...")
        await self.generate_project_config(code_dir, project_name, description)
        
        # Phase 4: Package as ZIP
        print("AICoder: Packaging application...")
        zip_path = await self.package_application(code_dir, project_id, project_name)
        
        print(f"AICoder: Generation complete! ZIP at {zip_path}")
        return str(zip_path)
    
    async def generate_nextjs_app(self, output_dir: Path, wireframes: List[Dict], ui_contracts: Dict, ui_design: Dict, description: str, project_name: str):
        """Generate Next.js frontend application"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        app_dir = output_dir / "app"
        components_dir = output_dir / "components"
        lib_dir = output_dir / "lib"
        
        app_dir.mkdir(exist_ok=True)
        components_dir.mkdir(exist_ok=True)
        lib_dir.mkdir(exist_ok=True)
        
        # Extract design tokens for the prompt
        design_tokens = ui_design.get('design_tokens', {}) if ui_design else {}
        
        # Generate root layout
        await self._generate_root_layout(app_dir, project_name)
        
        # Generate global CSS
        await self._generate_global_css(app_dir, ui_design)
        
        # Index UI contracts by screen name for easy lookup
        contracts_map = {}
        if ui_contracts:
            contracts = ui_contracts.get('ui_contracts', []) if isinstance(ui_contracts, dict) else ui_contracts
            for c in contracts:
                contracts_map[c.get('screen', '').lower()] = c

        # Collect all routes for navigation
        all_routes = []
        for wf in wireframes.get('wireframes', []) if isinstance(wireframes, dict) else wireframes:
            s_name = wf.get('screen', 'Screen')
            s_key = wf.get('screenKey', s_name.lower().replace(' ', '-')).strip()
            
            route = "/"
            if s_key.lower() in ['landing', 'landingpage', 'home', 'index', 'landing-page']:
                route = "/"
            elif 'login' in s_key.lower() or 'register' in s_key.lower():
                route = f"/{s_key}"
            else:
                route = f"/{s_key}"
            
            all_routes.append({"name": s_name, "path": route})

        # Generate pages from wireframes
        pages_written = 0
        written_routes = set()
        
        for wf in wireframes.get('wireframes', []) if isinstance(wireframes, dict) else wireframes:
            screen_name = wf.get('screen', 'Screen')
            # More aggressive landing page detection
            screen_key = wf.get('screenKey', screen_name.lower().replace(' ', '-')).strip()
            
            # Find relevant contract
            relevant_contract = contracts_map.get(screen_name.lower(), {})
            
            # Generate page component
            page_code = await self.llm.generate_content(
                'PAGE_CODE',
                {
                    'idea': description,
                    'screen_name': screen_name,
                    'design_tokens': json.dumps(design_tokens, indent=2),
                    'wireframe': json.dumps(wf, indent=2),
                    'ui_contract': json.dumps(relevant_contract, indent=2),
                    'all_routes': json.dumps(all_routes, indent=2)
                },
                PAGE_CODE_PROMPT
            )
            
            # Clean code
            page_code = self._clean_code(page_code)
            
            # Validate
            if not page_code or len(page_code.strip()) < 100 or 'export default' not in page_code:
                print(f"AICoder: Invalid code for {screen_name}, using fallback")
                page_code = self._create_fallback_page(screen_name, screen_key, description)
            
            # Determine route path
            is_root = False
            # Aggressive root detection
            if screen_key.lower() in ['landing', 'landingpage', 'home', 'index', 'landing-page']:
                page_dir = app_dir
                is_root = True
            elif 'login' in screen_key.lower() or 'register' in screen_key.lower():
                page_dir = app_dir / "(auth)" / screen_key
            else:
                page_dir = app_dir / screen_key
            
            page_dir.mkdir(parents=True, exist_ok=True)
            target_file = page_dir / "page.tsx"
            
            # Write page.tsx
            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(page_code or "// Generation Failed")
                pages_written += 1
                written_routes.add(str(target_file.relative_to(app_dir)))
                print(f"AICoder: Wrote {screen_name} to {target_file}")
            except Exception as e:
                print(f"AICoder: Failed to write {target_file}: {e}")

        # SAFETY CHECK: If app/page.tsx was not written or is empty, force it
        root_page_file = app_dir / "page.tsx"
        needs_root_fallback = False
        if not root_page_file.exists():
            needs_root_fallback = True
        else:
            try:
                if root_page_file.stat().st_size < 100:
                    needs_root_fallback = True
            except Exception:
                needs_root_fallback = True
                
        if needs_root_fallback:
            print("AICoder: app/page.tsx missing or empty, forcing premium fallback Landing Page")
            try:
                fallback_root = self._create_fallback_page("Landing Page", "landing", description)
                with open(root_page_file, "w", encoding="utf-8") as f:
                    f.write(fallback_root)
            except Exception as e:
                print(f"AICoder: Critical failure writing root fallback: {e}")
                # Ultimate last resort
                with open(root_page_file, "w", encoding="utf-8") as f:
                    f.write("export default function Page() { return <div className='p-20 text-center font-bold'>Application Landing Page</div>; }")
        
        # Generate reusable components
        await self._generate_ui_components(components_dir, description)
        
        # Generate API client
        await self._generate_api_client(lib_dir)
    
    async def generate_fastapi_backend(self, output_dir: Path, ui_contracts: Dict, description: str, project_name: str):
        """Generate Python FastAPI backend"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create directory structure
        routes_dir = output_dir / "routes"
        models_dir = output_dir / "models"
        schemas_dir = output_dir / "schemas"
        
        routes_dir.mkdir(exist_ok=True)
        models_dir.mkdir(exist_ok=True)
        schemas_dir.mkdir(exist_ok=True)
        
        # Extract entities from UI contracts
        entities = self._extract_entities(ui_contracts)
        
        # Generate SQLAlchemy models
        models_code = await self.llm.generate_content(
            'SQLALCHEMY_MODEL',
            {
                'idea': description,
                'ui_contracts': json.dumps(ui_contracts, indent=2)
            },
            SQLALCHEMY_MODEL_PROMPT
        )
        
        models_code = self._clean_code(models_code)
        with open(models_dir / "models.py", "w", encoding="utf-8") as f:
            f.write(models_code)
        
        # Generate FastAPI routes for each entity
        for entity in entities:
            entity_name = entity['name']
            actions = entity.get('actions', [])
            data_fields = entity.get('data', [])
            
            route_code = await self.llm.generate_content(
                'FASTAPI_ROUTE',
                {
                    'idea': description,
                    'screen_name': entity.get('screen', entity_name),
                    'entity_name': entity_name,
                    'actions': json.dumps(actions),
                    'data_fields': json.dumps(data_fields)
                },
                FASTAPI_ROUTE_PROMPT
            )
            
            route_code = self._clean_code(route_code)
            filename = f"{entity_name.lower()}_routes.py"
            with open(routes_dir / filename, "w", encoding="utf-8") as f:
                f.write(route_code)
        
        # Generate authentication system
        await self._generate_auth_system(output_dir, description)
        
        # Generate database setup
        await self._generate_database_setup(output_dir)
        
        # Generate main.py
        await self._generate_main_py(output_dir, entities, project_name)
    
    async def generate_project_config(self, output_dir: Path, project_name: str, description: str):
        """Generate all configuration files using verified templates"""
        
        # 1. Frontend Configuration (hardcoded for reliability)
        frontend_dir = output_dir / "frontend"
        frontend_dir.mkdir(parents=True, exist_ok=True)
        
        package_json = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.1.0",
                "react": "^18",
                "react-dom": "^18",
                "lucide-react": "^0.300.0",
                "clsx": "^2.1.0",
                "tailwind-merge": "^2.2.0"
            },
            "devDependencies": {
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "autoprefixer": "^10.0.1",
                "postcss": "^8",
                "tailwindcss": "^3.3.0",
                "typescript": "^5"
            }
        }
        
        with open(frontend_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)
            
        tsconfig = {
            "compilerOptions": {
                "lib": ["dom", "dom.iterable", "esnext"],
                "allowJs": True,
                "skipLibCheck": True,
                "strict": True,
                "noEmit": True,
                "esModuleInterop": True,
                "module": "esnext",
                "moduleResolution": "bundler",
                "resolveJsonModule": True,
                "isolatedModules": True,
                "jsx": "preserve",
                "incremental": True,
                "plugins": [{"name": "next"}],
                "paths": {"@/*": ["./*"]}
            },
            "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
            "exclude": ["node_modules"]
        }
        
        with open(frontend_dir / "tsconfig.json", "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)
            
        with open(frontend_dir / "next.config.js", "w", encoding="utf-8") as f:
            f.write("/** @type {import('next').NextConfig} */\nconst nextConfig = {};\n\nmodule.exports = nextConfig;\n")
            
        with open(frontend_dir / "tailwind.config.ts", "w", encoding="utf-8") as f:
            f.write("""import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        surface: "var(--surface)",
        accent: "var(--accent)",
      },
    },
  },
  plugins: [],
  darkMode: 'class',
};
export default config;
""")

        with open(frontend_dir / "postcss.config.js", "w", encoding="utf-8") as f:
            f.write("module.exports = {\n  plugins: {\n    tailwindcss: {},\n    autoprefixer: {},\n  },\n};\n")

        # 2. Backend Configuration
        backend_dir = output_dir / "backend"
        backend_dir.mkdir(parents=True, exist_ok=True)
        
        requirements = """fastapi==0.109.0
uvicorn==0.27.0
sqlalchemy==2.0.25
pydantic==2.6.0
pydantic-settings==2.1.0
python-dotenv==1.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
psycopg2-binary==2.9.9
asyncpg==0.29.0
alembic==1.13.1
"""
        with open(backend_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write(requirements)
            
        # 3. Docker Configuration
        docker_compose = f"""version: '3.8'

services:
  web:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api
    depends_on:
      - api

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/{project_name.lower().replace(" ", "_")}
      - SECRET_KEY=supersecretkey123
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB={project_name.lower().replace(" ", "_")}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
        with open(output_dir / "docker-compose.yml", "w", encoding="utf-8") as f:
            f.write(docker_compose)

        # Dockerfiles
        with open(frontend_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write("""FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
""")

        with open(backend_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write("""FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""")
            
        with open(output_dir / ".gitignore", "w", encoding="utf-8") as f:
            f.write("node_modules/\n.next/\n__pycache__/\n*.pyc\n.env\n.DS_Store\n")

        # Generate README (still using LLM for custom instructions)
        readme_content = await self.llm.generate_content(
            'README_TEMPLATE',
            {
                'idea': description,
                'project_name': project_name
            },
            README_TEMPLATE_PROMPT
        )
        
        with open(output_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
    
    async def package_application(self, code_dir: Path, project_id: str, project_name: str) -> Path:
        """Package the generated code as a ZIP file"""
        artifacts_dir = code_dir.parent
        # Sanitize project name: remove newlines, special chars, limit length
        safe_name = re.sub(r'[^\w\s-]', '', project_name.replace('\n', ' ').replace('\r', ''))
        safe_name = safe_name.strip().lower().replace(' ', '-')[:50]
        zip_filename = f"{safe_name}-generated.zip"
        zip_path = artifacts_dir / zip_filename
        
        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in code_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(code_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
    
    # Helper Methods
    
    def _load_json(self, filepath: Path) -> Optional[Dict]:
        """Load JSON file safely"""
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"AICoder: Error loading {filepath}: {e}")
        return None
    
    def _clean_code(self, code: str) -> str:
        """Remove markdown fences and clean generated code"""
        # Remove markdown code fences
        code = re.sub(r'^```[\w]*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        
        # Remove conversational or artifact headers leaked by LLM
        # Matches: "# PAGE_CODE Document...", "# FIX_ERROR...", "Here is..."
        code = re.sub(r'(?i)^(?:#\s*[A-Z_]+\s+Document|#\s*FIX_ERROR|#\s*TASK|Here is).*?(\n|$)', '', code)
        
        code = code.strip()
        return code
    
    def _extract_entities(self, ui_contracts: Dict) -> List[Dict]:
        """Extract unique entities from UI contracts"""
        entities = []
        seen = set()
        
        contracts = ui_contracts.get('ui_contracts', []) if isinstance(ui_contracts, dict) else ui_contracts
        
        for contract in contracts:
            # Try to infer entity name from screen name
            screen = contract.get('screen', '')
            actions = contract.get('actions', [])
            data = contract.get('data', [])
            
            # Skip auth screens
            if any(x in screen.lower() for x in ['login', 'register', 'auth']):
                continue
            
            # Infer entity name
            entity_name = screen.split()[0] if ' ' in screen else screen
            entity_name = entity_name.replace('Screen', '').replace('Page', '').strip()
            
            if entity_name and entity_name not in seen:
                seen.add(entity_name)
                entities.append({
                    'name': entity_name,
                    'screen': screen,
                    'actions': actions,
                    'data': data
                })
        
        # Always include User entity
        if 'User' not in seen:
            entities.insert(0, {
                'name': 'User',
                'screen': 'User Management',
                'actions': ['Create', 'Read', 'Update', 'Delete'],
                'data': ['email', 'name', 'password']
            })
        
        return entities
    
    def _parse_multi_file_response(self, content: str) -> Dict[str, str]:
        """Parse LLM response containing multiple files"""
        files = {}
        current_file = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('### '):
                # Save previous file
                if current_file:
                    files[current_file] = '\n'.join(current_content).strip()
                
                # Start new file
                current_file = line.replace('### ', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Save last file
        if current_file:
            files[current_file] = '\n'.join(current_content).strip()
        
        return files
    
    def _create_fallback_wireframes(self, description: str) -> List[Dict]:
        """Create basic wireframes if none exist"""
        return [
            {"screen": "Landing Page", "screenKey": "landing", "layout": []},
            {"screen": "Login", "screenKey": "login", "layout": []},
            {"screen": "Register", "screenKey": "register", "layout": []},
            {"screen": "Dashboard", "screenKey": "dashboard", "layout": []}
        ]
    
    def _create_fallback_contracts(self, description: str) -> Dict:
        """Create basic UI contracts if none exist"""
        return {
            "ui_contracts": [
                {"screen": "Dashboard", "actions": ["View", "Create"], "data": ["title", "content"]}
            ]
        }
    
    def _create_fallback_page(self, screen_name: str, screen_key: str, description: str) -> str:
        """Create a premium, design-aware fallback page component when LLM generation fails"""
        screen_lower = screen_name.lower()
        
        # Landing Page Template
        if any(k in screen_lower or k in screen_key.lower() for k in ['landing', 'home', 'hero', 'index']) or screen_key == '':
            template = '''import React from 'react';
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
              __DESCRIPTION__
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
}'''
            return template.replace('__DESCRIPTION__', description)
        
        # Auth Pages (Login/Register)
        elif 'login' in screen_lower or 'register' in screen_lower:
            is_register = 'register' in screen_lower
            title = "Create Account" if is_register else "Welcome Back"
            button_text = "Sign Up" if is_register else "Sign In"
            switch_text = "Already have an account?" if is_register else "Don't have an account?"
            switch_link = "login" if is_register else "register"
            switch_button = "Sign In" if is_register else "Sign Up"
            
            confirm_field = '''
          <div className="space-y-2">
            <label className="text-[11px] font-black uppercase tracking-widest opacity-50">Confirm Password</label>
            <input type="password"  className="w-full px-6 py-4 bg-white/5 border border-white/10 rounded-2xl focus:border-primary outline-none transition-all" placeholder="••••••••" />
          </div>''' if is_register else ''
            
            template = '''import React from 'react';
import Link from 'next/link';

export default function __COMPONENT_NAME__Page() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6 text-foreground">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[20%] left-[20%] w-[500px] h-[500px] bg-primary/20 blur-[120px] rounded-full" />
        <div className="absolute bottom-[20%] right-[20%] w-[500px] h-[500px] bg-accent/10 blur-[120px] rounded-full" />
      </div>
      
      <div className="max-w-md w-full card-premium p-12 relative z-10 backdrop-blur-2xl">
        <div className="text-center mb-10">
          <div className="w-12 h-12 bg-primary rounded-xl mx-auto mb-6 shadow-lg shadow-primary/40" />
          <h1 className="text-4xl font-black tracking-tight mb-2">__TITLE__</h1>
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
          </div>__CONFIRM_FIELD__
          <button type="submit" className="w-full bg-primary text-white py-4 rounded-2xl font-bold hover:brightness-110 transition-all shadow-xl shadow-primary/20">
            __BUTTON_TEXT__
          </button>
        </form>
        
        <p className="text-center text-sm mt-8 opacity-60">
          __SWITCH_TEXT__
          <Link href="/__SWITCH_LINK__" className="text-primary font-black hover:underline">
            __SWITCH_BUTTON__
          </Link>
        </p>
      </div>
    </div>
  );
}'''
            return template.replace('__COMPONENT_NAME__', screen_name.replace(" ", "")) \
                           .replace('__TITLE__', title) \
                           .replace('__BUTTON_TEXT__', button_text) \
                           .replace('__SWITCH_TEXT__', switch_text) \
                           .replace('__SWITCH_LINK__', switch_link) \
                           .replace('__SWITCH_BUTTON__', switch_button) \
                           .replace('__CONFIRM_FIELD__', confirm_field)
        
        # Dashboard/App Pages
        else:
            template = '''import React from 'react';
import Link from 'next/link';
import { LayoutDashboard, Users, FileText, Settings, Plus, Bell } from 'lucide-react';

export default function __COMPONENT_NAME__Page() {
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
            <LayoutDashboard size={20} /> __SCREEN_NAME__
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
          <h2 className="text-2xl font-black">__SCREEN_NAME__</h2>
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
                Content for __SCREEN_NAME__ is being synchronized from the edge nodes. 
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
}'''
            return template.replace('__COMPONENT_NAME__', screen_name.replace(" ", "")) \
                           .replace('__SCREEN_NAME__', screen_name)
    
    
    async def _generate_root_layout(self, app_dir: Path, project_name: str):
        """Generate Next.js root layout"""
        # Sanitize project name to prevent multi-line strings breaking the JS template
        safe_project_name = project_name.replace('\n', ' ').replace('\r', ' ').strip()
        
        layout_code = f"""import type {{ Metadata }} from 'next'
import './globals.css'

export const metadata: Metadata = {{
  title: '{safe_project_name}',
  description: 'Generated by Idea-to-Deploy',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body className="min-h-screen bg-background antialiased">
        {{children}}
      </body>
    </html>
  )
}}
"""
        with open(app_dir / "layout.tsx", "w", encoding="utf-8") as f:
            f.write(layout_code)
    
    async def _generate_global_css(self, app_dir: Path, ui_design: Dict = None):
        """Generate global CSS with Tailwind and Design Tokens"""
        
        # Default premium tokens if none provided
        tokens = {
            "palette": {
                "background": "#0F172A",
                "surface": "#1E293B",
                "primary": "#8B5CF6",
                "foreground": "#F8FAFC",
                "accent": "#F472B6"
            }
        }
        
        if ui_design and 'design_tokens' in ui_design:
            tokens = ui_design['design_tokens']
        
        palette = tokens.get('palette', tokens.get('colors', {}))
        
        css_content = f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --background: {palette.get('background', '#0F172A')};
  --foreground: {palette.get('foreground', palette.get('text_main', '#F8FAFC'))};
  --primary: {palette.get('primary', '#8B5CF6')};
  --surface: {palette.get('surface', palette.get('card_bg', '#1E293B'))};
  --accent: {palette.get('accent', '#F472B6')};
}}

body {{
  background: var(--background);
  color: var(--foreground);
  font-family: 'Inter', sans-serif;
}}

.glass {{
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
}}

.card-premium {{
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
    border-radius: 24px;
    border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.3s ease;
}}

.card-premium:hover {{
    border-color: rgba(255,255,255,0.1);
    transform: translateY(-2px);
}}

.text-gradient {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.btn-primary {{
    background: var(--primary);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-weight: 700;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}}

.btn-primary:hover {{
    transform: translateY(-1px);
    filter: brightness(1.1);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}}

.animate-float {{
    animation: float 6s ease-in-out infinite;
}}

.animate-fade-in {{
    animation: fadeIn 0.5s ease-out forwards;
}}

.animate-slide-up {{
    animation: slideUp 0.5s ease-out forwards;
}}

@keyframes float {{
    0%, 100% {{ transform: translateY(0); }}
    50% {{ transform: translateY(-20px); }}
}}

@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}

@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
"""
        with open(app_dir / "globals.css", "w", encoding="utf-8") as f:
            f.write(css_content)
    
    async def _generate_ui_components(self, components_dir: Path, description: str):
        """Generate reusable UI components"""
        ui_dir = components_dir / "ui"
        ui_dir.mkdir(exist_ok=True)
        
        component_types = ['Button', 'Card', 'Input']
        
        for comp_type in component_types:
            code = await self.llm.generate_content(
                'COMPONENT_LIBRARY',
                {
                    'idea': description,
                    'component_type': comp_type
                },
                COMPONENT_LIBRARY_PROMPT
            )
            
            code = self._clean_code(code)
            filename = f"{comp_type}.tsx"
            with open(ui_dir / filename, "w", encoding="utf-8") as f:
                f.write(code)
    
    async def _generate_api_client(self, lib_dir: Path):
        """Generate API client utility with auth support"""
        api_client_code = """const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Get token from localStorage if available
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers = new Headers({
    'Content-Type': 'application/json',
    ...options.headers,
  });
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  if (response.status === 401) {
    // Handle unauthorized - clear token and redirect
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      if (window.location.pathname !== '/login') {
          window.location.href = '/login';
      }
    }
  }
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API Error: ${response.statusText}`);
  }
  
  return response.json();
}

export const api = {
  get: (endpoint: string) => apiRequest(endpoint),
  post: (endpoint: string, data: any) => apiRequest(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint: string, data: any) => apiRequest(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint: string) => apiRequest(endpoint, { method: 'DELETE' }),
};
"""
        with open(lib_dir / "api.ts", "w", encoding="utf-8") as f:
            f.write(api_client_code)
    
    async def _generate_auth_system(self, output_dir: Path, description: str):
        """Generate authentication system"""
        auth_content = await self.llm.generate_content(
            'AUTH_SETUP',
            {'idea': description},
            AUTH_SETUP_PROMPT
        )
        
        files = self._parse_multi_file_response(auth_content)
        
        for filename, content in files.items():
            content = self._clean_code(content)
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)
    
    async def _generate_database_setup(self, output_dir: Path):
        """Generate database configuration"""
        db_code = """from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# TODO: For production, use PostgreSQL
# engine = create_engine(DATABASE_URL)

# For development/safety, use SQLite by default or handle connection errors
try:
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
    )
except Exception as e:
    print(f"DB Connection failed: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    if engine is None:
        raise Exception("Database not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
        with open(output_dir / "database.py", "w", encoding="utf-8") as f:
            f.write(db_code)
    
    async def _generate_main_py(self, output_dir: Path, entities: List[Dict], project_name: str):
        """Generate FastAPI main.py entry point"""
        # Build router imports
        router_imports = "\n".join([
            f"from routes.{entity['name'].lower()}_routes import router as {entity['name'].lower()}_router"
            for entity in entities
        ])
        
        # Build router includes
        router_includes = "\n".join([
            f"app.include_router({entity['name'].lower()}_router)"
            for entity in entities
        ])
        
        main_code = f"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
try:
    from auth_routes import router as auth_router
except ImportError:
    auth_router = None
{router_imports}

# Create database tables
if engine:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{project_name} API",
    description="Generated by Idea-to-Deploy",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if auth_router:
    app.include_router(auth_router)

{router_includes}

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name} API"}}

@app.get("/health")
async def health():
    return {{"status": "healthy"}}
"""
        with open(output_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_code)
