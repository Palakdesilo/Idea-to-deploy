import json
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from .project_manager import ProjectManager, ARTIFACTS_DIR
from .llm_service import LLMService
from .validator import ValidationLayer
from .ai_prompts import (
    PAGE_CODE_PROMPT,
    DESIGN_SYSTEM_PROMPT,
    BACKEND_ACTION_PROMPT,
    SQLALCHEMY_MODEL_PROMPT,
    AUTH_SETUP_PROMPT,
    README_TEMPLATE_PROMPT,
    COMPONENT_LIBRARY_PROMPT,
    PROJECT_PLAN_PROMPT
)

class AIBuilder:
    def __init__(self):
        self.project_manager = ProjectManager()
        self.llm = LLMService()
        self.validator = ValidationLayer()

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

    async def orchestrate_build(self, project_id: str, description: str) -> Dict[str, Any]:
        """
        Orchestrates the sequential build process following the 8-step workflow:
        1. Input Freezing (Spec) -> 2. Design System -> 3. Backend -> 4. Frontend -> 5. Validation
        """
        
        # 1. INPUT FREEZING & MASTER SPEC GENERATION
        self._log_step("Generating Master Project Specification...")
        project_spec = await self._generate_project_spec(description)
        
        # 2. GATHER INPUTS & CONTRACTS
        docs = await self.project_manager.get_docs(project_id)
        visuals = await self.project_manager.get_visuals(project_id)
        
        # Use spec as the primary source of truth, fallback to extraction from visuals
        screens_map = self._extract_screens(project_id, visuals)
        actions_map = project_spec.get("features", {}).get("api_actions", [])
        
        # Convert actions list to map if needed for downstream
        if isinstance(actions_map, list):
            actions_dict = {}
            for action in actions_map:
                if isinstance(action, dict):
                    name = action.get("name", "action")
                    actions_dict[name] = action
                else:
                    actions_dict[str(action)] = {"description": str(action)}
            actions_map = actions_dict

        if not actions_map:
             actions_map = self._extract_actions(screens_map)
        
        # 3. VALIDATE DESIGN
        self._log_step("Validating Design Inputs...")
        if not self.validator.validate_design(actions_map, list(screens_map.keys()), []):
            # We continue even if validation warns, but log it
            self._log_step("Design Validation Warning: " + ", ".join(self.validator.get_errors()))

        # 4. GENERATE CANONICAL DESIGN SYSTEM
        self._log_step("Generating Canonical Design System...")
        design_system = await self._generate_design_system(description)
        
        # 5. GENERATE BACKEND (Service Architecture & Implementation)
        self._log_step("Generating Backend Layer...")
        backend_files = await self._generate_backend(description, actions_map, design_system, screens_map, project_spec)
        
        # 6. VALIDATE BACKEND
        endpoints = self._extract_endpoints_from_files(backend_files)
        self.validator.validate_backend(endpoints, ["MockController"], [])

        # 7. GENERATE FRONTEND (Component Library & Screen Assembly)
        self._log_step("Generating Frontend Layer...")
        frontend_files = await self._generate_frontend(description, screens_map, design_system, backend_files, project_spec)

        # 8. VALIDATE FRONTEND
        self.validator.validate_frontend(["react"], [f"/{k}" for k in screens_map.keys()], endpoints)

        # 9. ASSEMBLE PROJECT
        all_files = backend_files + frontend_files
        
        # Add Spec and Design System Files
        all_files.append({
            "path": "project-spec.json",
            "content": json.dumps(project_spec, indent=2)
        })
        all_files.append({
            "path": "design-system.json",
            "content": json.dumps(design_system, indent=2)
        })

        # Add Root Configs (package.json, etc.)
        all_files.extend(self._generate_root_configs())
        
        # Add Readme
        readme = await self._generate_readme(description, project_id)
        all_files.append({"path": "README.md", "content": readme})
        
        return {
            "projectId": project_id,
            "files": all_files,
            "projectSpec": project_spec,
            "designSystem": design_system,
            "status": "SUCCESS",
            "stats": { "fileCount": len(all_files) }
        }

    # --- Helper Generation Methods ---

    def _extract_screens(self, project_id: str, visuals: List[Dict]) -> Dict[str, Any]:
        """Extract screen data from artifacts"""
        screens_map = {}
        json_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "json"
        if json_dir.exists():
            for json_file in json_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        screens_map[data.get('screen_name', json_file.stem).lower()] = data
                except: pass
        
        if not screens_map:
            # Fallback to visuals list
            for v in visuals:
                if v.get('type') in ['WIRE_JSON', 'wireframe_json'] and v.get('localPath'):
                    try:
                        with open(v['localPath'], 'r') as f:
                            data = json.load(f)
                            screens_map[v.get('screenName', 'unknown').lower()] = data
                    except: pass
        
        # If still empty, create at least a Home screen
        if not screens_map:
            screens_map['home'] = {"screen_name": "Home", "components": []}
            
        return screens_map

    def _extract_actions(self, screens_map: Dict[str, Any]) -> Dict[str, Any]:
        """Derive potential API actions from screen components"""
        # This is a simplification. In a real system, we'd parse buttons/forms.
        actions = {}
        for name, data in screens_map.items():
            # Assume every screen might need a READ action, and forms need WRITE
            slug = name.replace(' ', '-').lower()
            actions[f"get_{slug}"] = {"method": "GET", "endpoint": f"/api/{slug}"}
            # Heuristic: if 'login' or 'register' in name, add auth actions
            if 'login' in slug:
                 actions['login'] = {"method": "POST", "endpoint": "/api/auth/login"}
            if 'register' in slug or 'signup' in slug:
                 actions['register'] = {"method": "POST", "endpoint": "/api/auth/register"}
        return actions

    async def _generate_project_spec(self, idea: str) -> Dict[str, Any]:
        """Generate the master project specification"""
        raw = await self.llm.generate_content('PROJECT_SPEC', {"idea": idea}, PROJECT_PLAN_PROMPT)
        try:
            return json.loads(self._clean_code(raw))
        except:
             # Fallback spec
             return {
                 "features": {"core_features": [], "screens": [], "api_actions": []},
                 "tech_stack": {"frontend": "Next.js", "backend": "FastAPI", "database": "PostgreSQL"},
                 "system_contracts": {"api_structure": {}, "database_schema": {}}
             }

    async def _generate_design_system(self, idea: str) -> Dict[str, Any]:
        raw = await self.llm.generate_content('DESIGN_TOKENS', {"idea": idea}, DESIGN_SYSTEM_PROMPT)
        cleaned = self._clean_code(raw)
        try:
            return json.loads(cleaned)
        except:
            # Fallback default
            return {
                "theme": {
                    "colors": {
                        "primary": "#2563eb", "secondary": "#475569", "background": "#0f172a", "foreground": "#f8fafc"
                    },
                    "borderRadius": "0.5rem"
                }
            }

    async def _generate_backend(self, idea: str, actions: Dict, design_system: Dict, screens_map: Dict, project_spec: Dict) -> List[Dict]:
        files = []
        project_spec_str = json.dumps(project_spec, indent=2)
        
        # 1. Models
        ui_summary = "\n".join([f"- {s}" for s in screens_map.keys()])
        raw_models = await self.llm.generate_content('SQL_MODELS', {
            "idea": idea, 
            "ui_contracts": ui_summary,
            "project_spec": project_spec_str
        }, SQLALCHEMY_MODEL_PROMPT)
        files.append({ "path": "apps/api/models.py", "content": self._clean_code(raw_models) })
        
        # 2. Auth
        raw_auth = await self.llm.generate_content('AUTH_SETUP', {"idea": idea}, AUTH_SETUP_PROMPT)
        auth_blocks = self._parse_multi_file_response(raw_auth)
        files.append({ "path": "apps/api/auth.py", "content": auth_blocks.get('auth.py', '# Auth missing') })
        files.append({ "path": "apps/api/auth_routes.py", "content": auth_blocks.get('auth_routes.py', '# Auth routes missing') })
        files.append({ "path": "apps/api/dependencies.py", "content": auth_blocks.get('dependencies.py', '# Deps missing') })

        # 3. Main Router (using new Actions Prompt logic or strictly following actions map)
        # Using BACKEND_ACTION_PROMPT to generate a consolidated router for defined actions
        actions_str = json.dumps(actions, indent=2)
        design_sys_str = json.dumps(design_system)
        
        raw_router = await self.llm.generate_content('API_ROUTER', {
            "actions": actions_str,
            "design_system": design_sys_str,
            "project_spec": project_spec_str
        }, BACKEND_ACTION_PROMPT)
        
        files.append({ "path": "apps/api/routers/main.py", "content": self._clean_code(raw_router) })
        
        # 4. Standard Backend Configs
        files.append({ "path": "apps/api/requirements.txt", "content": "fastapi\nuvicorn\nsqlalchemy\npsycopg2-binary\npydantic\npython-dotenv\npasslib[bcrypt]\npython-jose[cryptography]" })
        files.append({ "path": "apps/api/database.py", "content": "from sqlalchemy import create_engine\nfrom sqlalchemy.ext.declarative import declarative_base\nSQLALCHEMY_DATABASE_URL = 'sqlite:///./sql_app.db'\nBase = declarative_base()\nengine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False})" })
        files.append({ "path": "apps/api/create_tables.py", "content": "from database import engine, Base\nfrom models import *\n\nprint('Creating tables...')\nBase.metadata.create_all(bind=engine)\nprint('Tables created successfully.')" })
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

        files.append({ "path": "apps/api/view_db.py", "content": """
import sqlite3
import os
import sys

def get_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in cursor.fetchall()]

def view_table(cursor, table_name):
    print(f"\\n--- Contents of '{table_name}' table ---")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    if not columns_info:
        print(f"Table '{table_name}' does not exist or has no columns.")
        return

    columns = [col[1] for col in columns_info]
    
    # Get data
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print("No Records Found.")
    else:
        # Print Header
        header = " | ".join(columns)
        print(header)
        print("-" * len(header))
        
        # Print Rows
        for row in rows:
            print(" | ".join(str(item) for item in row))

def main():
    db_path = os.path.join(os.path.dirname(__file__), 'sql_app.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return

    print(f"--- Connecting to {db_path} ---")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        tables = get_tables(cursor)
        
        if not tables:
            print("No tables found in the database.")
            return

        target_table = None
        
        # If argument provided, use it
        if len(sys.argv) > 1:
            target_table = sys.argv[1]
        
        # If no argument or invalid table, ask user
        if not target_table or target_table not in tables:
            if target_table:
                print(f"Table '{target_table}' not found.")
            
            print("\\nAvailable tables:")
            for i, table in enumerate(tables):
                print(f"{i + 1}. {table}")
            
            try:
                choice = input("\\nEnter table number (or table name) to view: ")
                if choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(tables):
                        target_table = tables[idx]
                else:
                    if choice in tables:
                        target_table = choice
            except (KeyboardInterrupt, EOFError):
                return

        if target_table:
            view_table(cursor, target_table)
        else:
            print("Invalid selection.")

    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("\\nConnection closed.")

if __name__ == "__main__":
    main()
""" })
        
        return files

    async def _generate_frontend(self, idea: str, screens_map: Dict, design_system: Dict, backend_files: List[Dict], project_spec: Dict) -> List[Dict]:
        files = []
        design_tokens_str = json.dumps(design_system)
        
        # 1. Component Library
        raw_comp = await self.llm.generate_content('COMP_LIB', {"idea": idea, "component_type": "Main Library"}, COMPONENT_LIBRARY_PROMPT)
        files.append({ "path": "apps/web/components/UI.tsx", "content": self._clean_code(raw_comp) })
        
        # 2. Pages
        all_routes = [f"/{s.replace(' ', '-').lower()}" for s in screens_map.keys()]
        if 'home feed' in screens_map: all_routes.append('/')
        
        # Ensure 'home' maps to / if exists
        
        for screen_name, json_data in screens_map.items():
            slug = screen_name.replace(' ', '-').lower()
            is_home = 'home' in slug or 'welcome' in slug
            
            raw_page = await self.llm.generate_content('PAGE_CODE', {
                "idea": idea,
                "screen_name": screen_name,
                "project_spec": json.dumps(project_spec, indent=2),
                "design_tokens": design_tokens_str,
                "all_routes": json.dumps(all_routes),
                "wireframe": json.dumps(json_data, indent=2),
                "ui_contract": "Use /auth and /api endpoints" # simplified for now
            }, PAGE_CODE_PROMPT)
            
            path = "apps/web/app/page.tsx" if is_home else f"apps/web/app/{slug}/page.tsx"
            files.append({ "path": path, "content": self._clean_code(raw_page) })

        # 3. Base Configs
        files.extend(self._generate_frontend_configs(design_system))
        
        # 4. API Client
        files.append({ "path": "apps/web/lib/api.ts", "content": """
const BASE_URL = 'http://localhost:8000'; // Matched python backend
export const api = {
    get: async (url: string) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${BASE_URL}${url}`, { headers: { 'Authorization': `Bearer ${token}` } });
        return res.json();
    },
    post: async (url: string, data: any) => {
        const token = localStorage.getItem('token');
        const res = await fetch(`${BASE_URL}${url}`, { 
            method: 'POST', 
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(data)
        });
        return res.json();
    }
};
""" })

        return files

    def _generate_root_configs(self) -> List[Dict]:
        return [
            { "path": "package.json", "content": json.dumps({"name": "app", "workspaces": ["apps/*"], "scripts": {"dev": "turbo run dev"}}, indent=2) },
            { "path": "turbo.json", "content": json.dumps({"pipeline": {"dev": {"cache": False, "persistent": True}}}, indent=2) }
        ]

    def _generate_frontend_configs(self, design_system: Dict) -> List[Dict]:
        # Generate tailwind config and globals.css based on design system
        theme = design_system.get('theme', {}).get('colors', {})
        primary = theme.get('primary', '#3c82f6')
        bg = theme.get('background', '#000000')
        
        # Simplified dynamic CSS generation
        css_content = f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --background: {bg};
  --primary: {primary};
}}

