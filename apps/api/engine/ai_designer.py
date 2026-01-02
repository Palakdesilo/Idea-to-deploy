import uuid
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from .wireframe_renderer import WireframeRenderer
from .ui_renderer import UIRenderer
from .llm_service import LLMService
from .ai_prompts import VISUAL_PROMPT_PROMPT, WIREFRAMES_PROMPT, DYNAMIC_SCREENS_PROMPT

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
            # DYNAMIC FALLBACK: Generate wireframes on the fly using LLM to ensure uniqueness
            print(f"AIDesigner: Generating dynamic wireframes for '{description}'...")
            try:
                # Use the dedicated DYNAMIC_SCREENS_PROMPT for one-shot generation
                prompt = DYNAMIC_SCREENS_PROMPT.format(idea=description)
                
                # Call LLM
                response_str = await llm.generate_content("DynamicWireframes", {"idea": description}, prompt)
                
                # Clean and parse JSON
                # Clean and parse JSON using robust regex
                clean_json = response_str.strip()
                match = re.search(r'```json\s*(.*?)\s*```', response_str, re.DOTALL)
                if match:
                    clean_json = match.group(1).strip()
                else:
                    match = re.search(r'```\s*(.*?)\s*```', response_str, re.DOTALL)
                    if match:
                        clean_json = match.group(1).strip()
                
                # Verify we have braces, if not try to find them
                if not clean_json.startswith('{'):
                    start = clean_json.find('{')
                    end = clean_json.rfind('}')
                    if start != -1 and end != -1:
                        clean_json = clean_json[start:end+1]

                print(f"AIDesigner: Parsed JSON length: {len(clean_json)}")
                generated_data = json.loads(clean_json)
                dynamic_screens = generated_data.get("wireframes", [])
                
                fallback_wireframes = []

                if not dynamic_screens:
                    raise Exception("No wireframes returned from LLM")

                for idx, wf in enumerate(dynamic_screens):
                    screen = wf.get("screen", f"Screen {idx}")
                    screen_key = wf.get("screenKey", screen.lower().replace(" ", ""))
                    
                    # Generate a beautiful placeholder image
                    prompt_visual = f"Modern high-fidelity UI design, {screen} screen for {description}, dark mode, premium aesthetic. 4k."
                    image_url = f"https://pollinations.ai/p/{prompt_visual.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                    
                    roles = ["Admin", "User"] if any(x in screen.lower() for x in ["dashboard", "admin", "settings"]) else ["User"]
                    
                    # Store for visual list
                    visuals.append({
                        "id": str(uuid.uuid4()),
                        "projectId": project_id,
                        "screenName": screen,
                        "description": f"Interface for {screen}",
                        "imageUrl": image_url,
                        "promptUsed": prompt_visual,
                        "purpose": wf.get("purpose", f"User interaction for {screen}"),
                        "roles": roles,
                        "components": [], # Components are inside html, not needed here for basic visual
                        "interactions": ["Click", "Input"],
                        "states": ["Default"],
                        "wireframeKey": screen_key,
                        "uiKey": screen_key
                    })
                    
                    # Store structured data for HTML rendering
                    fallback_wireframes.append(wf)
                
                # Render the HTML files for these dynamically generated screens
                WireframeRenderer().render_project(project_id, fallback_wireframes)
                UIRenderer().render_project(project_id, fallback_wireframes, {}, project_name=description.split(' ')[0])
                
            except Exception as e:
                with open("debug_dynamic_gen_error.log", "w", encoding="utf-8") as f:
                    f.write(f"Error: {str(e)}\n\nResponse:\n{response_str if 'response_str' in locals() else 'NO RESPONSE'}")
                print(f"AIDesigner: Dynamic generation failed ({e}), reverting to static fallback.")
                
                # STATIC FALLBACK (Last Resort)
                default_screens = ["Landing Page", "Login", "Register", "Dashboard", "Settings"]
                fallback_wireframes = []
                
                for idx, screen in enumerate(default_screens):
                    screen_lower = screen.lower()
                    screen_key = screen_lower.replace(" ", "")
                    prompt = f"Modern {screen} screen for {description}. 4k."
                    image_url = f"https://pollinations.ai/p/{prompt.replace(' ', '%20')}?width=1280&height=720&seed={idx}&nologo=true"
                    
                    visuals.append({
                        "id": str(uuid.uuid4()),
                        "projectId": project_id,
                        "screenName": screen,
                        "description": f"Interface for {screen}",
                        "imageUrl": image_url,
                        "promptUsed": prompt,
                        "purpose": f"User interaction for {screen}",
                        "roles": ["User"],
                        "components": [],
                        "interactions": ["Click", "Input"],
                        "states": ["Default"],
                        "wireframeKey": screen_key,
                        "uiKey": screen_key
                    })
                    
                    # Minimal Layout
                    layout = []
                    if "landing" in screen_lower:
                        layout = [{"section": "Hero", "components": [{"type": "Hero", "label": "Welcome", "content": description}]}]
                    else:
                        layout = [{"section": "Content", "components": [{"type": "Card", "label": screen}]}]
                        
                    fallback_wireframes.append({
                        "screen": screen, "screenKey": screen_key, "layout": layout
                    })
                
                UIRenderer().render_project(project_id, fallback_wireframes, {}, project_name="Project")
                # Also render wireframe HTMLs for the fallback screens so the "Select a screen" view works
                WireframeRenderer().render_project(project_id, fallback_wireframes)

                # --- GENERATE MISSING FIGMA ARTIFACTS ---
                print("AIDesigner: Generating missing Figma artifacts for dynamic screens...")
                try:
                    # 1. Construct Synthetic Figma Layout from Wireframes
                    synthetic_pages = []
                    current_frames = []
                    for i, wf in enumerate(fallback_wireframes):
                        # Convert wireframe layout to figma frame structure
                        f_sections = []
                        for section in wf.get("layout", []):
                            f_comps = []
                            for comp in section.get("components", []):
                                c_key = comp.get("label", "Component")
                                f_comps.append({"key": c_key})
                            
                            f_sections.append({
                                "name": section.get("section", "Section"),
                                "components": f_comps
                            })

                        current_frames.append({
                            "name": wf.get("screen", f"Screen {i}"),
                            "sections": f_sections
                        })

                    synthetic_layout = {
                        "figma": {
                            "pages": [{"name": "Wireframes", "frames": current_frames}]
                        }
                    }

                    # 2. Save figma_layout.json
                    artifacts_dir = ARTIFACTS_DIR / project_id / "docs"
                    artifacts_dir.mkdir(parents=True, exist_ok=True)
                    
                    with open(artifacts_dir / "figma_layout.json", 'w', encoding='utf-8') as f:
                        json.dump(synthetic_layout, f, indent=2)

                    # 3. Transform and Save json_to_figma.json
                    # (Inlining the transformation logic here to avoid huge refactor/dependency)
                    def transform_to_figma(layout_data):
                        figma_data = layout_data.get('figma', {})
                        all_frames = []
                        frame_x = 0
                        frame_y = 0
                        max_frame_height = 0
                        
                        for page in figma_data.get('pages', []):
                            for frame in page.get('frames', []):
                                figma_frame = {
                                    "type": "FRAME", "name": frame.get('name', 'Frame'),
                                    "x": frame_x, "y": frame_y, "width": 1200, "height": 800,
                                    "children": [],
                                    "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                                    "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}],
                                    "strokeWeight": 1
                                }
                                
                                section_y = 40
                                for sec in frame.get('sections', []):
                                    # Simplified section generation for fallback
                                    sec_h = 100 + (len(sec.get('components', [])) * 60)
                                    sec_frame = {
                                        "type": "FRAME", "name": sec.get('name'), "x": 40, "y": section_y,
                                        "width": 1120, "height": sec_h, "children": [],
                                        "fills": [{"type": "SOLID", "color": {"r": 0.95, "g": 0.95, "b": 0.95}}],
                                        "strokes": [{"type": "SOLID", "color": {"r": 0.8, "g": 0.8, "b": 0.8}}],
                                        "strokeWeight": 1
                                    }
                                    
                                    cy = 40
                                    for comp in sec.get('components', []):
                                        sec_frame["children"].append({
                                            "type": "RECTANGLE", "name": comp.get('key'), "x": 20, "y": cy, "width": 1080, "height": 40,
                                            "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}]
                                        })
                                        sec_frame["children"].append({
                                            "type": "TEXT", "name": comp.get('key'), "characters": comp.get('key'), "x": 35, "y": cy+12, "fontSize": 12,
                                            "fills": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}]
                                        })
                                        cy += 50
                                    
                                    figma_frame["children"].append(sec_frame)
                                    section_y += sec_h + 20
                                
                                figma_frame["height"] = max(section_y + 20, 800)
                                all_frames.append(figma_frame)
                                frame_x += 1300
                        return all_frames

                    json_to_figma = transform_to_figma(synthetic_layout)
                    with open(artifacts_dir / "json_to_figma.json", 'w', encoding='utf-8') as f:
                        json.dump(json_to_figma, f, indent=2)

                    # 4. Transform and save figma_nodes_output.json
                    def generate_nodes(layout_data):
                        pages = []
                        for page in layout_data.get('figma', {}).get('pages', []):
                            f_nodes = []
                            for i, frame in enumerate(page.get('frames', [])):
                                f_nodes.append({
                                    "type": "FRAME", "name": frame.get('name'), "x": (i*850), "y": 0, "width": 800, "height": 600,
                                    "children": [],
                                    "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                                    "strokes": [{"type": "SOLID", "color": {"r": 0.5, "g": 0.5, "b": 0.5}}],
                                    "strokeWeight": 1
                                })
                            pages.append({"name": page.get("name"), "frames": f_nodes})
                        return {"pages": pages}

                    figma_nodes = generate_nodes(synthetic_layout)
                    with open(artifacts_dir / "figma_nodes_output.json", 'w', encoding='utf-8') as f:
                        json.dump(figma_nodes, f, indent=2)

                    print("AIDesigner: Successfully generated all fallback Figma artifacts.")
                    
                except Exception as e:
                    print(f"AIDesigner: Error generating Figma artifacts in fallback: {e}")
        
        return visuals
