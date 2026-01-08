import json
import zipfile
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

        
        # Setup directories
        artifacts_dir = ARTIFACTS_DIR / project_id
        code_dir = artifacts_dir / "code"
        code_dir.mkdir(parents=True, exist_ok=True)
        
        # Load design artifacts
        wireframes = self._load_json(artifacts_dir / "docs" / "wireframes.json")
        ui_contracts = self._load_json(artifacts_dir / "docs" / "ui_contracts.json")
        ui_design = self._load_json(artifacts_dir / "docs" / "ui_design.json")
        
        
        # Generate project structure
        frontend_dir = code_dir / "frontend"
        backend_dir = code_dir / "backend"
        
        # Phase 1: Generate Frontend

        await self.generate_nextjs_app(frontend_dir, wireframes, ui_contracts, ui_design, description, project_name)
        
        # Phase 2: Generate Backend

        await self.generate_fastapi_backend(backend_dir, ui_contracts, description, project_name)
        
        # Phase 3: Generate Configuration Files

        await self.generate_project_config(code_dir, project_name, description)
        
        # Phase 4: Package as ZIP

        zip_path = await self.package_application(code_dir, project_id, project_name)
        

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
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(page_code)
            pages_written += 1
            written_routes.add(str(target_file.relative_to(app_dir)))
        
        
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
        """Load JSON file"""
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
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
        
        tokens = ui_design.get('design_tokens', {}) if ui_design else {}
        
        palette = tokens.get('palette', tokens.get('colors', {}))
        
        css_content = f"""@tailwind base;
@tailwind components;
@tailwind utilities;

:root {{
  --background: {palette.get('background', '#ffffff')};
  --foreground: {palette.get('foreground', '#000000')};
  --primary: {palette.get('primary', '#3b82f6')};
  --surface: {palette.get('surface', '#f8fafc')};
  --accent: {palette.get('accent', '#f43f5e')};
}}

body {{
  background: var(--background);
  color: var(--foreground);
  font-family: sans-serif;
  line-height: 1.5;
}}

.card {{
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid rgba(0,0,0,0.1);
    padding: 1.5rem;
}}

.btn-primary {{
    background: var(--primary);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 600;
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
    const errorData = await response.json();
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
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

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
from auth_routes import router as auth_router
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
