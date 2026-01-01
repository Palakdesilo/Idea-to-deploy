import uuid
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from .wireframe_renderer import WireframeRenderer
from .ui_renderer import UIRenderer
from .llm_service import LLMService
from .ai_prompts import VISUAL_PROMPT_PROMPT

class AIDesigner:
    async def generate_visuals(self, project_id: str, description: str) -> List[Dict[str, Any]]:
        from .project_manager import ProjectManager, ARTIFACTS_DIR
        pm = ProjectManager()
        llm = LLMService()
        visuals = []
        
        # 1. Load structured wireframes and UI designs from artifacts
        artifacts_dir = ARTIFACTS_DIR / project_id / "docs"
        wireframes_file = artifacts_dir / "wireframes.json"
        ui_design_file = artifacts_dir / "ui_design.json"
        
        if wireframes_file.exists():
            try:
                with open(wireframes_file, 'r', encoding='utf-8') as f:
                    wire_data = json.loads(f.read())
                    screens = wire_data.get('wireframes', [])
                    
                    # Get project name
                    project = await pm.get_project(project_id)
                    project_name = project.name if project else "Project"

                    # Render Low-Fi Wireframes
                    renderer = WireframeRenderer()
                    renderer.render_project(project_id, screens)
                    
                    # Render High-Fi UI
                    ui_data = {}
                    if ui_design_file.exists():
                        with open(ui_design_file, 'r', encoding='utf-8') as f2:
                            ui_data = json.loads(f2.read())
                    
                    ui_renderer = UIRenderer()
                    ui_renderer.render_project(project_id, screens, ui_data, project_name=project_name)
                
                for idx, wf in enumerate(screens):
                    raw_name = wf.get('screen', wf.get('screenTitle', wf.get('screenKey', 'Screen')))
                    screen_name = raw_name.split(' / ')[0].replace(' Screen', '').strip()
                    screen_key = wf.get('screenKey', '').lower()
                    if not screen_key:
                        screen_key = screen_name.lower().replace(' ', '')
                    
                    # Extract flat list of all components across all sections for metadata
                    all_components = []
                    for section in wf.get('layout', []):
                        for comp in section.get('components', []):
                            if isinstance(comp, dict):
                                all_components.append(comp.get('key', 'Component'))
                            else:
                                all_components.append(str(comp))
                                
                    # Determine roles
                    screen_lower = screen_name.lower()
                    roles = ["Admin", "User"] if screen_lower in ["dashboard", "settings", "analytics"] else ["Public", "User"]

                    # Determine the visual theme using Gemini (as requested)
                    visual_prompt = await llm.generate_content(
                        'VISUAL_PROMPT',
                        {
                            "idea": description,
                            "screen_name": screen_name,
                            "purpose": wf.get('purpose', f"Interface for {screen_name}")
                        },
                        VISUAL_PROMPT_PROMPT
                    )
                    prompt = visual_prompt or f"Modern UI, {screen_name} for {description}. 4k."
                    
                    image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"

                    visuals.append({
                        "id": str(uuid.uuid4()),
                        "projectId": project_id,
                        "screenName": screen_name,
                        "description": wf.get('purpose', f"Interface for {screen_name}"),
                        "imageUrl": image_url,
                        "promptUsed": prompt,
                        "purpose": wf.get('purpose', ""),
                        "roles": roles,
                        "components": all_components,
                        "interactions": [],
                        "states": ["Default"],
                        "wireframeKey": screen_key,
                        "uiKey": screen_key
                    })
            except Exception as e:
                print(f"AIDesigner: Error loading wireframes.json: {e}")

        # 2. If no wireframes.json, try loading from doc storage (legacy or UI_UX specification)
        if not visuals:
            docs = await pm.get_docs(project_id)
            uiux_doc = next((d for d in docs if d.category == 'UI_UX'), None)
            
            if uiux_doc:
                if uiux_doc.content.strip().startswith('{'):
                    try:
                        data = json.loads(uiux_doc.content)
                        screens = data.get('wireframes', [])
                        for idx, wf in enumerate(screens):
                            raw_name = wf.get('screen', wf.get('screenTitle', wf.get('screenKey', 'Screen')))
                            screen_name = raw_name.split(' / ')[0].replace(' Screen', '').strip()
                            screen_key = wf.get('screenKey') or (screen_name[0].lower() + screen_name[1:].replace(' ', ''))
                            
                            prompt = f"UI mockup, {screen_name} for {description}. 4k."
                            image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                            
                            visuals.append({
                                "id": str(uuid.uuid4()),
                                "projectId": project_id,
                                "screenName": screen_name,
                                "description": wf.get('purpose', f"Interface for {screen_name}"),
                                "imageUrl": image_url,
                                "promptUsed": prompt,
                                "purpose": wf.get('purpose', ""),
                                "roles": [wf.get('role', "User")],
                                "components": [],
                                "interactions": [],
                                "states": ["Default"],
                                "wireframeKey": screen_key,
                                "uiKey": screen_key
                            })
                    except: pass
                else:
                    # Markdown parsing
                    sections = uiux_doc.content.split('### ')[1:]
                    for idx, section in enumerate(sections):
                        screen_name = section.split('\n')[0].strip()
                        screen_key = screen_name[0].lower() + screen_name[1:].replace(' ', '')
                        prompt = f"Modern UI, {screen_name} for {description}. 4k."
                        image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                        visuals.append({
                            "id": str(uuid.uuid4()),
                            "projectId": project_id,
                            "screenName": screen_name,
                            "description": f"Interface for {screen_name}",
                            "imageUrl": image_url,
                            "promptUsed": prompt,
                            "purpose": "",
                            "roles": ["User"],
                            "components": [],
                            "interactions": [],
                            "states": ["Default"],
                            "wireframeKey": screen_key,
                            "uiKey": screen_key
                        })

        if not visuals:
            default_screens = ["Landing Page", "Login", "Register", "Dashboard", "Settings", "Analytics", "Profile"]
            fallback_wireframes = []
            
            for idx, screen in enumerate(default_screens):
                screen_lower = screen.lower()
                screen_key = screen_lower.replace(" ", "")
                prompt = f"Modern {screen} screen for {description}. 4k."
                image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                
                # Role Based Access
                roles = ["Admin", "User"] if screen_lower in ["dashboard", "settings", "analytics"] else ["Public", "User"]
                
                visuals.append({
                    "id": str(uuid.uuid4()),
                    "projectId": project_id,
                    "screenName": screen,
                    "description": f"Interface for {screen}",
                    "imageUrl": image_url,
                    "promptUsed": prompt,
                    "purpose": f"User interaction for {screen}",
                    "roles": roles,
                    "components": [],
                    "interactions": ["Click", "Input"],
                    "states": ["Default"],
                    "wireframeKey": screen_key,
                    "uiKey": screen_key
                })
                
                # CUSTOM LAYOUTS BASED ON SCREEN TYPE
                layout = []
                
                if "landing" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": "Product"}]},
                        {"section": "Hero", "components": [{"type": "Hero", "label": "Build Faster", "content": "The ultimate platform for your needs.", "subtext": "Get Started"}]},
                        {"section": "Features", "components": [{"type": "FeatureGrid", "label": "Key Features", "content": "AI Powered Analysis"}]},
                        {"section": "Testimonials", "components": [{"type": "TestimonialGrid", "label": "What Users Say", "content": [{"user": "Alex", "quote": "Incredible tool!", "rating": 5}]}]},
                        {"section": "Footer", "components": [{"type": "Footer", "label": "Footer"}]}
                    ]
                elif "login" in screen_lower or "register" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": "Product"}]},
                        {"section": "Auth", "components": [{"type": "AuthCard", "label": screen}]},
                        {"section": "Footer", "components": [{"type": "Footer", "label": "Footer"}]}
                    ]
                elif "dashboard" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": screen}]},
                        {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                        {"section": "Stats", "components": [{"type": "StatGrid", "label": "Overview", "content": [{"label": "Total Users", "value": "12.5k"}, {"label": "Revenue", "value": "$120k"}, {"label": "Growth", "value": "+24%"}]}]},
                        {"section": "Table", "components": [{"type": "Table", "label": "Recent Transactions", "content": [{"item": "Subscription", "date": "2m ago", "status": "Paid"}, {"item": "Refund", "date": "1h ago", "status": "Pending"}]}]}
                    ]
                elif "settings" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": screen}]},
                        {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                        {"section": "Profile Settings", "components": [
                            {"type": "Input", "label": "Full Name", "subtext": "Enter your name"},
                            {"type": "Input", "label": "Email Address", "subtext": "Enter your email"},
                            {"type": "Button", "label": "Save Changes", "variant": "primary"}
                        ]},
                        {"section": "Preferences", "components": [
                            {"type": "Input", "label": "Notification Email", "subtext": "Secondary email"},
                            {"type": "Button", "label": "Update Password", "variant": "outline"}
                        ]}
                    ]
                elif "analytics" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": screen}]},
                        {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                        {"section": "MainCharts", "components": [{"type": "StatGrid", "label": "Traffic Sources", "content": [{"label": "Organic", "value": "45%"}, {"label": "Social", "value": "30%"}, {"label": "Direct", "value": "25%"}]}]},
                        {"section": "Engagement", "components": [{"type": "StatGrid", "label": "Engagement", "content": [{"label": "Bounce Rate", "value": "42%"}, {"label": "Avg. Session", "value": "4m 30s"}]}]},
                        {"section": "Detailed Data", "components": [{"type": "Table", "label": "Top Pages", "content": [{"item": "/home", "date": "15k views", "status": "High"}, {"item": "/pricing", "date": "8k views", "status": "Med"}]}]}
                    ]
                elif "profile" in screen_lower:
                    layout = [
                        {"section": "Header", "components": [{"type": "Header", "label": screen}]},
                        {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                        {"section": "UserInfo", "components": [
                            {"type": "Input", "label": "Username", "subtext": "johndoe123"},
                            {"type": "Input", "label": "Bio", "subtext": "Product Designer at Tech Co."},
                            {"type": "Button", "label": "Edit Profile", "variant": "primary"}
                        ]},
                        {"section": "Activity", "components": [{"type": "PostCard", "label": "Recent Post", "content": "Just launched my new portfolio!"}]}
                    ]

                # Create minimal wireframe data for rendering
                fallback_wireframes.append({
                    "screen": screen,
                    "screenKey": screen_key, # Use the computed key
                    "purpose": f"User interaction for {screen}",
                    "layout": layout
                })

            # Ensure HTML files are generated for these fallback screens
            try:
                WireframeRenderer().render_project(project_id, fallback_wireframes)
                UIRenderer().render_project(project_id, fallback_wireframes, {})
            except Exception as e:
                print(f"AIDesigner: Error rendering fallback screens: {e}")
                
        return visuals
