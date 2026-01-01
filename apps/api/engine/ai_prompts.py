CANONICAL_JSON_PROMPT = """
You are a Product Strategy Expert and Venture Architect. 
Your task is to transform a high-level project idea into a **Structured Canonical JSON Object**.
This JSON will serve as the single source of truth for all downstream documentation.

**Project Idea**: {idea}

**CRITICAL RULES:**
1.  **Output MUST be ONLY valid JSON**. No markdown formatting, no preamble.
2.  **Schema Consistency**: You must adhere to the structure below.
3.  **Expansion**: Deeply expand the idea. If it's a "Gym App", think about specific niches (e.g., CrossFit management, Yoga wellness, or Personal Training CRM). 
4.  **No Generic Roles**: Use domain-specific roles. Instead of "User", use "Patient", "Athlete", "Collector", etc.
5.  **Unique Value Proposition**: Define 3-5 unique features that differentiate this from standard templates.

**REQUIRED JSON SCHEMA:**
{{
  "project_overview": {{
    "summary": "Detailed 2-3 sentence overview with a unique angle",
    "problem_statement": "The specific bottleneck or friction point this solves",
    "objectives": ["Unique Goal 1", "Unique Goal 2", "Unique Goal 3"]
  }},
  "users": {{
    "target_users": ["Niche User Type A", "Niche User Type B"],
    "user_roles": ["Domain Role 1", "Domain Role 2", "Secondary Role"]
  }},
  "scope": {{
    "in_scope": ["Feature A (Unique)", "Feature B (Core)", "Module C (Integration)"],
    "out_of_scope": ["Generic Feature X", "Future expansion Y"]
  }},
  "features": {{
    "must_have": ["Niche-Specific Core 1", "Niche-Specific Core 2"],
    "nice_to_have": ["Extra 1", "Extra 2"]
  }},
  "constraints": {{
    "time": "e.g., 12 weeks",
    "budget": "e.g., Enterprise standard",
    "technical": "e.g., Edge computing, AI-integrated",
    "regulatory": "e.g., HIPAA, GDPR"
  }},
  "assumptions": ["Assumption 1", "Assumption 2"],
  "risks": ["Domain-specific Risk 1", "Risk 2"],
  "success_metrics": ["Metric 1", "Metric 2"],
  "scalability_expectations": "e.g., Support 10k concurrent users"
}}
"""

REQUIREMENT_PROMPT = """
You are a PMP-certified Software Project Consultant.
Create a **Requirement Document** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 14 sections.**
1. Document Control & Versioning
2. Project Background & Objectives
3. Stakeholder Identification
4. Assumptions & Constraints
5. In-Scope / Out-of-Scope
6. Functional Requirements (REQ-001 format)
7. Non-Functional Requirements (NFR-001 format)
8. User Roles & Permissions
9. Business Rules
10. Use Cases / User Stories
11. UI/UX & Screen References
12. Data Requirements
13. Regulatory & Compliance Requirements
14. Requirement Traceability Matrix (RTM)
"""

PLANNING_PROMPT = """
You are a PMP-certified Software Project Consultant.
Create a **Project Planning Document** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 11 sections.**
1. Project Overview
2. Project Governance Structure
3. Project Organization & Roles
4. Project Methodology (Agile Scrum recommended)
5. Work Breakdown Structure (WBS)
6. Deliverables & Milestones
7. Resource Planning
8. Communication Management Plan
9. Change Management Plan
10. Dependency Management
11. Assumptions & Constraints
"""

ARCHITECTURE_PROMPT = """
You are a Senior System Architect.
Create a **Technical Architecture & Delivery Plan** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 12 sections.**
1. Architecture Overview
2. System Context Diagram
3. Logical Architecture
4. Physical Architecture
5. Technology Stack (Next.js, Node.js, Python, PostgreSQL)
6. Application Architecture
7. Database & Data Flow Design
8. API & Integration Strategy
9. Security Architecture
10. Scalability & Performance Design
11. Deployment Architecture
12. Technical Risks & Mitigations
"""

IPMP_PROMPT = """
You are a PMP-certified Project Manager.
Create an **Integrated Project Management Plan (IPMP)** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 11 sections.**
1. IPMP Purpose & Scope
2. Project Objectives & Success Criteria
3. Integrated Baselines (Scope, Schedule, Cost)
4. Governance & Decision Framework
5. Integrated Change Control
6. Risk, Quality & Procurement Integration
7. Stakeholder Engagement Strategy
8. Performance Measurement (KPIs, EV, Metrics)
9. Reporting & Review Cadence
10. Escalation & Issue Resolution
11. Compliance & Audit Strategy
"""

