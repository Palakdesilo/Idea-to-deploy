import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class LLMService:
    VERSION = "1.1.0-PY"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                print("OpenAI module not found. Using fallback.")

    async def generate_content(self, prompt_name: str, variables: Dict[str, str], template: str) -> str:
        if self.api_key and self.client:
            try:
                # Format template with variables
                formatted_prompt = template
                for k, v in variables.items():
                    formatted_prompt = formatted_prompt.replace(f"{{{k}}}", str(v))
                
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": formatted_prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLM Generation failed for {prompt_name}, falling back: {e}")
                return self.fallback_generation(prompt_name, variables)
        else:
            return self.fallback_generation(prompt_name, variables)

    def fallback_generation(self, prompt_name: str, variables: Dict[str, str]) -> str:
        canonical_json = variables.get('canonical_json')
        idea = variables.get('idea', 'Project Idea')
        
        json_data = None
        if canonical_json:
            try:
                json_data = json.loads(canonical_json)
            except:
                pass

        if prompt_name == 'CANONICAL_JSON':
            return json.dumps({
                "project_overview": {
                    "summary": idea,
                    "problem_statement": "Manual processes in " + idea + " are inefficient.",
                    "objectives": ["Automate workflows", "Improve user experience", "Provide data insights"]
                },
                "users": {
                    "target_users": ["Internal Staff", "System Administrators"],
                    "user_roles": ["Standard User", "Admin"]
                },
                "scope": {
                    "in_scope": ["Web interface", "Core database", "User authentication"],
                    "out_of_scope": ["Mobile application", "Offline mode"]
                },
                "features": {
                    "must_have": ["User Dashboard", "Data Entry Forms", "Reporting Module"],
                    "nice_to_have": ["Dark Mode", "Push Notifications"]
                },
                "constraints": {
                    "time": "12 weeks",
                    "budget": "Enterprise standard",
                    "technical": "Modern web stack",
                    "regulatory": "GDPR Compliance"
                },
                "assumptions": ["Stable internet connectivity", "Basic technical proficiency"],
                "risks": ["Data security vulnerabilities", "Integration challenges"],
                "success_metrics": ["90% user adoption", "Reduced processing time"],
                "scalability_expectations": "Support up to 10,000 users"
            }, indent=2)

        # Extraction from JSON for other docs
        summary = idea
        objectives = ["High quality delivery", "User satisfaction"]
        features = ["Core System"]
        roles = ["Admin", "User"]

        if json_data:
            summary = json_data.get("project_overview", {}).get("summary", summary)
            objectives = json_data.get("project_overview", {}).get("objectives", objectives)
            features = json_data.get("features", {}).get("must_have", features)
            roles = json_data.get("users", {}).get("user_roles", roles)

        if prompt_name == 'REQUIREMENTS':
            return f"""# Requirement Document: {summary}
            
## 1. Project Background & Objectives
{summary}
Objectives: {', '.join(objectives)}

## 2. Functional Requirements
{chr(10).join([f'- REQ-{i+1:03}: {f}' for i, f in enumerate(features)])}

## 3. User Roles
{', '.join(roles)}
"""

        if prompt_name == 'PLANNING':
            return f"""# Project Planning Document: {summary}
            
## 1. Work Breakdown Structure
- Phase 1: Requirement & Design
- Phase 2: Core Development of {features[0] if features else 'system'}
- Phase 3: Integration & Testing

## 2. Milestones
- M1: Sign-off (Week 2)
- M2: MVP (Week 8)
- M3: Launch (Week 12)
"""

        if prompt_name == 'ARCHITECTURE':
            return f"""# Technical Architecture: {summary}
            
## 1. Tech Stack
- Frontend: Next.js
- Backend: Python (FastAPI)
- Database: PostgreSQL

## 2. System Components
- API Server
- Auth Service
- Data Storage Service
"""

        if prompt_name == 'IPMP':
            return f"""# Integrated Project Management Plan (IPMP): {summary}
            
## 1. Purpose
Defines the integration of all project work for {summary}.

## 2. Success Criteria
{chr(10).join([f'- {o}' for o in objectives])}
"""

        if prompt_name == 'SCHEDULE_COST':
            return f"""# Schedule & Cost Plan: {summary}
            
## 1. Timeline
Total Project Duration: 12 weeks.

## 2. Budget Allocation
- Development: 70%
- Design: 15%
- Infrastructure: 15%
"""

        if prompt_name == 'QUALITY_RISK':
            return f"""# Quality, Risk & Procurement Plan: {summary}
            
## 1. Quality Standards
Adherence to clean code principles and ISO quality metrics.

## 2. Risk Matrix
- R1: Scope creep (Medium)
- R2: Tech debt (Low)
"""

        if prompt_name == 'TESTING_RELEASE':
            return f"""# Testing & Release Plan: {summary}
            
## 1. Testing Strategy
- Unit Testing
- Integration Testing
- User Acceptance Testing (UAT)

## 2. Deployment Plan
CI/CD based automated deployment to production.
"""

        if prompt_name == 'UI_UX':
            return f"""# UI/UX Design Specification: {summary}
            
## 1. Screen List
- Dashboard for {roles[0]}
- Data Entry for {roles[1] if len(roles) > 1 else 'Users'}
- Global Search

## 2. Style Guide
Modern, clean interface with blue-primary color palette.
"""

        return f"# {prompt_name} Document for {summary}\n\nDetailed specifications generated for the project."
