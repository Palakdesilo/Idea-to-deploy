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
You are a Senior Product Architect. 
List the Essential Screens for this project.

**Project Idea**: {idea}

**Output Format**: 
Provide a simple PLAIN TEXT LIST of screens.
Example:
- Login Screen: User authentication
- Dashboard: Overview of metrics
- Settings: User preferences

Do NOT output JSON. Just a clean text list.
"""

# ... (keep other prompts) ...


PAGE_CODE_PROMPT = """
You are an expert Senior Full-Stack Engineer and UI/UX Architect.
Your task is to write a production-ready Next.js 14 Page component that FAITHFULLY replicates the provided design and functionality.

**Project Context**: {idea}
**Screen Name**: {screen_name}
**Design Tokens**: {design_tokens}
**Available Routes**: {all_routes}
**Wireframe Definition**: 
{wireframe}
**UI Contract (API/Actions)**:
{ui_contract}

**STRICT CODE RULES:**
1. **VISUAL FAITHFULNESS**: Replicate the premium aesthetics from the design tokens.
   - **Strictly use** the provided `primary`, `secondary`, and `surface` HSL/Hex codes for backgrounds and buttons.
   - Apply the specific `radius` (e.g., rounded-xl) and `shadow` defined in the tokens.
   - Implement glassmorphism (bg-white/5 backdrop-blur-lg) for cards and modals if specified in `design_tokens`.
   - Use **standard Tailwind animations** (animate-fade-in, animate-pulse, etc.) and CSS transitions (`transition-all duration-300`) for page elements and hover effects. Avoid complex animation libraries unless strictly necessary for a specific requested effect.
2. **FUNCTIONAL NAVIGATION**: 
   - Use Next.js `Link` for internal navigation using the "Available Routes" provided.
   - Ensure navigation links mentioned in the wireframe/contract are functional.
3. **API INTEGRATION**:
   - Use the `api` utility from `@/lib/api` for all data fetching and actions.
   - Example: `api.post('/auth/login', data)` or `api.get('/items')`.
   - Handle loading and error states for all API calls.
4. **NAVIGATION & ROUTING (CRITICAL)**:
   - **Login/Register Success**: AFTER a successful API call (e.g., login), you MUST redirect the user.
     - Example: `router.push('/dashboard')` or to the user's home screen.
   - **Internal Links**: Use Next.js `<Link href="/path">` for all internal navigation (sidebar items, dashboard cards).
     - Ensure these paths MATCH the `Available Routes` provided above.
   - **Dashboard**: Sidebar or specific action buttons MUST link to valid routes (e.g., Users -> `/users`, Settings -> `/settings`).
5. **FORM VALIDATION**:
   - Implement forms with `react-hook-form` and `zod` validation.
   - Match the fields specified in the UI contract.
5. **AUTHENTICATION**:
   - If it's a login/register page, implement the full flow using the `api` client (storing token in localStorage).
   - For protected pages, implement a check using the `api` client or assume `useAuth` is available.
6. **DOMAIN-SPECIFIC COPY**: Use real, professional copy. NO LOREM IPSUM.

**Technical Stack**:
- Next.js 14 (App Router, TSX)
- Tailwind CSS (Premium glassmorphism, gradients)
- Lucide React Icons
- Framer Motion (Animations)
- react-hook-form + zod (Forms)

**Output Format**:
Return ONLY the raw React code (TSX). Do not wrap in markdown fenced blocks.
Include "use client"; at the very top of the file.
Include all necessary imports.
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


DYNAMIC_SCREENS_PROMPT = """
want to Build "{idea}".

Give me page list and wireframe with branding.
"""
