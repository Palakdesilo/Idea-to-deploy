
export const CANONICAL_JSON_PROMPT = `
MODE: Canonical Knowledge Generation

Given the following project idea, extract and normalize all information
into a single structured JSON object.

Input Idea:
{idea}

Instructions:
- Expand the idea logically but conservatively
- Do not invent advanced features unless implied
- Identify users, goals, scope, risks, and constraints
- If information is unclear, state assumptions explicitly
- Output ONLY valid JSON
- Do not include explanations or markdown

JSON Schema (must match exactly):
{{
  "project_overview": {{
    "summary": "",
    "problem_statement": "",
    "objectives": []
  }},
  "users": {{
    "target_users": [],
    "user_roles": []
  }},
  "scope": {{
    "in_scope": [],
    "out_of_scope": []
  }},
  "features": {{
    "must_have": [],
    "nice_to_have": []
  }},
  "constraints": {{
    "time": "",
    "budget": "",
    "technical": "",
    "regulatory": ""
  }},
  "assumptions": [],
  "risks": [],
  "success_metrics": [],
  "scalability_expectations": ""
}}
`;

export const REQUIREMENT_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a professional Requirement Specification document.

Rules:
- Do not introduce new features
- Use formal documentation tone
- Structure the document clearly
- All requirements must map to in_scope and must_have features

Canonical JSON:
{canonical_json}

Document Structure:
- Purpose
- Scope
- User Roles
- Functional Requirements
- Non-Functional Requirements
- Assumptions
- Constraints
- Dependencies
`;

export const PLANNING_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a project Planning document.

Rules:
- Base milestones on scope and features
- Reflect stated constraints
- Avoid technical implementation details

Canonical JSON:
{canonical_json}

Document Structure:
- Project Goals
- Deliverables
- Project Phases
- Milestones
- Resource Overview
- Communication Plan
`;

export const ARCHITECTURE_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a high-level Technical Architecture document.

Rules:
- Choose standard, proven technologies
- Avoid unnecessary complexity
- Justify technical choices briefly
- Align with scalability expectations

Canonical JSON:
{canonical_json}

Document Structure:
- System Overview
- High-Level Architecture
- Technology Stack
- Data Flow Overview
- Security Considerations
- Scalability Strategy
- Deployment Overview
`;

export const IPMP_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate an Integrated Project Management Plan (IPMP).

Rules:
- Reference planning and governance
- Assume standard enterprise controls
- Avoid repetition of full requirements

Canonical JSON:
{canonical_json}

Document Structure:
- Project Overview
- Governance Structure
- Scope Management
- Schedule Management
- Cost Management
- Quality Management
- Risk Management
- Change Control
- Communication Management
`;

export const SCHEDULE_COST_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a Schedule and Cost Estimation document.

Rules:
- Use conservative estimates
- Clearly separate time and cost
- Include contingency buffer

Canonical JSON:
{canonical_json}

Document Structure:
- Work Breakdown Structure (High-Level)
- Estimated Timeline
- Resource Effort Estimates
- Cost Breakdown
- Contingency Planning
`;

export const QUALITY_RISK_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a Quality Assurance and Risk Management document.

Rules:
- Risks must come from canonical risks or logical implications
- Include mitigation strategies
- Define quality acceptance clearly

Canonical JSON:
{canonical_json}

Document Structure:
- Quality Objectives
- Quality Standards
- Review & Approval Process
- Risk Register
- Risk Mitigation Plan
`;

export const TESTING_RELEASE_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a Testing Strategy document.

Rules:
- Testing must align with requirements and risks
- No implementation-specific test cases
- Focus on validation and acceptance

Canonical JSON:
{canonical_json}

Document Structure:
- Test Strategy
- Test Types
- Test Scenarios (High-Level)
- Entry & Exit Criteria
- Defect Management
- Release Approval
`;

export const UI_UX_PROMPT = `
MODE: Document Generation

Using ONLY the provided canonical JSON,
generate a Detailed UI/UX Design Specification.

Rules:
- Generate 5-7 key screens based on the features and user roles
- Use professional design terminology
- CRITICAL: YOUR OUTPUT MUST BE PARSABLE. USE THIS FORMAT FOR EACH SCREEN:

### [Screen Name] Screen
- **Purpose**: A clear description of why this screen exists.
- **Roles**: Which user roles can access this.
- **Components**: A comma-separated list of UI components (e.g., Header, Sidebar, Search Bar, Card List).
- **Interactions**: User actions available (e.g., Click 'Buy' to add to cart, Drag and Drop to reorder).
- **States**: Different UI states (e.g., Loading, Empty, Error, Success).

Canonical JSON:
{canonical_json}
`;
