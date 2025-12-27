import json
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
    UI_UX_PROMPT
)
from typing import Dict

class AIAnalyst:
    VERSION = "2.0.0-PY"

    def __init__(self):
        self.llm = LLMService()

    async def analyze_idea(self, idea_description: str) -> Dict[str, str]:
        # STEP 1: IDEA -> CANONICAL JSON
        print("AIAnalyst: Generating Canonical JSON...")
        canonical_json_raw = await self.llm.generate_content(
            'CANONICAL_JSON',
            {"idea": idea_description},
            CANONICAL_JSON_PROMPT
        )

        # Basic cleaning of JSON
        canonical_json = canonical_json_raw.strip()
        if canonical_json.startswith('```json'):
            canonical_json = canonical_json.replace('```json', '', 1).rsplit('```', 1)[0].strip()
        elif canonical_json.startswith('```'):
            canonical_json = canonical_json.replace('```', '', 1).rsplit('```', 1)[0].strip()

        try:
            json.loads(canonical_json)
            print("AIAnalyst: Canonical JSON validated successfully.")
        except Exception as e:
            print(f"AIAnalyst: Failed to parse canonical JSON. Proceeding but it may affect downstream documents: {e}")

        variables = {
            "canonical_json": canonical_json
        }

        # STEP 2: DOCUMENT GENERATION
        # We'll do this sequentially for now to avoid any rate limiting or context issues, 
        # though parallel is possible with asyncio.gather
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

        return results