SCHEDULE_COST_PROMPT = """
You are a Project Scheduler and Cost Controller.
Create a **Schedule & Cost Plan** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 11 sections.**
1. Schedule Management Approach
2. Project Timeline & Milestones
3. Task Dependencies
4. Resource Allocation
5. Critical Path Analysis
6. Cost Estimation Methodology
7. Budget Breakdown (CAPEX / OPEX)
8. Cost Baseline
9. Cost Control & Tracking
10. Earned Value Management (EVM)
11. Schedule & Cost Risks
"""

QUALITY_RISK_PROMPT = """
You are a Quality and Risk Manager.
Create a **Quality, Risk & Procurement Plan** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 15 sections.**
1. Quality Management Approach
2. Quality Objectives
3. Quality Standards & Metrics
4. Quality Assurance Process
5. Quality Control Activities
6. Risk Management Approach
7. Risk Identification
8. Risk Register
9. Risk Analysis & Prioritization
10. Risk Response Strategies
11. Procurement Management Approach
12. Procurement Strategy
13. Vendor Selection Criteria
14. Contract Types
15. SLA & Performance Monitoring
"""

TESTING_RELEASE_PROMPT = """
You are a QA Lead and Release Manager.
Create a **Testing & Release Plan** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 12 sections.**
1. Test Strategy
2. Test Scope & Objectives
3. Test Environment Setup
4. Test Types (Unit, Integration, System, UAT)
5. Test Data Management
6. Defect Management Process
7. Entry & Exit Criteria
8. Release Management Strategy
9. Deployment Plan
10. Rollback & Recovery Plan
11. Post-Release Validation
12. Maintenance & Support Strategy
"""

UI_UX_PROMPT = """
You are a Senior UI/UX Designer.
Create a **Detailed UI/UX Design Specification** in STRICT JSON format.

**Canonical JSON**: {canonical_json}

**REQUIRED JSON SCHEMA:**
{{
  "design_system": {{
    "style_guide": "Summary of system",
    "typography": [],
    "colors": []
  }},
  "user_flows": [],
  "screen_specifications": [
    {{
      "name": "Screen Name",
      "purpose": "Screen purpose",
      "roles": [],
      "components": [],
      "interactions": [],
      "states": []
    }}
  ],
  "accessibility": "Standards followed",
  "responsiveness": "Strategy description"
}}
"""

SCREEN_INVENTORY_PROMPT = """
You are a Senior Product Designer & UI/UX Architect. 
Analyze the Project Idea and the generated documentation to identify a PROJECT-WISE DIFFERENT screen inventory.

**Project Idea**: {idea}

**Input Documentation Bundle**:
{bundle}

**STRICT GENERATION RULES:**
1. **NO GENERIC SCREENS**: Do NOT use default names like "Dashboard", "Settings", or "Home Feed" unless they are logically the only option for this specific idea.
2. **DOMAIN-FIRST NAMING**: If the project is for medical use, screens should be named like "Patient Wellness Prism", "Clinical Record Vault", etc.
3. **ONLY NECESSARY SCREENS**: Explicitly decide which screens are required for THIS project. Avoid bloat.
4. **UNIQUE WORKFLOWS**: Focus on screens that solve the specific workflows defined in the Functional Requirements.
5. **USER ROLES**: Ensure screens are mapped to the specific roles (e.g., "Athlete Perspective", "Coach Command Center").

**Include**:
- Custom landing experiences (not a generic landing page)
- Core feature screens that are unique to this business model
- Specific management/admin screens derived from the data model

**Output Format**: STRICT JSON ONLY.
{{
  "screen_inventory": [
    {{
      "name": "Unique Screen Name",
      "category": "Role-Specific Category",
      "description": "The specific business value this screen provides",
      "route": "/url-safe-path"
    }}
  ]
}}
"""

