import json
import re
from typing import Dict, Any, List
from .project_manager import ProjectManager, ARTIFACTS_DIR
from .llm_service import LLMService
from .ai_prompts import PAGE_CODE_PROMPT

class AIBuilder:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.llm = LLMService()

    def _clean_code(self, raw: str) -> str:
        """Strip markdown code blocks aggressively"""
        import re
        if raw.strip() == "Limit Exists":
            return "# Generation failed due to AI rate limits. Please try again."
        
        # Look for content between triple backticks
        match = re.search(r'```(?:\w+)?\n?(.*?)\n?```', raw, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback if no backticks but looks like code
        return raw.strip()

    async def build_project(self, project_id: str, description: str) -> Dict[str, Any]:
        docs = await self.project_manager.get_docs(project_id)
        visuals = await self.project_manager.get_visuals(project_id)
        
        # 1. Identify Core Sources
        functional_doc = next((d for d in docs if d.category == 'REQUIREMENTS'), None)
        architecture_doc = next((d for d in docs if d.category == 'ARCHITECTURE'), None)
        uiux_doc = next((d for d in docs if d.category == 'UI_UX'), None)

        # 2. Extract Data for Generation
        # Features from Requirements
        features = []
        if functional_doc:
            matches = re.findall(r'- \*\*(.*?)\*\*', functional_doc.content)
            features = [m.replace('- **', '').replace('**', '') for m in matches] if matches else []

        # Screens from Wireframe JSONs (Primary Source of Structure)
        screens_map = {} # screen_name -> json_data
        json_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "json"
        if json_dir.exists():
            for json_file in json_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        screens_map[data.get('screen_name', json_file.stem).lower()] = data
                except: pass
        
        # Fallback to visuals.json if directory scan found nothing (legacy/different structure)
        if not screens_map:
            for v in visuals:
                v_type = v.get('type')
                v_path = v.get('localPath')
                if (v_type == 'WIRE_JSON' or v_type == 'wireframe_json') and v_path:
                    json_path = Path(v_path)
                    if json_path.exists():
                        try:
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                screens_map[v.get('screenName', 'unknown').lower()] = data
                        except: pass
        
        screen_names = list(screens_map.keys())
        all_routes = [f"/{s.replace(' ', '-').lower()}" for s in screen_names]
        if 'home feed' in screen_names: all_routes.append('/')

        # 3. Generate Backend Models & Logic (FastAPI)
        ui_contracts_summary = "\n".join([f"- {s}: {list(data.get('components', []))}" for s, data in screens_map.items()])
        
        from .ai_prompts import (
            SQLALCHEMY_MODEL_PROMPT, 
            AUTH_SETUP_PROMPT, 
            FASTAPI_ROUTE_PROMPT, 
            README_TEMPLATE_PROMPT, 
            COMPONENT_LIBRARY_PROMPT
        )

        # Generate SQL Models
        raw_models = await self.llm.generate_content('SQL_MODELS', {
            "idea": description,
            "ui_contracts": ui_contracts_summary
        }, SQLALCHEMY_MODEL_PROMPT)
        models_code = self._clean_code(raw_models)

        # Generate Auth System
        raw_auth = await self.llm.generate_content('AUTH_SETUP', {
            "idea": description
        }, AUTH_SETUP_PROMPT)
        # auth prompt returns 3 blocks
        auth_blocks = {}
        current_file = None
        for line in raw_auth.split('\n'):
            if line.startswith('### '):
                current_file = line.replace('### ', '').strip()
                auth_blocks[current_file] = ""
            elif current_file:
                auth_blocks[current_file] += line + "\n"
        
        for k, v in auth_blocks.items(): auth_blocks[k] = self._clean_code(v)

        # Assemble Files List
        files = []

        # Root Configs
        files.append({ "path": "package.json", "content": json.dumps({"name": "app", "workspaces": ["apps/*"], "scripts": {"dev": "turbo run dev"}}, indent=2) })
        files.append({ "path": "turbo.json", "content": json.dumps({"pipeline": {"dev": {"cache": False, "persistent": True}}}, indent=2) })
        
        # --- API FILES ---
        files.append({ "path": "apps/api/requirements.txt", "content": "fastapi\nuvicorn\nsqlalchemy\npsycopg2-binary\npydantic\npython-dotenv\npasslib[bcrypt]\npython-jose[cryptography]" })
        files.append({ "path": "apps/api/database.py", "content": "from sqlalchemy import create_engine\nfrom sqlalchemy.ext.declarative import declarative_base\nfrom sqlalchemy.orm import sessionmaker\nSQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'\nBase = declarative_base()" })
        files.append({ "path": "apps/api/models.py", "content": models_code })
        
        # Auth Files
        files.append({ "path": "apps/api/auth.py", "content": auth_blocks.get('auth.py', '# Auth missing') })
        files.append({ "path": "apps/api/auth_routes.py", "content": auth_blocks.get('auth_routes.py', '# Auth routes missing') })
        files.append({ "path": "apps/api/dependencies.py", "content": auth_blocks.get('dependencies.py', '# Deps missing') })

        # Entity Routers
        # Extract entities from models or docs (simplified: generate one main router for now)
        raw_router = await self.llm.generate_content('API_ROUTER', {
            "idea": description,
            "screen_name": "Main",
            "entity_name": "Entity",
            "actions": "All requirements",
            "data_fields": "As per models"
        }, FASTAPI_ROUTE_PROMPT)
        files.append({ "path": "apps/api/routers/main.py", "content": self._clean_code(raw_router) })

        # API Main
        files.append({ "path": "apps/api/main.py", "content": """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from routers.main import router as main_router

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(main_router, prefix='/api', tags=['api'])

@app.get('/health')
def health(): return {'status': 'ok'}
""" })

        # --- WEB FILES ---
        files.append({ "path": "apps/web/package.json", "content": json.dumps({
            "name": "web",
            "version": "0.1.0",
            "private": True,
            "scripts": { "dev": "next dev", "build": "next build", "start": "next start" },
            "dependencies": {
                "next": "14.2.3",
                "react": "^18",
                "react-dom": "^18",
                "lucide-react": "latest",
                "framer-motion": "latest",
                "react-hook-form": "latest",
                "clsx": "latest",
                "tailwind-merge": "latest"
            },
            "devDependencies": {
                "typescript": "^5",
                "@types/node": "^20",
                "@types/react": "^18",
                "@types/react-dom": "^18",
                "postcss": "^8",
                "tailwindcss": "^3.4.1"
            }
        }, indent=2) })
        files.append({ "path": "apps/web/next.config.mjs", "content": "/** @type {import('next').NextConfig} */\nconst nextConfig = {};\nexport default nextConfig;" })
        files.append({ "path": "apps/web/tailwind.config.ts", "content": "import type { Config } from 'tailwindcss';\nconst config: Config = { content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'], theme: { extend: {} }, plugins: [] };\nexport default config;" })
        files.append({ "path": "apps/web/postcss.config.js", "content": "module.exports = { plugins: { tailwindcss: {}, autoprefixer: {}, }, };" })
        
        # Tailwind Infrastructure
        files.append({ "path": "apps/web/app/globals.css", "content": "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n\n:root {\n  --foreground-rgb: 255, 255, 255;\n  --background-start-rgb: 15, 23, 42;\n  --background-end-rgb: 2, 6, 23;\n}\n\nbody {\n  color: rgb(var(--foreground-rgb));\n  background: linear-gradient(to bottom, transparent, rgb(var(--background-end-rgb))) rgb(var(--background-start-rgb));\n  min-height: 100vh;\n}\n" })
        
        files.append({ "path": "apps/web/app/layout.tsx", "content": """import './globals.css';
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'E-commerce Platform',
  description: 'Premium AI-generated e-commerce experience',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
""" })

        # Component Library
        raw_comp = await self.llm.generate_content('COMP_LIB', {
            "idea": description,
            "component_type": "Main Library"
        }, COMPONENT_LIBRARY_PROMPT)
        files.append({ "path": "apps/web/components/UI.tsx", "content": self._clean_code(raw_comp) })
        
        # API Client helper
        files.append({ "path": "apps/web/lib/api.ts", "content": """
const BASE_URL = 'http://localhost:8080';
export const api = {
    get: (url: string) => fetch(`${BASE_URL}${url}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()),
    post: (url: string, data: any) => fetch(`${BASE_URL}${url}`, { 
        method: 'POST', 
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify(data)
    }).then(r => r.json())
};
""" })

        # App Pages
        for screen_name, json_data in screens_map.items():
            slug = screen_name.replace(' ', '-').lower()
            is_home = 'home' in screen_name or 'welcome' in screen_name
            
            raw_page = await self.llm.generate_content('PAGE_CODE', {
                "idea": description,
                "screen_name": screen_name,
                "design_tokens": "{'primary': '#0f172a', 'secondary': '#3b82f6', 'radius': '1rem'}",
                "all_routes": json.dumps(all_routes),
                "wireframe": json.dumps(json_data, indent=2),
                "ui_contract": "Use /auth and /api endpoints"
            }, PAGE_CODE_PROMPT)
            
            path = "apps/web/app/page.tsx" if is_home else f"apps/web/app/{slug}/page.tsx"
            files.append({ "path": path, "content": self._clean_code(raw_page) })

        # Readme
        raw_readme = await self.llm.generate_content('README', { "idea": description, "project_name": description.title(), "project_id": project_id }, README_TEMPLATE_PROMPT)
        files.append({ "path": "README.md", "content": self._clean_code(raw_readme) })

        # --- ZIP PACKAGING ---
        # We'll use a simple zipfile approach to match AICoder's output format
        import zipfile
        import io
        
        # We'll do this in the ProjectManager.save_build_result or here?
        # Better to do it here and include it in the build_result or let ProjectManager handle it.
        # Given main.py expects a file on disk for download, ProjectManager should handle the zip creation.
        
        return {
            "projectId": project_id,
            "files": files,
            "stats": { "fileCount": len(files), "totalLines": sum([len(f["content"].splitlines()) for f in files]) }
        }
    