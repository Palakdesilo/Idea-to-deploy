import json
from pathlib import Path
from .llm_service import LLMService
from .ai_prompts import (
    CANONICAL_JSON_PROMPT,
    REQUIREMENT_PROMPT, 
    PLANNING_PROMPT, 
    ARCHITECTURE_PROMPT, 
    IPMP_PROMPT, 
    SCHEDULE_COST_PROMPT, 
    QUALITY_RISK_PROMPT, 
    TESTING_RELEASE_PROMPT, 
    UI_UX_PROMPT,
    SCREEN_INVENTORY_PROMPT,
    UI_CONTRACTS_PROMPT,
    WIREFRAMES_PROMPT,
    UI_DESIGN_PROMPT,
    FIGMA_LAYOUT_PROMPT
)
from typing import Dict, List

class AIAnalyst:
    VERSION = "2.1.0-PY-DESIGN"

    def __init__(self):
        self.llm = LLMService()

    async def analyze_idea(self, idea_description: str, project_id: str = None) -> Dict[str, str]:
        # STEP 1: IDEA -> CANONICAL JSON
        print("AIAnalyst: Generating Canonical JSON...")
        canonical_json_raw = await self.llm.generate_content(
            'CANONICAL_JSON',
            {"idea": idea_description},
            CANONICAL_JSON_PROMPT
        )

        canonical_json = canonical_json_raw.strip()
        if canonical_json.startswith('```json'):
            canonical_json = canonical_json.replace('```json', '', 1).rsplit('```', 1)[0].strip()
        elif canonical_json.startswith('```'):
            canonical_json = canonical_json.replace('```', '', 1).rsplit('```', 1)[0].strip()

        try:
            json.loads(canonical_json)
        except:
            pass

        variables = {
            "canonical_json": canonical_json
        }

        # STEP 2: DOCUMENT GENERATION
        results = {}
        
        print("AIAnalyst: Generating 7 core project documents...")
        results['REQUIREMENTS'] = await self.llm.generate_content('REQUIREMENTS', variables, REQUIREMENT_PROMPT)
        results['PLANNING'] = await self.llm.generate_content('PLANNING', variables, PLANNING_PROMPT)
        results['ARCHITECTURE'] = await self.llm.generate_content('ARCHITECTURE', variables, ARCHITECTURE_PROMPT)
        results['IPMP'] = await self.llm.generate_content('IPMP', variables, IPMP_PROMPT)
        results['SCHEDULE_COST'] = await self.llm.generate_content('SCHEDULE_COST', variables, SCHEDULE_COST_PROMPT)
        results['QUALITY_RISK'] = await self.llm.generate_content('QUALITY_RISK', variables, QUALITY_RISK_PROMPT)
        results['TESTING_RELEASE'] = await self.llm.generate_content('TESTING_RELEASE', variables, TESTING_RELEASE_PROMPT)
        
        # UI_UX is now part of design artifacts
        ui_ux_raw = await self.llm.generate_content('UI_UX', variables, UI_UX_PROMPT)
        ui_ux_json = self._clean_json(ui_ux_raw)

        # STEP 3: GENERATE STRUCTURED UI DESIGN ARTIFACTS (if project_id provided)
        if project_id:
            try:
                print("AIAnalyst: Generating structured UI design artifacts...")
                
                # Bundle the 7 docs
                bundle = f"""
                REQUIREMENTS:
                {results['REQUIREMENTS']}
                
                PLANNING:
                {results['PLANNING']}
                
                ARCHITECTURE:
                {results['ARCHITECTURE']}
                
                IPMP:
                {results['IPMP']}
                
                SCHEDULE & COST:
                {results['SCHEDULE_COST']}
                
                QUALITY & RISK:
                {results['QUALITY_RISK']}
                
                TESTING & RELEASE:
                {results['TESTING_RELEASE']}
                """
                
                # Prompt A: Docs -> Screen Inventory
                print("  - Running Prompt A: Screen Inventory...")
                screen_inventory_raw = await self.llm.generate_content(
                    'SCREEN_INVENTORY', 
                    {"bundle": bundle, "idea": idea_description}, 
                    SCREEN_INVENTORY_PROMPT
                )
                screen_inventory_json = self._clean_json(screen_inventory_raw)
                
                # Prompt B: Screen Inventory -> UI Contracts
                print("  - Running Prompt B: UI Contracts...")
                ui_contracts_raw = await self.llm.generate_content(
                    'UI_CONTRACTS', 
                    {"screen_inventory": screen_inventory_json, "idea": idea_description}, 
                    UI_CONTRACTS_PROMPT
                )
                ui_contracts_json = self._clean_json(ui_contracts_raw)
                
                # Prompt C: UI Contracts -> Wireframes JSON
                print("  - Running Prompt C: Wireframes...")
                wireframes_raw = await self.llm.generate_content(
                    'WIREFRAMES',
                    {"ui_contracts": ui_contracts_json, "idea": idea_description},
                    WIREFRAMES_PROMPT
                )
                wireframes_json = self._clean_json(wireframes_raw)
                
                # Generate UI Design (Optional, but keeping for completeness)
                print("  - Generating UI Design Tokens & Styles...")
                ui_design_raw = await self.llm.generate_content(
                    'UI_DESIGN',
                    {
                        "wireframes": wireframes_json,
                        "ui_contracts": ui_contracts_json
                    },
                    UI_DESIGN_PROMPT
                )
                ui_design_json = self._clean_json(ui_design_raw)
                
                # Prompt D: Figma Layout
                print("  - Running Prompt D: Figma Layout...")
                figma_layout_raw = await self.llm.generate_content(
                    'FIGMA_LAYOUT',
                    {
                        "ui_contracts": ui_contracts_json,
                        "wireframes": wireframes_json,
                        "idea": idea_description
                    },
                    FIGMA_LAYOUT_PROMPT
                )
                figma_layout_json = self._clean_json(figma_layout_raw)
                
                # Save artifacts to files
                self._save_design_artifacts(
                    project_id, 
                    screen_inventory_json, 
                    ui_contracts_json, 
                    wireframes_json, 
                    ui_design_json,
                    figma_layout_json,
                    ui_ux_json
                )
                
                print("AIAnalyst: UI design artifacts generated and saved successfully!")
                
            except Exception as e:
                print(f"AIAnalyst: Error generating UI design artifacts: {e}")

        return results

    def _clean_json(self, raw_content: str) -> str:
        """Clean JSON content by removing markdown formatting"""
        content = raw_content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '', 1).rsplit('```', 1)[0].strip()
        elif content.startswith('```'):
            content = content.replace('```', '', 1).rsplit('```', 1)[0].strip()
        return content

    def _save_design_artifacts(self, project_id: str, screen_inventory: str, ui_contracts: str, wireframes: str, ui_design: str, figma_layout: str = None, ui_ux: str = None):
        """Save design artifacts as separate JSON files"""
        artifacts_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "docs"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save UI_UX if provided
        if ui_ux:
            with open(artifacts_dir / "ui_ux.json", 'w', encoding='utf-8') as f:
                f.write(ui_ux)
        
        # Save Screen Inventory
        with open(artifacts_dir / "screen_inventory.json", 'w', encoding='utf-8') as f:
            f.write(screen_inventory)

        # Save UI Contracts
        with open(artifacts_dir / "ui_contracts.json", 'w', encoding='utf-8') as f:
            f.write(ui_contracts)
        
        # Save Wireframes
        with open(artifacts_dir / "wireframes.json", 'w', encoding='utf-8') as f:
            f.write(wireframes)
        
        # Save UI Design
        with open(artifacts_dir / "ui_design.json", 'w', encoding='utf-8') as f:
            f.write(ui_design)

        if figma_layout:
            # Save Figma Layout
            with open(artifacts_dir / "figma_layout.json", 'w', encoding='utf-8') as f:
                f.write(figma_layout)
            
            try:
                layout_data = json.loads(figma_layout)
                
                # Transform to json_to_figma.json
                json_to_figma = self._transform_to_figma_plugin(layout_data)
                with open(artifacts_dir / "json_to_figma.json", 'w', encoding='utf-8') as f:
                    json.dump(json_to_figma, f, indent=2)
                
                # Transform to figma_nodes_output.json
                figma_nodes = self._generate_figma_nodes(layout_data)
                with open(artifacts_dir / "figma_nodes_output.json", 'w', encoding='utf-8') as f:
                    json.dump(figma_nodes, f, indent=2)
            except Exception as e:
                print(f"AIAnalyst: Error transforming Figma layout: {e}")

    def _transform_to_figma_plugin(self, layout_data: Dict) -> List:
        """Transform layout data to format suitable for JSON to Figma plugin"""
        figma_data = layout_data.get('figma', {})
        all_frames = []
        frame_x = 0
        frame_y = 0
        max_frame_height = 0
        frame_count = 0

        for page in figma_data.get('pages', []):
            for frame in page.get('frames', []):
                figma_frame = {
                    "type": "FRAME",
                    "name": frame.get('name', 'Frame'),
                    "x": frame_x,
                    "y": frame_y,
                    "width": 1200,
                    "height": 800,
                    "children": [],
                    "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                    "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}],
                    "strokeWeight": 1,
                    "cornerRadius": 8
                }
                
                section_y = 40
                for section in frame.get('sections', []):
                    section_frame = {
                        "type": "FRAME",
                        "name": section.get('name', 'Section'),
                        "x": 40,
                        "y": section_y,
                        "width": 1120,
                        "height": 100,
                        "children": [],
                        "fills": [{"type": "SOLID", "color": {"r": 0.95, "g": 0.95, "b": 0.95}}],
                        "strokes": [{"type": "SOLID", "color": {"r": 0.8, "g": 0.8, "b": 0.8}}],
                        "strokeWeight": 1
                    }
                    
                    section_frame["children"].append({
                        "type": "TEXT",
                        "name": "Section Title",
                        "characters": section.get('name', 'Section').upper(),
                        "x": 10,
                        "y": 10,
                        "fontSize": 14,
                        "fills": [{"type": "SOLID", "color": {"r": 0.2, "g": 0.2, "b": 0.2}}]
                    })
                    
                    comp_y = 40
                    for comp in section.get('components', []):
                        rect = {
                            "type": "RECTANGLE",
                            "name": comp.get('key', 'Component'),
                            "x": 20,
                            "y": comp_y,
                            "width": 1080,
                            "height": 40,
                            "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}]
                        }
                        section_frame["children"].append(rect)
                        
                        section_frame["children"].append({
                            "type": "TEXT",
                            "name": "Component Label",
                            "characters": comp.get('key', 'Component'),
                            "x": 35,
                            "y": comp_y + 12,
                            "fontSize": 12,
                            "fills": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}]
                        })
                        comp_y += 50
                    
                    section_frame["height"] = max(comp_y + 10, 60)
                    figma_frame["children"].append(section_frame)
                    section_y += section_frame["height"] + 20
                
                figma_frame["height"] = max(section_y + 20, 600)
                all_frames.append(figma_frame)
                
                frame_x += 1300
                max_frame_height = max(max_frame_height, figma_frame["height"])
                frame_count += 1
                if frame_count % 4 == 0:
                    frame_x = 0
                    frame_y += max_frame_height + 200
                    max_frame_height = 0
        return all_frames

    def _generate_figma_nodes(self, layout_plan: Dict) -> Dict:
        """Generate Figma nodes format"""
        def create_rectangle_node(component_key, x, y):
            return {
                'type': 'RECTANGLE',
                'name': component_key,
                'x': x,
                'y': y,
                'width': 200,
                'height': 50,
                'fills': [{'type': 'SOLID', 'color': {'r': 0.9, 'g': 0.9, 'b': 0.9, 'a': 1}}],
                'strokes': [],
                'strokeWeight': 0
            }

        def create_section_frame(section_name, components, y_offset):
            children = []
            current_y = 20
            for component in components:
                component_key = component.get('key', 'Component')
                rect = create_rectangle_node(component_key, 20, current_y)
                children.append(rect)
                current_y += 70
            
            return {
                'type': 'FRAME',
                'name': section_name,
                'x': 0,
                'y': y_offset,
                'width': 240,
                'height': max(current_y + 20, 100),
                'children': children,
                'fills': [{'type': 'SOLID', 'color': {'r': 0.98, 'g': 0.98, 'b': 0.98, 'a': 1}}],
                'strokes': [{'type': 'SOLID', 'color': {'r': 0.8, 'g': 0.8, 'b': 0.8, 'a': 1}}],
                'strokeWeight': 1,
                'cornerRadius': 4
            }

        def create_frame_node(frame_data):
            name = frame_data.get('name', 'Frame')
            sections = frame_data.get('sections', [])
            children = []
            current_y = 0
            
            for section in sections:
                section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), current_y)
                section_frame['x'] = 20
                section_frame['width'] = 760
                children.append(section_frame)
                current_y += section_frame['height'] + 20
            
            return {
                'type': 'FRAME',
                'name': name,
                'x': 0,
                'y': 0,
                'width': 800,
                'height': max(600, current_y + 20),
                'children': children,
                'fills': [{'type': 'SOLID', 'color': {'r': 1, 'g': 1, 'b': 1, 'a': 1}}],
                'strokes': [{'type': 'SOLID', 'color': {'r': 0.7, 'g': 0.7, 'b': 0.7, 'a': 1}}],
                'strokeWeight': 2,
                'cornerRadius': 8
            }

        pages = []
        for page_data in layout_plan.get('figma', {}).get('pages', []):
            page_name = page_data.get('name', 'Wireframes')
            frames = page_data.get('frames', [])
            frame_nodes = []
            for idx, frame_data in enumerate(frames):
                frame_node = create_frame_node(frame_data)
                frame_node['x'] = (idx % 5) * 850
                frame_node['y'] = (idx // 5) * 650
                frame_nodes.append(frame_node)
            pages.append({'name': page_name, 'frames': frame_nodes})
        
        return {'pages': pages}