UI_CONTRACTS_PROMPT = """
You are a UI/UX Architect & Full-Stack Engineer.
Define dynamic UI Contracts for each discovered screen.

**Project Idea**: {idea}
**Screen Inventory**: {screen_inventory}

**TASK**: Map data and actions to screens using STRICTLY IDEA-BASED logic.
Avoid generic "Action 1 / Action 2". Use real, domain-specific actions related to the idea.

**REQUIRED DATA & ACTIONS:**
- For a Marketplace: "Escrow Request", "Verify Seller Identity", "Dynamic Price Negotiation".
- For a SaaS: "Sync Cloud Workspace", "Generate AI Insight", "Export Audit Trail".
- For a Social App: "Ripple Content", "Connect via Prism", "Burn Notification".

**REQUIRED JSON SCHEMA:**
{{
  "ui_contracts": [
    {{
      "screen": "Screen Name",
      "role": "Specific Domain Role",
      "purpose": "What makes this screen vital to the project",
      "actions": ["Real Project Action A", "Real Project Action B"],
      "components": ["Contextual Component 1", "Contextual Component 2"],
      "data": ["Domain Data A", "Domain Data B"],
      "states": ["Active", "Empty (Niche Desc)", "Error (Niche Desc)"],
      "navigation": ["Target Screen Name"]
    }}
  ]
}}
"""

WIREFRAMES_PROMPT = """
You are a Lead UI/UX Architect creating a high-fidelity full-stack web application.
Do NOT reuse any generic layouts. 

**Project Idea**: {idea}
**UI Contracts**: {ui_contracts}

**TASK**: Generate unique wireframe layouts in JSON format.
Each project must have a different number of screens, different naming, and different layouts depending on the idea.

**LAYOUT OPTIONS (Choose for variety):**
- `fullPage`: Massive immersive experience.
- `splitVisual`: Concentrated action on one side, visual context on the other.
- `dashboardShell`: Sidebar-driven tool with complex grid system.
- `centeredFlow`: Minimalist focused task execution.
- `masonryGrid`: Dynamic content discovery.

**VARYING COMPONENT DENSITY:**
- Public pages: High visual density, 8-12 sections.
- Tool pages: High operational density, 3-column layouts.
- Modal/Overlay: Focus layouts.

**JSON OUTPUT FORMAT:**
{{
  "wireframes": [
    {{
      "screen": "Screen Name",
      "screenKey": "camelCase",
      "layoutType": "fullPage | splitVisual | dashboardShell | centeredFlow | masonry",
      "purpose": "Project-specific goal",
      "layout": [
        {{
          "section": "Header | Sidebar | Main | Footer | Overlay",
          "components": [
            {{
              "key": "UniqueComponentKey",
              "type": "Hero | FeatureGrid | Stats | ActionCard | Feed | ProfileHeader | ...",
              "label": "Domain Title",
              "content": "Rich, persuasive copy of 50-80 words or detailed data JSON",
              "subtext": "Niche-specific metadata"
            }}
          ]
        }}
      ]
    }}
  ]
}}
"""

UI_DESIGN_PROMPT = """
You are a Premium UI Designer specialized in Gemini-style aesthetics.
Create a modern, premium visual UI for the project.

**Project Idea**: {idea}
**Wireframes**: {wireframes}
**UI Contracts**: {ui_contracts}

**DESIGN ARCHITECTURE:**
1. **Color Selection**: Do NOT use plain red/blue. Use curated HSL palettes. (e.g., Deep Slate, Neon Indigo, Glassmorphic White).
2. **Typography**: Use modern Google Fonts (Inter, Outfit, Roboto).
3. **Layout Polish**: Define exact spacing tokens (8px, 16px, 24px, 48px).
4. **Premium Touches**: Add rules for hover states, scale transitions, and subtle borders.

**REQUIRED JSON SCHEMA:**
{{
  "design_tokens": {{
    "palette": {{ "background": "HSL HEX", "surface": "HSL HEX", "primary": "HSL HEX", "accent": "HSL HEX" }},
    "typography": {{ "heading": "Font Name", "body": "Font Name", "scale": "Modern Value" }},
    "effects": {{ "radius": "16px", "blur": "12px", "shadow": "Premium Soft Shadow" }}
  }},
  "screens": [
    {{
      "screen": "Screen Name",
      "visual_spec": "Detailed description of the visual vibe and unique animation/transition for this screen"
    }}
  ]
}}
"""

FIGMA_LAYOUT_PROMPT = """
You are a FIGMA Layout Architect. 

**Project Idea**: {idea}
**UI Contracts**: {ui_contracts}
**Wireframes**: {wireframes}

**Task**: Generate a highly structured Figma layout plan.
Ensure the layoutType and sections reflect the actual complexity of the project (e.g., if it's a Finance app, use a dashboardShell; if it's a Landing Page, use fullPage).

**REQUIRED JSON SCHEMA:**
{{
  "figma": {{
    "pages": [
      {{
        "name": "Project Wireframes / UI",
        "frames": [
          {{
            "name": "screenKey",
            "description": "Contextual description",
            "layoutType": "fullPage | twoColumn | dashboardShell | centeredForm",
            "sections": [
              {{
                "name": "Section Name",
                "components": [
                  {{ "key": "ComponentKey" }}
                ]
              }}
            ]
          }}
        ]
      }}
    ]
  }}
}}
"""

