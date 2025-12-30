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
        idea = variables.get('idea', variables.get('bundle', 'Project Idea'))
        
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

        if prompt_name == 'SCREEN_INVENTORY':
            # Smarter fallback using idea keywords
            lower_idea = idea.lower()
            screens = [
                {"name": "Landing Page", "category": "Public", "description": "Welcome screen"},
                {"name": "Login", "category": "Auth", "description": "Login page"},
                {"name": "Register", "category": "Auth", "description": "Sign up page"}
            ]
            
            if "social" in lower_idea or "content" in lower_idea:
                screens.append({"name": "Home Feed", "category": "User", "description": "Social feed of posts"})
                screens.append({"name": "Create Post", "category": "User", "description": "Create new content"})
                screens.append({"name": "Profile", "category": "User", "description": "User profile screen"})
            
            if "chat" in lower_idea or "message" in lower_idea:
                screens.append({"name": "Messages", "category": "User", "description": "List of conversations"})
                screens.append({"name": "Chat Detail", "category": "User", "description": "One-on-one chat screen"})

            if "subscription" in lower_idea or "payment" in lower_idea or "ecommerce" in lower_idea:
                screens.append({"name": "Pricing Plans", "category": "User", "description": "Subscription options"})
                screens.append({"name": "Payment Gateway", "category": "User", "description": "Secure checkout"})
                screens.append({"name": "Transaction History", "category": "User", "description": "List of payments"})

            screens.extend([
                {"name": "Dashboard", "category": "User", "description": "Main user interface"},
                {"name": "Settings", "category": "User", "description": "User preferences"},
                {"name": "Notifications", "category": "User", "description": "Activity alerts"}
            ])

            return json.dumps({"screen_inventory": screens}, indent=2)

        if prompt_name == 'UI_CONTRACTS':
            inventory_raw = variables.get('screen_inventory', '{}')
            inventory = {}
            try: inventory = json.loads(inventory_raw)
            except: pass
            
            screens = inventory.get('screen_inventory', [])
            if not screens:
                screens = [{"name": "Landing Page", "role": "Public"}]
            
            contracts = []
            for s in screens:
                name = s.get('name', 'Screen')
                contracts.append({
                    "screen": name,
                    "role": s.get('category', 'User'),
                    "purpose": s.get('description', f"Interaction for {name}"),
                    "actions": ["View Content", "Interact"],
                    "components": ["Header", "ContentArea", "Footer"],
                    "data": ["id", "title"],
                    "state": ["Default"],
                    "navigation": ["Dashboard"]
                })
            return json.dumps({"ui_contracts": contracts}, indent=2)

        if prompt_name == 'WIREFRAMES':
            contracts_raw = variables.get('ui_contracts', '{}')
            contracts_data = {}
            try: contracts_data = json.loads(contracts_raw)
            except: pass
            
            screens = contracts_data.get('ui_contracts', [])
            if not screens:
                screens = [{"screen": "Landing Page"}]
            
            wireframes = []
            for s in screens:
                name = s.get('screen', 'Screen')
                key = name[0].lower() + name[1:].replace(' ', '')
                
                is_landing = any(x in name for x in ["Landing", "Home", "Welcome"])
                is_auth = any(x in name for x in ["Login", "Sign", "Register", "Password"])
                
                layout = []
                
                if is_auth:
                    layout = [
                        {
                            "section": "Main",
                            "components": [
                                {"key": "Auth", "type": "AuthCard", "label": "Switch to Register", "annotation": "Centered Auth Block"}
                            ]
                        }
                    ]
                elif is_landing:
                    layout = [
                        {
                            "section": "Header",
                            "components": [
                                {"key": "L1", "type": "Link", "label": "Features"},
                                {"key": "L2", "type": "Link", "label": "Pricing"},
                                {"key": "B1", "type": "Button", "label": "Get Started"}
                            ]
                        },
                        {
                            "section": "Main",
                            "components": [
                                {"key": "H1", "type": "Card", "label": "Hero Headline", "annotation": "Main value proposition"},
                                {"key": "F1", "type": "StatCard", "label": "Metric 1", "annotation": "Proof point"},
                                {"key": "F2", "type": "StatCard", "label": "Metric 2", "annotation": "Proof point"},
                                {"key": "F3", "type": "StatCard", "label": "Metric 3", "annotation": "Proof point"}
                            ]
                        }
                    ]
                else:
                    # Dashboard / App Mode
                    is_settings = any(x in name for x in ["Setting", "Account", "Config"])
                    is_notifications = any(x in name for x in ["Notification", "Message", "Alert"])
                    is_profile = any(x in name for x in ["Profile", "User", "Bio"])
                    
                    header = {
                        "section": "Header",
                        "components": [
                            {"key": "Search", "type": "SearchBar", "label": "Search..."},
                            {"key": "User", "type": "ProfileCircle", "label": "User Profile"}
                        ]
                    }
                    sidebar = {
                        "section": "Sidebar",
                        "components": [
                            {"key": "Nav1", "type": "Button", "label": "Dashboard"},
                            {"key": "Nav2", "type": "Button", "label": "Analytics"},
                            {"key": "Nav3", "type": "Button", "label": "Settings"}
                        ]
                    }

                    if is_settings:
                        layout = [header, sidebar, {
                            "section": "Main",
                            "components": [
                                {"key": "I1", "type": "Input", "label": "Display Name", "annotation": "User's public name"},
                                {"key": "I2", "type": "Input", "label": "Email Address", "annotation": "Primary contact"},
                                {"key": "I3", "type": "Card", "label": "Privacy Settings", "annotation": "Toggle visibility rules"},
                                {"key": "B1", "type": "Button", "label": "Save Changes"}
                            ]
                        }]
                    elif is_notifications:
                        layout = [header, sidebar, {
                            "section": "Main",
                            "components": [
                                {"key": "N1", "type": "Card", "label": "New Subscription", "annotation": "2 minutes ago"},
                                {"key": "N2", "type": "Card", "label": "Payment Received", "annotation": "1 hour ago"},
                                {"key": "N3", "type": "Card", "label": "System Update", "annotation": "Yesterday"}
                            ]
                        }]
                    elif is_profile:
                        layout = [header, sidebar, 
                        {
                            "section": "SubHeader",
                            "components": [
                                {"key": "P1", "type": "StatCard", "label": "Posts Made"},
                                {"key": "P2", "type": "StatCard", "label": "Followers"},
                                {"key": "P3", "type": "StatCard", "label": "Engagement"}
                            ]
                        },
                        {
                            "section": "Main",
                            "components": [
                                {"key": "Bio", "type": "Card", "label": "User Biography", "annotation": "Short description about the user"},
                                {"key": "Feed", "type": "Table", "label": "Recent Activity"}
                            ]
                        }]
                    else:
                        layout = [header, sidebar, 
                        {
                            "section": "SubHeader",
                            "components": [
                                {"key": "S1", "type": "StatCard", "label": "Metric A"},
                                {"key": "S2", "type": "StatCard", "label": "Metric B"},
                                {"key": "S3", "type": "StatCard", "label": "Metric C"}
                            ]
                        },
                        {
                            "section": "Main",
                            "components": [
                                {"key": "P1", "type": "PostCard", "label": "General Overview Feed"},
                                {"key": "T1", "type": "Table", "label": "Data Records"}
                            ]
                        }]

                wireframes.append({
                    "screen": name,
                    "screenKey": key,
                    "purpose": f"Overview and management for {name}",
                    "layout": layout,
                    "primary_action": "Create New",
                    "flow": "Navigation → Action → Confirmation"
                })
            return json.dumps({"wireframes": wireframes}, indent=2)

        if prompt_name == 'FIGMA_LAYOUT':
            wireframes_raw = variables.get('wireframes', '{}')
            wf_data = {}
            try: wf_data = json.loads(wireframes_raw)
            except: pass
            
            screens = wf_data.get('wireframes', [])
            if not screens:
                screens = [{"screen": "Landing Page", "screenKey": "landingPage"}]
            
            frames = []
            for s in screens:
                frames.append({
                    "name": s.get('screenKey', 'screen'),
                    "description": s.get('screen', 'Screen'),
                    "layoutType": "fullPage",
                    "sections": [
                        {"name": "Main", "components": [{"key": "HeroSection"}]}
                    ]
                })
            
            return json.dumps({
                "figma": {
                    "pages": [
                        {
                            "name": "Project Wireframes / UI",
                            "frames": frames
                        }
                    ]
                }
            }, indent=2)

        if prompt_name == 'UI_DESIGN':
            return json.dumps({
                "design_tokens": {"colors": {"primary": "#000000"}},
                "screens": []
            }, indent=2)

        return f"# {prompt_name} Document for {summary}"
