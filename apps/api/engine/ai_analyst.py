import os
import re
from pathlib import Path
from .llm_service import LLMService
from typing import Dict, List
from .project_manager import ARTIFACTS_DIR

class AIAnalyst:
    VERSION = "3.2.0-SIMPLIFIED-MAX-ROBUST"

    def __init__(self):
        self.llm = LLMService()

    async def analyze_idea(self, idea_description: str, project_id: str = None, on_doc_generated=None) -> Dict[str, str]:
        if not project_id:
            return {"error": "Project ID is required"}

        print(f"AIAnalyst: Starting robust simplified analysis for {project_id}")
        
        # PROMPT WITH STRICT DELIMITERS
        prompt = f"""
You are a senior product and project architect.

Given the following product idea:
"{idea_description}"

Generate the following 7 documents.
Use the EXACT Delimiters shown below to separate each document. 
Do NOT output PREAMBLE or POSTSCRIPT.

<<<DOC: REQUIREMENTS>>>
[Content for Requirement Document]
<<<END>>>

<<<DOC: PLANNING>>>
[Content for Project Planning Document]
<<<END>>>

<<<DOC: ARCHITECTURE>>>
[Content for Technical Architecture]
<<<END>>>

<<<DOC: IPMP>>>
[Content for IPMP]
<<<END>>>

<<<DOC: SCHEDULE_COST>>>
[Content for Schedule & Cost]
<<<END>>>

<<<DOC: QUALITY_RISK>>>
[Content for Quality & Risk]
<<<END>>>

<<<DOC: TESTING_RELEASE>>>
[Content for Testing & Release]
<<<END>>>

Document Rules:
- Clear headers and bullet points.
- Plain text, no JSON.
- Realistic timeline estimation (Weeks/Months based on complexity).
"""

        print("AIAnalyst: Requesting LLM...")
        full_result = await self.llm.generate_content("PROJECT_DOCS", {"idea": idea_description}, prompt)
        
        print(f"AIAnalyst: Received content (len: {len(full_result)})")
        
        # Save raw for debugging
        docs_dir = ARTIFACTS_DIR / project_id / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        with open(docs_dir / "project_documents.txt", "w", encoding="utf-8") as f:
            f.write(full_result)

        mapping = [
            ("REQUIREMENTS", "Requirement Documents"),
            ("PLANNING", "Project Planning Documents"),
            ("ARCHITECTURE", "Technical Architecture & Delivery Plans"),
            ("IPMP", "Integrated Project Management Plans (IPMP)"),
            ("SCHEDULE_COST", "Schedule & Cost Plans"),
            ("QUALITY_RISK", "Quality, Risk & Procurement Plans"),
            ("TESTING_RELEASE", "Testing & Release Plans")
        ]
        
        generated_docs = {}
        
        # Robust Splitting Strategy
        for cat, title in mapping:
            pattern = f"<<<DOC: {cat}>>>(.*?)<<<END>>>"
            match = re.search(pattern, full_result, re.DOTALL)
            if match:
                content = match.group(1).strip()
                generated_docs[cat] = content
            else:
                generated_docs[cat] = ""
                print(f"AIAnalyst: Warning - Missing section for {cat}")

        # Final Pass: Notify UI
        for cat, title in mapping:
            if on_doc_generated:
                await on_doc_generated(cat, generated_docs.get(cat, ""))

        print(f"AIAnalyst: Completed. Docs parsed: {len(generated_docs)}")
        return generated_docs
