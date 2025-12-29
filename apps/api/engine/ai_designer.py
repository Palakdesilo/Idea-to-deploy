import uuid
import json
from pathlib import Path
from typing import List, Dict, Any

class AIDesigner:
    async def generate_visuals(self, project_id: str, description: str) -> List[Dict[str, Any]]:
        # Try to load UI design and contracts from artifacts
        artifacts_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "docs"
        ui_design_file = artifacts_dir / "ui_design.json"
        ui_contracts_file = artifacts_dir / "ui_contracts.json"
        
        visuals = []
        
        # If UI design artifacts exist, generate visuals from them
        if ui_design_file.exists() and ui_contracts_file.exists():
            try:
                with open(ui_design_file, 'r', encoding='utf-8') as f:
                    ui_design = json.load(f)
                
                with open(ui_contracts_file, 'r', encoding='utf-8') as f:
                    ui_contracts = json.load(f)
                
                # Extract screens from UI design
                screens = ui_design.get('screens', [])
                contracts = ui_contracts.get('ui_contracts', [])
                
                # Create a mapping of screen names to contracts
                contract_map = {c['screen']: c for c in contracts}
                
                for screen in screens:
                    screen_name = screen.get('screen', 'Unnamed Screen')
                    contract = contract_map.get(screen_name, {})
                    
                    # Extract components from layout
                    components = []
                    for section in screen.get('layout', []):
                        for comp in section.get('components', []):
                            comp_name = comp.get('name', comp) if isinstance(comp, dict) else comp
                            components.append(comp_name)
                    
                    visual = {
                        "id": str(uuid.uuid4()),
                        "projectId": project_id,
                        "screenName": screen_name,
                        "description": contract.get('purpose', f'UI design for {screen_name}'),
                        "imageUrl": f"https://images.unsplash.com/photo-{1551288049 + len(visuals)}-bebda4e38f71",
                        "promptUsed": f"E-commerce {screen_name}",
                        "purpose": contract.get('purpose', 'Screen view'),
                        "roles": [contract.get('role', 'User')],
                        "components": components[:5],  # Limit to 5 for display
                        "interactions": contract.get('actions', [])[:3],  # Limit to 3
                        "states": contract.get('states', ['Default'])
                    }
                    visuals.append(visual)
                
                return visuals
            except Exception as e:
                print(f"Error loading UI artifacts: {e}")
                # Fall through to default
        
        # Fallback to default visual if no artifacts found
        return [{
            "id": str(uuid.uuid4()),
            "projectId": project_id,
            "screenName": "Dashboard",
            "description": f"Design for {description[:30]}",
            "imageUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
            "promptUsed": "Premium UI",
            "purpose": "Main view",
            "roles": ["Admin"],
            "components": ["Charts"],
            "interactions": ["Click"],
            "states": ["Default"]
        }]
