import uuid
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from .wireframe_renderer import WireframeRenderer

class AIDesigner:
    async def generate_visuals(self, project_id: str, description: str) -> List[Dict[str, Any]]:
        from .project_manager import ProjectManager
        pm = ProjectManager()
        visuals = []
        
        # 1. Load structured wireframes.json from artifacts if it exists
        artifacts_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "docs"
        wireframes_file = artifacts_dir / "wireframes.json"
        
        if wireframes_file.exists():
            try:
                with open(wireframes_file, 'r', encoding='utf-8') as f:
                    data = json.loads(f.read())
                    screens = data.get('wireframes', [])
                    
                    # Render these JSON wireframes to HTML files
                    renderer = WireframeRenderer()
                    renderer.render_project(project_id, screens)
                    
                    for idx, wf in enumerate(screens):
                        raw_name = wf.get('screen', wf.get('screenTitle', wf.get('screenKey', 'Screen')))
                        screen_name = raw_name.split(' / ')[0].replace(' Screen', '').strip()
                        screen_key = wf.get('screenKey')
                        
                        if not screen_key:
                            # Fallback camelCase
                            screen_key = screen_name[0].lower() + screen_name[1:].replace(' ', '')
                        
                        # Extract flat list of all components across all sections for metadata
                        all_components = []
                        for section in wf.get('layout', []):
                            for comp in section.get('components', []):
                                if isinstance(comp, dict):
                                    all_components.append(comp.get('key', 'Component'))
                                else:
                                    all_components.append(str(comp))

                        prompt = f"Professional UI mockup, {screen_name} for {description}. Modern SaaS design, high-fidelity, blue and white theme, 4k."
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
                            "components": all_components,
                            "interactions": [],
                            "states": ["Default"],
                            "wireframeKey": screen_key
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
                                "wireframeKey": screen_key
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
                            "wireframeKey": screen_key
                        })

        # 3. Final Fallback (The 4 screens you saw)
        if not visuals:
            default_screens = ["Dashboard", "Settings", "Analytics", "Profile"]
            for idx, screen in enumerate(default_screens):
                prompt = f"Modern {screen} screen for {description}. 4k."
                image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                visuals.append({
                    "id": str(uuid.uuid4()),
                    "projectId": project_id,
                    "screenName": screen,
                    "description": f"A sleek {screen.lower()}",
                    "imageUrl": image_url,
                    "promptUsed": prompt,
                    "purpose": f"User interaction for {screen}",
                    "roles": ["Admin", "User"],
                    "components": ["Header", "Sidebar", "Main Content"],
                    "interactions": ["Scroll", "Click"],
                    "states": ["Default", "Loading"],
                    "wireframeKey": screen.lower()
                })
                
        return visuals
