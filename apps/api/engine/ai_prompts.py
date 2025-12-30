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
You are a UI/UX Strategist. 
Analyze the original Project Idea and the generated documentation bundle to identify a UNIQUE screen inventory. 

**Project Idea**: {idea}

**Input Documentation Bundle**:
{bundle}

**Task**: Generate a comprehensive list of screens tailored specifically to this project's requirements. 
Do NOT just provide "Dashboard" or "Settings" if they aren't relevant. 
Focus on the specific workflows defined in the Functional Requirements (REQ-XXX) and Use Cases.

Include:
- Public pages specific to the business niche
- Specific User features and workflows
- Relevant Admin/Backoffice screens for this specific data
- Edge cases relevant to this project

**Output Format**: STRICT JSON ONLY.
{{
  "screen_inventory": [
    {{
      "name": "Screen Name",
      "category": "Auth / User / Admin / Public / etc.",
      "description": "How this screen solves a specific project objective"
    }}
  ]
}}
"""

UI_CONTRACTS_PROMPT = """
You are a UI/UX Architect. 
Convert the Screen Inventory into detailed UI contracts.

**Project Idea**: {idea}
**Screen Inventory**: {screen_inventory}

**Task**: For EACH screen, define exactly what data and actions it needs based on the Project Idea.
Avoid generic "Action 1". Use real actions like "Upload Medical Report" or "Compare Subscription Plans" as appropriate for the project.

**REQUIRED JSON SCHEMA:**
{{
  "ui_contracts": [
    {{
      "screen": "Screen Name",
      "role": "User Role",
      "purpose": "Specific project goal this screen fulfills",
      "actions": ["Project-specific Action A", "Project-specific Action B"],
      "components": ["Component Key 1", "Component Key 2"],
      "data": ["Data Field 1", "Data Field 2"],
      "states": ["Default", "Error", "Specific State X"],
      "navigation": ["Target Screen Key"]
    }}
  ]
}}
"""

WIREFRAMES_PROMPT = """
You are a Principal UI/UX Architect designing a world-class digital product. 

**REFERENCE AESTHETIC**: Think of premium sites like "STOREFRONT" or modern Apple-style landing pages. 
- High density of content.
- Diverse layouts (Grids, Split Sections, Carousels).
- Professional, persuasive copywriting.

**Project Idea**: {idea}
**UI Contracts**: {ui_contracts}

**STRICT PAGE DENSITY & LAYOUT RULES:**
1. **FULL PAGE ARCHITECTURE**: Every screen MUST have a `Header`, `Main`, and `Footer`.
2. **COMPONENT DENSITY**: A screen must have 6-10 components. 
3. **LAYOUT DIVERSITY**: 
   - Use `SplitSection` for Hero or feature highlights (Image left/right, Text other side).
   - Use `ProductGrid` or `FeatureGrid` for browsing.
   - Use `TestimonialGrid` for social proof.
   - Use `Newsletter` for engagement.
4. **NO PLACEHOLDERS**: Every `content` field must be 40-80 words of niche-specific, persuasive copy.
5. **DYNAMIC NAVIGATION**: Use the `Link` component in Header/Footer to create a real website feel.

**COMPONENT SCHEMA:**
- `key`: UNIQUE string
- `type`: `Hero | SplitSection | ProductGrid | FeatureGrid | TestimonialGrid | Newsletter | StatGrid | Table | PostCard | AuthCard | Card | Banner`
- `label`: Component Title
- `content`: Stringified JSON or long-form copy.
  - For `ProductGrid`: JSON array `[{"name": "...", "price": "$...", "image_desc": "..."}]`
  - For `TestimonialGrid`: JSON array `[{"user": "...", "rating": 5, "quote": "..."}]`
  - For `StatGrid`: JSON array `[{"label": "...", "value": "..."}]`
- `subtext`: Metadata or CTA label.

**JSON OUTPUT FORMAT:**
{{
  "wireframes": [
    {{
      "screen": "Screen Name",
      "screenKey": "camelCase",
      "purpose": "Detailed UX goal",
      "layout": [
        {{
          "section": "Header | Main | Footer",
          "components": [...]
        }}
      ]
    }}
  ]
}}
"""

UI_DESIGN_PROMPT = """
You are a Senior UI/UX Designer converting wireframes into niche-perfect Visual Interfaces.

**Project Idea**: {idea}
**Wireframes**: {wireframes}
**UI Contracts**: {ui_contracts}

**THEMATIC STYLE GUIDE**:
Select the most appropriate archetype based on the project idea:
1. **E-COMMERCE**: Palette: Crisp White, Bold Black (#1a1a1a), and a vibrant CTA color (e.g., #E44D26 or #00a8e8). Style: Clean product cards, sharp shadows, prominent pricing.
2. **FINANCE/BANKING**: Palette: Deep Navy (#0d1117), Slate Grey, and Emerald Green (#10b981) for values. Style: Professional, ultra-clean borders, condensed typography for data.
3. **SOCIAL/COMMUNITY**: Palette: Soft Grey backgrounds, Vibrant Blue (#1da1f2) or Purple (#6366f1) accents. Style: Rounded avatars, high-contrast like/comment buttons, fluid spacing.
4. **HEALTH/WELLNESS**: Palette: Soft Mint (#f0fff4) or Sky Blue, with Charcoal text. Style: Large whitespace, rounded corners (12px+), calming soft shadows.
5. **SAAS/DASHBOARD**: Palette: Neutral Grey, White, and a strong Indigo (#4f46e5) brand color. Style: Glassmorphism touches, subtle border-bottoms, clear hierarchy.

**Task**: Apply these thematic design tokens to create a complete UI design specification.

**CRITICAL RULES:**
1. Output MUST be ONLY valid JSON.
2. Apply the specific archetype colors to `design_tokens`.
3. Fill `component_styles` with detailed CSS properties (box-shadow, border-radius, font-weight).
4. Match every screen in `wireframes` to a screen in the `screens` array.

**REQUIRED JSON SCHEMA:**
{{
  "design_tokens": {{
    "colors": {{
      "primary": "Hex code based on archetype",
      "background": "#f8f9fa",
      "card_bg": "#ffffff",
      "text_main": "#1a1a1a",
      "accent": "Hex code"
    }},
    "typography": {{
       "font_family": "Inter, sans-serif",
       "heading_size": "24px",
       "body_size": "14px"
    }},
    "spacing": {{ "padding": "24px", "gap": "16px" }},
    "radius": {{ "large": "12px", "medium": "8px", "small": "4px" }},
    "shadows": {{ "soft": "0 4px 12px rgba(0,0,0,0.05)", "card": "0 1px 3px rgba(0,0,0,0.1)" }}
  }},
  "component_styles": {{
    "Button": {{ "bg": "var(--primary)", "text": "#ffffff", "radius": "var(--radius-medium)" }},
    "Card": {{ "bg": "var(--card-bg)", "shadow": "var(--shadow-card)", "radius": "var(--radius-large)" }},
    "Input": {{ "border": "#e0e0e0", "focus": "var(--primary)" }}
  }},
  "screens": [
    {{
      "screen": "Screen Name",
      "theme_override": "Special styling note for this screen"
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
