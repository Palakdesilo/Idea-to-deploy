CANONICAL_JSON_PROMPT = """
You are a Product Strategy Expert. 
Your task is to transform a high-level project idea into a **Structured Canonical JSON Object**.
This JSON will serve as the single source of truth for all downstream documentation.

**Project Idea**: {idea}

**CRITICAL RULES:**
1.  **Output MUST be ONLY valid JSON**. No markdown formatting, no preamble.
2.  **Schema Consistency**: You must adhere to the structure below.
3.  **Expansion**: Expand the idea realistically. If an idea is "A gym app", define user roles (Trainer, Member), core features (Workout logging, etc.), and risks.
4.  **Conservative Scope**: Do not over-engineer. Focus on core MVP requirements.

**REQUIRED JSON SCHEMA:**
{{
  "project_overview": {{
    "summary": "Detailed 2-3 sentence overview",
    "problem_statement": "The specific problem this solves",
    "objectives": ["Goal 1", "Goal 2", "Goal 3"]
  }},
  "users": {{
    "target_users": ["User Type A", "User Type B"],
    "user_roles": ["Admin", "Standard User", "etc."]
  }},
  "scope": {{
    "in_scope": ["Feature A", "Feature B", "Module C"],
    "out_of_scope": ["Feature X", "Future expansion Y"]
  }},
  "features": {{
    "must_have": ["Core Feature 1", "Core Feature 2"],
    "nice_to_have": ["Extra 1", "Extra 2"]
  }},
  "constraints": {{
    "time": "e.g., 12 weeks",
    "budget": "e.g., Enterprise standard",
    "technical": "e.g., Cloud-native",
    "regulatory": "e.g., GDPR"
  }},
  "assumptions": ["Assumption 1", "Assumption 2"],
  "risks": ["Risk 1", "Risk 2"],
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
Create a **Detailed UI/UX Design Specification** using the Canonical JSON provided.

**Canonical JSON**: {canonical_json}

**CRITICAL: Use these 5 sections.**
1. Design System & Style Guide
2. User Flows
3. Screen Specifications (Purpose, Roles, Components, Interactions, States)
4. Accessibility Standards
5. Mobile Responsiveness
"""

UI_CONTRACTS_PROMPT = """
You are a UI/UX Architect specializing in creating structured UI contracts.

**Canonical JSON**: {canonical_json}

**Task**: Generate a comprehensive list of ALL screens needed for this application in STRICT JSON format.

**CRITICAL RULES:**
1. Output MUST be ONLY valid JSON. No markdown, no explanations.
2. Each screen must have: screen, role, purpose, actions, components, data, states, navigation
3. Include ALL screens: public pages, auth flows, user dashboards, admin panels, error pages
4. Be thorough - include login, register, forgot password, 404, 500, etc.

**REQUIRED JSON SCHEMA:**
{{
  "ui_contracts": [
    {{
      "screen": "Screen Name",
      "role": "User Role (e.g., Public / Guest, Standard User, Admin)",
      "purpose": "What this screen does",
      "actions": ["Action 1", "Action 2"],
      "components": ["Component 1", "Component 2"],
      "data": ["Data 1", "Data 2"],
      "states": ["State 1", "State 2"],
      "navigation": ["Target Screen 1", "Target Screen 2"]
    }}
  ]
}}

**Example screens to include:**
- Landing/Home, Product Listing, Product Detail
- Login, Register, Forgot Password, Reset Password
- User Dashboard, Profile, Settings
- Admin Dashboard, Management Screens
- Cart, Checkout, Order Confirmation
- Error pages (404, 500)
"""

WIREFRAMES_PROMPT = """
You are a UI/UX Designer creating low-fidelity wireframes.

**UI Contracts**: {ui_contracts}

**Task**: Convert the UI contracts into wireframe layouts showing ONLY structure and component placement.

**CRITICAL RULES:**
1. Output MUST be ONLY valid JSON. No markdown, no explanations.
2. Use ONLY components from the UI contracts - DO NOT invent new ones
3. Organize components into logical sections (Header, Sidebar, Main Content, Footer, etc.)
4. NO colors, NO styling, NO branding - structure only

**REQUIRED JSON SCHEMA:**
{{
  "wireframes": [
    {{
      "screen": "Screen Name (must match UI contract)",
      "layout": [
        {{
          "section": "Section Name",
          "components": ["Component 1", "Component 2"]
        }}
      ]
    }}
  ]
}}
"""

UI_DESIGN_PROMPT = """
You are a UI/UX Designer applying design tokens and component styles to wireframes.

**Wireframes**: {wireframes}
**UI Contracts**: {ui_contracts}

**Task**: Apply consistent design tokens and component styles to create a complete UI design specification.

**CRITICAL RULES:**
1. Output MUST be ONLY valid JSON. No markdown, no explanations.
2. DO NOT change layout structure from wireframes
3. DO NOT invent new components
4. Apply professional design tokens: colors, typography, spacing, radius, shadows
5. Define component styles: Button, Input, Card, Header, Sidebar, Table
6. Apply styles to each screen's layout

**REQUIRED JSON SCHEMA:**
{{
  "design_tokens": {{
    "colors": {{}},
    "typography": {{}},
    "spacing": {{}},
    "radius": {{}},
    "shadows": {{}}
  }},
  "component_styles": {{
    "Button": {{}},
    "Input": {{}},
    "Card": {{}},
    "Header": {{}},
    "Sidebar": {{}},
    "Table": {{}}
  }},
  "screens": [
    {{
      "screen": "Screen Name (must match wireframe)",
      "layout": [
        {{
          "section": "Section Name",
          "style": {{}},
          "components": [
            {{
              "name": "Component Name",
              "variant": "Component.variant",
              "additional_properties": {{}}
            }}
          ]
        }}
      ]
    }}
  ]
}}

Use modern, professional design tokens suitable for the application type.
"""
