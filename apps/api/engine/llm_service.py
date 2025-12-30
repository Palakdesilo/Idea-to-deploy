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
            lower_idea = idea.lower()
            screens = [
                {"name": "Landing Page", "category": "Public", "description": "Welcome screen"},
                {"name": "Login", "category": "Auth", "description": "Access account"},
            ]
            
            # Detect Niche
            is_portfolio = any(x in lower_idea for x in ["portfolio", "showcase", "cv", "resume", "student"])
            is_social = any(x in lower_idea for x in ["social", "community", "chat", "network"])
            is_ecommerce = any(x in lower_idea for x in ["store", "shop", "ecommerce", "cart", "product"])
            is_learning = any(x in lower_idea for x in ["learn", "course", "lms", "education", "student"])

            if is_portfolio:
                screens.append({"name": "Work Gallery", "category": "User", "description": "Showcase of projects"})
                screens.append({"name": "Experience Timeline", "category": "User", "description": "Work and education history"})
                screens.append({"name": "Skill Matrix", "category": "User", "description": "Technical and soft skills"})
            elif is_social:
                screens.append({"name": "Home Feed", "category": "User", "description": "Social feed of posts"})
                screens.append({"name": "Friend List", "category": "User", "description": "Connected people"})
            elif is_ecommerce:
                screens.append({"name": "Product Catalog", "category": "User", "description": "Browsing items"})
                screens.append({"name": "Shopping Cart", "category": "User", "description": "Reviewing selected items"})
                screens.append({"name": "Checkout", "category": "User", "description": "Payment and shipping"})
            elif is_learning:
                screens.append({"name": "Course Dashboard", "category": "User", "description": "Track progress"})
                screens.append({"name": "Lesson View", "category": "User", "description": "Video or text content"})

            screens.extend([
                {"name": "User Dashboard", "category": "User", "description": "Main control center"},
                {"name": "Account Settings", "category": "User", "description": "Profile management"},
                {"name": "Alert Center", "category": "User", "description": "All notifications"}
            ])

            return json.dumps({"screen_inventory": screens}, indent=2)

        if prompt_name == 'UI_CONTRACTS':
            inventory_raw = variables.get('screen_inventory', '{}')
            inventory = {}
            try: inventory = json.loads(inventory_raw)
            except: pass
            
            screens = inventory.get('screen_inventory', [])
            if not screens: screens = [{"name": "Landing Page"}]
            
            contracts = []
            for s in screens:
                name = s.get('name', 'Screen')
                desc = s.get('description', f"Interface for {name}")
                
                # Dynamic components based on screen name
                comps = ["Header", "Nav"]
                if "Feed" in name or "Gallery" in name: comps += ["Search", "Grid", "CardList"]
                elif "Catalog" in name: comps += ["Filter", "ProductGrid"]
                elif "Settings" in name: comps += ["Form", "Tabs", "Toggles"]
                elif "Dashboard" in name: comps += ["Stats", "SummaryTable", "ActivityFeed"]
                else: comps += ["Content", "Footer"]

                contracts.append({
                    "screen": name,
                    "role": s.get('category', 'User'),
                    "purpose": desc,
                    "actions": ["Explore", "Submit"],
                    "components": comps,
                    "data": ["id", "title", "metadata"],
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
            if not screens: screens = [{"screen": "Landing Page"}]
            
            wireframes = []
            for s in screens:
                name = s.get('screen', 'Screen')
                key = name[0].lower() + name[1:].replace(' ', '')
                is_auth = any(x in name for x in ["Login", "Sign", "Register", "Password"])
                is_landing = any(x in name for x in ["Landing", "Home", "Welcome"])
                
                header = {"section": "Header", "components": [{"key": "S1", "type": "SearchBar", "label": "Search..."}, {"key": "U1", "type": "ProfileCircle", "label": "User"}]}
                sidebar = {"section": "Sidebar", "components": [{"key": "N1", "type": "Button", "label": "Home"}, {"key": "N2", "type": "Button", "label": name}]}
                
                layout = []
                if is_auth:
                    layout = [{"section": "Main", "components": [{"key": "Auth", "type": "AuthCard", "label": name, "annotation": "Auth block"}]}]
                elif is_landing:
                    layout = [
                        {"section": "Header", "components": [{"key": "H1", "type": "Link", "label": "Features"}, {"key": "H2", "type": "Button", "label": "Join"}]},
                        {"section": "Main", "components": [{"key": "Hero", "type": "Card", "label": idea.split()[-1].capitalize() + " Platform", "annotation": "Value prop"}]}
                    ]
                else:
                    # Dynamic Niche-Specific Layouts
                    if "Gallery" in name or "Feed" in name:
                        layout = [header, sidebar, {"section": "Main", "components": [
                            {"key": "C1", "type": "ProjectCard", "label": "Case Study: Mobile App Design"},
                            {"key": "C2", "type": "ProjectCard", "label": "Brand Identity: Fintech Startup"}
                        ]}]
                    elif "Timeline" in name or "History" in name:
                        layout = [header, sidebar, {"section": "Main", "components": [
                            {"key": "T1", "type": "TimelineItem", "label": "Lead Developer Role", "annotation": "2022 - Present"},
                            {"key": "T2", "type": "TimelineItem", "label": "Senior Designer Role", "annotation": "2020 - 2022"},
                            {"key": "T3", "type": "TimelineItem", "label": "University Education", "annotation": "2016 - 2020"}
                        ]}]
                    elif "Skill" in name or "Ability" in name:
                        layout = [header, sidebar, {"section": "Main", "components": [
                            {"key": "S1", "type": "SkillItem", "label": "Python"},
                            {"key": "S2", "type": "SkillItem", "label": "Next.js"},
                            {"key": "S3", "type": "SkillItem", "label": "UI Design"},
                            {"key": "S4", "type": "SkillItem", "label": "Cloud Arch"}
                        ]}]
                    elif "Settings" in name:
                         layout = [header, sidebar, {"section": "Main", "components": [
                            {"key": "I1", "type": "Input", "label": "Display Info"},
                            {"key": "I2", "type": "Button", "label": "Save Preferences"}
                        ]}]
                    elif "Dashboard" in name or "Stats" in name:
                         layout = [header, sidebar, 
                            {"section": "SubHeader", "components": [
                                {"key": "M1", "type": "StatCard", "label": "Core Metric"},
                                {"key": "M2", "type": "StatCard", "label": "Secondary"},
                                {"key": "M3", "type": "StatCard", "label": "Growth"}
                            ]},
                            {"section": "Main", "components": [{"key": "T1", "type": "Table", "label": "Recent Activity"}]}
                         ]
                    else:
                        layout = [header, sidebar, {"section": "Main", "components": [
                            {"key": "X1", "type": "Card", "label": f"{name} Content", "annotation": "Main workspace area"}
                        ]}]

                wireframes.append({
                    "screen": name, "screenKey": key, "route": "/"+key, "shellType": "Internal",
                    "purpose": s.get('purpose', ""), "layout": layout, "primary_action": "Proceed", "flow": "Standard flow"
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