VISUAL_PROMPT_PROMPT = """
You are a Creative Director for a world-class design agency.

**Project Idea**: {idea}
**Screen Name**: {screen_name}
**Screen Purpose**: {purpose}

**Task**: Generate a highly detailed, professional prompt for an AI image generator (like Pollinations or Midjourney) to create a high-fidelity UI mockup of this specific screen.

**Prompt Requirements**:
1. **Style**: Describe the visual style (e.g., Glassmorphism, Brutalism, Minimalist, Neumorphism).
2. **Atmosphere**: Describe the mood and lighting.
3. **Color Palette**: Use specific, sophisticated color names.
4. **Layout**: Mention the structural elements (e.g., "centered authentication card", "complex data grid with vibrant charts").
5. **Technical Details**: Include terms like "4k resolution", "sharp focus", "soft shadows", "premium UI/UX design".

**OUTPUT**: ONLY the prompt string. NO markdown, NO quotes.
"""

PAGE_CODE_PROMPT = """
You are an expert Senior Full-Stack Engineer and UI/UX Architect.
Your task is to write a production-ready Next.js 14 Page component that is UNIQUE and PREMIUM.

**Project Context**: {idea}
**Screen Name**: {screen_name}
**Wireframe Definition**: 
{wireframe}

**STRICT CODE RULES:**
1. **NO GENERIC LAYOUTS**: Use the `layoutType` in the wireframe to drive the structure. If it's `splitVisual`, use a 2-column flex/grid.
2. **RICH AESTHETICS**: Use Tailwind for glassmorphism, gradients, and subtle animations (framer-motion if needed).
3. **DO NOT REUSE TEMPLATES**: Every page must feel custom-built for {idea}.
4. **DOMAIN-SPECIFIC COPY**: Write 50-100 words of real, persuasive text. Avoid "Lorem Ipsum".
5. **INTERACTIVE ELEMENTS**: Include real form validation with `zod`, loading states, and domain-specific icons from `lucide-react`.

**Technical Stack**:
- Next.js 14 (App Router)
- Tailwind CSS (Premium utilities)
- Lucide React Icons
- React State Management

**Output Format**:
Return ONLY the raw React code (TSX). Do not wrap in markdown fenced blocks.
"""

COMPONENT_LIBRARY_PROMPT = """
You are a Senior UI Engineer creating a reusable component library.

**Project Context**: {idea}
**Component Type**: {component_type}

**Task**: Create a production-ready, reusable React component with TypeScript.

**Requirements**:
1. Use TypeScript with proper prop types
2. Style with Tailwind CSS utility classes
3. Include variants (primary, secondary, outline, etc.) where applicable
4. Add proper accessibility attributes (aria-labels, roles)
5. Include JSDoc comments for props
6. Make it fully responsive

**Component Types to Support**:
- Button (with variants, sizes, loading states)
- Card (with header, body, footer sections)
- Input (text, email, password with validation states)
- Modal (with backdrop, close button)
- Table (with sorting, pagination)
- Badge (status indicators)

**Output Format**:
Return ONLY the raw React component code (TSX).
Do not wrap in markdown fenced blocks.
Start directly with imports.
"""

FASTAPI_ROUTE_PROMPT = """
You are a Senior Backend Engineer specializing in Python FastAPI.

**Project Context**: {idea}
**Screen**: {screen_name}
**Entity Name**: {entity_name}
**Actions**: {actions}
**Data Fields**: {data_fields}

**Task**: Generate a complete FastAPI router module for this entity with CRUD operations.

**Technical Stack**:
- Framework: FastAPI
- ORM: SQLAlchemy
- Validation: Pydantic
- Auth: JWT tokens
- Database: PostgreSQL

**Requirements**:
1. **Pydantic Schemas**: Define `Base`, `Create`, `Update`, and `Response` schemas.
   - Using strict typing (str, int, float, bool, datetime).
   - `Response` schema must include `id`, `created_at`, `updated_at`.
2. **Error Handling**:
   - Return 404 if item not found.
   - Return 401/403 for unauthorized actions.
   - Return 422 automatically via Pydantic.
3. **Authentication**:
   - Protect write operations (POST, PUT, DELETE) with `Depends(get_current_user)`.
   - Read operations can be public if it makes sense for {entity_name}, otherwise protect them.
4. **Database Safety**:
   - Comment out the actual database session commit line (`# db.commit()`) and add a `# TODO: Uncomment when DB is configured` comment to prevent crashes if DB isn't running.
   - Use `db.refresh(item)` after commit.
5. **Structure**:
   - Imports: `fastapi`, `sqlalchemy`, `pydantic`.
   - Router definition.
   - Schema definitions.
   - Route handlers.

**Output Format**:
Return ONLY the raw Python code.
Do not wrap in markdown fenced blocks.
Start directly with imports.
"""

