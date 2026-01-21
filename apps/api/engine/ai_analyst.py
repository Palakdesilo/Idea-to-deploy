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
        
        # EXACTLY LIKE REQUESTED PROMPT
        prompt = f"""
You are a senior product and project architect.

Given the following product idea:
"{idea_description}"

Generate the following 7 documents.
Each document must have:
- Clear headings
- Bullet points
- Industry-standard structure
- No JSON
- Plain readable text

Documents:
1. Requirement Documents
2. Project Planning Documents
3. Technical Architecture & Delivery Plans
4. Integrated Project Management Plans (IPMP)
5. Schedule & Cost Plans
6. Quality, Risk & Procurement Plans
7. Testing & Release Plans

Write each document under a clear heading.

IMPORTANT RULE FOR TIMELINES:
- You must ESTIMATE REALISTIC TIMELINES based on the complexity of the idea.
- If the idea is a Simple Static Website, the TOTAL duration should be 3-7 days.
- If the idea is a Basic Web App (CRUD), the TOTAL duration should be 2-4 weeks.
- If the idea is a Complex Enterprise System, the TOTAL duration can be 2-3 months.
- Adjust the "Schedule & Cost Plan" specifically to reflect this. DO NOT propose a 6-month timeline for a simple landing page.
"""

        print("AIAnalyst: Requesting LLM...")
        full_result = await self.llm.generate_content("PROJECT_DOCS", {"idea": idea_description}, prompt)
        

        print(f"AIAnalyst: Received content (len: {len(full_result)})")
        
        # Save the full result
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
        
        # Strategy A: Regex Split by Numbered Headers (Strongest if LLM follows instructions)
        # We look for newline + optional markdown + digit + dot + space
        # We use capturing group to see what we split, but split logic usually consumes delimiters.
        # So we use lookahead or just standard split.
        
        # Pattern: Newline, optional hash/asterisk/whitespace, digit, dot, space.
        # Updated to handle **bold** numbers or ## headers
        header_pattern = r'(?:^|\n)(?:[\#\*]+\s*)?\d+\.\s+[A-Z][a-zA-Z\s\&\(\)]+'
        
        # Find all start indices of headers
        matches = list(re.finditer(header_pattern, full_result))
        
        if len(matches) >= 4:
            print(f"AIAnalyst: Found {len(matches)} numbered headers.")
            # We assume these matches correspond to our 7 documents in order
            # (Or as many as found)
            
            for i in range(len(matches)):
                start_idx = matches[i].start()
                end_idx = matches[i+1].start() if i < len(matches) - 1 else len(full_result)
                
                # Extract content
                content_chunk = full_result[start_idx:end_idx].strip()
                
                # Determine category based on content header or index
                # We try to match the header text against our mapping
                header_text = content_chunk.split('\n')[0].lower()
                
                matched_cat = None
                for cat, title in mapping:
                    # distinct words
                    keywords = [w.lower() for w in title.replace('&', '').replace('(', '').replace(')', '').split() if len(w) > 3]
                    # Check if enough keywords match
                    match_count = sum(1 for k in keywords if k in header_text)
                    if match_count >= 1:
                        matched_cat = cat
                        break
                
                # Fallback to index if reliable
                if not matched_cat and i < len(mapping):
                    matched_cat = mapping[i][0]
                
                if matched_cat:
                    generated_docs[matched_cat] = content_chunk

        # Strategy B: If Strategy A failed to find enough sections, try fuzzy title search
        if len(generated_docs) < 4:
            print("AIAnalyst: Regex headers not sufficient, trying fuzzy title search.")
            lower_content = full_result.lower()
            found_indices = []
            
            for cat, title in mapping:
                # Simplify title for search
                simple_title = title.lower().split('(')[0].strip()
                idx = lower_content.find(simple_title)
                if idx != -1:
                    found_indices.append((idx, cat))
            
            # Sort by position
            found_indices.sort(key=lambda x: x[0])
            
            for i in range(len(found_indices)):
                start, cat = found_indices[i]
                end = found_indices[i+1][0] if i < len(found_indices) - 1 else len(full_result)
                generated_docs[cat] = full_result[start:end].strip()

        # Strategy C was removed

        # Final Pass: Fill in missing docs and notify UI
        for cat, title in mapping:
            if cat not in generated_docs:
                generated_docs[cat] = ""
            
            # Send to UI
            if on_doc_generated:
                await on_doc_generated(cat, generated_docs[cat])

        print(f"AIAnalyst: Completed. Docs parsed: {len(generated_docs)}")
        return generated_docs

