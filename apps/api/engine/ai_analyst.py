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
    UI_CONTRACTS_PROMPT,
    WIREFRAMES_PROMPT,
    UI_DESIGN_PROMPT
)
from typing import Dict

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
        
        print("AIAnalyst: Generating 8 project documents...")
        results['REQUIREMENTS'] = await self.llm.generate_content('REQUIREMENTS', variables, REQUIREMENT_PROMPT)
        results['PLANNING'] = await self.llm.generate_content('PLANNING', variables, PLANNING_PROMPT)
        results['ARCHITECTURE'] = await self.llm.generate_content('ARCHITECTURE', variables, ARCHITECTURE_PROMPT)
        results['IPMP'] = await self.llm.generate_content('IPMP', variables, IPMP_PROMPT)
        results['SCHEDULE_COST'] = await self.llm.generate_content('SCHEDULE_COST', variables, SCHEDULE_COST_PROMPT)
        results['QUALITY_RISK'] = await self.llm.generate_content('QUALITY_RISK', variables, QUALITY_RISK_PROMPT)
        results['TESTING_RELEASE'] = await self.llm.generate_content('TESTING_RELEASE', variables, TESTING_RELEASE_PROMPT)
        results['UI_UX'] = await self.llm.generate_content('UI_UX', variables, UI_UX_PROMPT)

        # STEP 3: GENERATE STRUCTURED UI DESIGN ARTIFACTS (if project_id provided)
        if project_id:
            try:
                print("AIAnalyst: Generating structured UI design artifacts...")
                
                # Generate UI Contracts
                print("  - Generating UI Contracts...")
                ui_contracts_raw = await self.llm.generate_content('UI_CONTRACTS', variables, UI_CONTRACTS_PROMPT)
                ui_contracts_json = self._clean_json(ui_contracts_raw)
                
                # Generate Wireframes
                print("  - Generating Wireframes...")
                wireframes_raw = await self.llm.generate_content(
                    'WIREFRAMES',
                    {"ui_contracts": ui_contracts_json},
                    WIREFRAMES_PROMPT
                )
                wireframes_json = self._clean_json(wireframes_raw)
                
                # Generate UI Design
                print("  - Generating UI Design...")
                ui_design_raw = await self.llm.generate_content(
                    'UI_DESIGN',
                    {
                        "wireframes": wireframes_json,
                        "ui_contracts": ui_contracts_json
                    },
                    UI_DESIGN_PROMPT
                )
                ui_design_json = self._clean_json(ui_design_raw)
                
                # Save artifacts to files
                self._save_design_artifacts(project_id, ui_contracts_json, wireframes_json, ui_design_json)
                print("AIAnalyst: UI design artifacts generated and saved successfully!")
                
            except Exception as e:
                print(f"AIAnalyst: Error generating UI design artifacts: {e}")
                # Continue without failing the entire analysis

        return results

    def _clean_json(self, raw_content: str) -> str:
        """Clean JSON content by removing markdown formatting"""
        content = raw_content.strip()
        if content.startswith('```json'):
            content = content.replace('```json', '', 1).rsplit('```', 1)[0].strip()
        elif content.startswith('```'):
            content = content.replace('```', '', 1).rsplit('```', 1)[0].strip()
        return content

    def _save_design_artifacts(self, project_id: str, ui_contracts: str, wireframes: str, ui_design: str):
        """Save design artifacts as separate JSON files"""
        artifacts_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "docs"
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save UI Contracts
        with open(artifacts_dir / "ui_contracts.json", 'w', encoding='utf-8') as f:
            f.write(ui_contracts)
        
        # Save Wireframes
        with open(artifacts_dir / "wireframes.json", 'w', encoding='utf-8') as f:
            f.write(wireframes)
        
        # Save UI Design
        with open(artifacts_dir / "ui_design.json", 'w', encoding='utf-8') as f:
            f.write(ui_design)
