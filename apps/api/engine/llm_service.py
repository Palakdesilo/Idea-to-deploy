import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except:
                pass

    async def generate_content(self, prompt_name: str, variables: Dict[str, str], template: str) -> str:
        if self.api_key and self.client:
            try:
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
                return self.fallback_generation(prompt_name, variables)
        else:
            return self.fallback_generation(prompt_name, variables)

    def fallback_generation(self, prompt_name: str, variables: Dict[str, str]) -> str:
        canonical_json = variables.get('canonical_json')
        idea = variables.get('idea', 'Project Idea')
        
        json_data = None
        if canonical_json:
            try: json_data = json.loads(canonical_json)
            except: pass

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

        summary = idea
        objectives = ["High quality delivery"]
        features = ["Core System"]
        roles = ["Admin", "User"]

        if json_data:
            summary = json_data.get("project_overview", {}).get("summary", summary)
            objectives = json_data.get("project_overview", {}).get("objectives", objectives)
            features = json_data.get("features", {}).get("must_have", features)
            roles = json_data.get("users", {}).get("user_roles", roles)

        if prompt_name == 'REQUIREMENTS':
            return f"# Requirement Document: {summary}\n\n## Objectives\n" + "\n".join(objectives)
        if prompt_name == 'PLANNING':
            return f"# Project Planning Document: {summary}\n\n## Timeline\n- Phase 1: Planning\n- Phase 2: Execution"
        if prompt_name == 'ARCHITECTURE':
            return f"# Technical Architecture: {summary}\n\n## Stack\n- Next.js, FastAPI, PostgreSQL"
        if prompt_name == 'IPMP':
            return f"# Integrated Project Management Plan (IPMP): {summary}\n\n## Goals\n" + "\n".join(objectives)
        if prompt_name == 'SCHEDULE_COST':
            return f"# Schedule & Cost Plan: {summary}\n\n## Period\n12-week roadmap"
        if prompt_name == 'QUALITY_RISK':
            return f"# Quality, Risk & Procurement Plan: {summary}\n\n## Maintenance\nCode review and QA testing."
        if prompt_name == 'TESTING_RELEASE':
            return f"# Testing & Release Plan: {summary}\n\n## Phases\n- Unit\n- Integration\n- UAT"
        if prompt_name == 'UI_UX':
            return f"# UI/UX Design Specification: {summary}\n\n## Screens\n- Landing Page\n- Dashboard"

        return f"# {prompt_name} Document for {summary}"