body {{
  background-color: var(--background);
  color: {theme.get('foreground', '#ffffff')};
}}
"""
        return [
           { "path": "apps/web/package.json", "content": json.dumps({
                "name": "web", "version": "0.1.0", "scripts": { "dev": "next dev", "build": "next build" },
                "dependencies": { "next": "14.2.3", "react": "^18", "react-dom": "^18", "lucide-react": "latest", "framer-motion": "latest", "react-hook-form": "latest", "zod": "latest", "clsx": "latest", "tailwind-merge": "latest" },
                "devDependencies": { "typescript": "^5", "tailwindcss": "^3.4.1", "postcss": "^8", "@types/react": "^18" }
            }, indent=2) },
           { "path": "apps/web/tailwind.config.ts", "content": "import type { Config } from 'tailwindcss';\nconst config: Config = { content: ['./app/**/*.{js,ts,jsx,tsx}', './components/**/*.{js,ts,jsx,tsx}'], theme: { extend: {} }, plugins: [] };\nexport default config;" },
           { "path": "apps/web/postcss.config.js", "content": "module.exports = { plugins: { tailwindcss: {}, autoprefixer: {}, }, };" },
           { "path": "apps/web/app/globals.css", "content": css_content },
           { "path": "apps/web/app/layout.tsx", "content": "import './globals.css';\nimport { Inter } from 'next/font/google';\nconst inter = Inter({ subsets: ['latin'] });\nexport const metadata = { title: 'App' };\nexport default function RootLayout({ children }: { children: React.ReactNode }) { return (<html lang='en'><body className={inter.className}>{children}</body></html>); }" },
           { "path": "apps/web/next.config.mjs", "content": "/** @type {import('next').NextConfig} */\nconst nextConfig = {};\nexport default nextConfig;" }
        ]

    async def _generate_readme(self, idea: str, project_id: str) -> str:
        raw = await self.llm.generate_content('README', { "idea": idea, "project_name": idea, "project_id": project_id }, README_TEMPLATE_PROMPT)
        return self._clean_code(raw)

    def _parse_multi_file_response(self, raw: str) -> Dict[str, str]:
        blocks = {}
        current_file = None
        for line in raw.split('\n'):
            if line.startswith('### '):
                current_file = line.replace('### ', '').strip()
                blocks[current_file] = ""
            elif current_file:
                blocks[current_file] += line + "\n"
        
        for k, v in blocks.items(): blocks[k] = self._clean_code(v)
        return blocks
    
    def _extract_endpoints_from_files(self, files: List[Dict]) -> List[str]:
        # Basic regex to find @router.get/post etc
        endpoints = []
        for f in files:
            content = f['content']
            matches = re.findall(r'@(?:router|app)\.(get|post|put|delete)\([\'"](.*?)[\'"]', content)
            endpoints.extend([m[1] for m in matches])
        return endpoints

    def _log_step(self, msg: str):
        print(f"[AIBuilder] {msg}")

    def _error_result(self, error_msg: str, details: List[str]) -> Dict[str, Any]:
        return {
            "status": "ERROR",
            "error": error_msg,
            "details": details
        }
    
    # Alias build_project to orchestrate_build to maintain backward compatibility if needed
    async def build_project(self, project_id: str, description: str) -> Dict[str, Any]:
         return await self.orchestrate_build(project_id, description)