SQLALCHEMY_MODEL_PROMPT = """
You are a Database Architect specializing in SQLAlchemy.

**Project Context**: {idea}
**UI Contracts**: {ui_contracts}

**Task**: Generate SQLAlchemy models for all entities in this project.

**Requirements**:
1. **Completeness**: Create a model for every entity implied by this project (e.g., User, Product, Post, Order).
2. **Relationships**: Define proper `ForeignKey` and `relationship`.
3. **Optimized**: Add indexes for frequently queried fields.
4. **Base**: Inherit from `database.Base`.
5. **Types**: Use correct SQLAlchemy types (Integer, String, DateTime, Boolean, Text, JSON).
6. **User Model**: MUST include `id`, `email`, `hashed_password`, `name`, `created_at`.

**Example Output**:
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    # ...
```

**Output Format**:
Return ONLY the raw Python code.
Do not wrap in markdown fenced blocks.
Start directly with imports.
"""

AUTH_SETUP_PROMPT = """
You are a Security Engineer specializing in FastAPI authentication.

**Project Context**: {idea}

**Task**: Generate a secure JWT authentication system.

**Requirements**:
1. **JWT Strategy**: Use `python-jose` to create access tokens (30 min exp) and refresh tokens (7 days exp).
2. **Password Hashing**: Use `passlib` with `bcrypt` context.
3. **Endpoints**:
   - `POST /auth/register`: Create new user.
   - `POST /auth/login`: Return access_token and refresh_token.
   - `POST /auth/refresh`: Use refresh_token to get new access_token.
   - `GET /auth/me`: Get current user profile.
4. **Dependencies**:
   - `get_db`: Yields database session.
   - `get_current_user`: Validates token and returns User object.
   - `get_current_active_user`: Ensures user is not suspended.

**Output Format**:
Return THREE separate code blocks labeled exactly:
### auth.py
### auth_routes.py
### dependencies.py

Do not wrap in markdown fenced blocks.
"""

PROJECT_CONFIG_PROMPT = """
You are a DevOps Engineer setting up a full-stack project.

**Project Context**: {idea}
**Project Name**: {project_name}

**Task**: Generate all configuration files for a production-ready project.

**Files to Generate**:
1. **Frontend (Next.js)**:
   - package.json (with all dependencies)
   - tsconfig.json
   - next.config.js
   - tailwind.config.js
   - postcss.config.js
   - .env.example

2. **Backend (Python FastAPI)**:
   - requirements.txt
   - main.py (FastAPI app entry point)
   - config.py (settings with pydantic)
   - database.py (SQLAlchemy setup)
   - .env.example

3. **Deployment**:
   - docker-compose.yml (frontend, backend, postgres)
   - Dockerfile (for backend)
   - Dockerfile.frontend (for frontend)
   - .dockerignore
   - .gitignore

4. **Documentation**:
   - README.md (comprehensive setup guide)
   - API_DOCS.md (API endpoint documentation)

**Output Format**:
Return each file's content labeled with:
### filename
[content]

Do not wrap in markdown fenced blocks.
"""

README_TEMPLATE_PROMPT = """
You are a Technical Writer creating project documentation.

**Project Context**: {idea}
**Project Name**: {project_name}
**Tech Stack**: Next.js 14, Python FastAPI, PostgreSQL, SQLAlchemy

**Task**: Generate a comprehensive README.md file.

**Sections to Include**:
1. Project Title and Description
2. Features (based on project idea)
3. Tech Stack
4. Prerequisites (Node.js, Python, PostgreSQL)
5. Installation Steps (detailed, step-by-step)
6. Environment Variables (.env setup)
7. Running the Application (dev and production)
8. API Documentation (link to /docs)
9. Project Structure (directory tree)
10. Contributing Guidelines
11. License

**Output Format**:
Return ONLY the markdown content for README.md.
Do not wrap in additional markdown fenced blocks.
Use proper markdown formatting with headers, code blocks, lists.
"""

