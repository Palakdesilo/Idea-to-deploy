import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import urllib.request
import urllib.parse
import google.generativeai as genai

class LLMService:
    def __init__(self):
        # Load .env - try multiple locations to be safe
        env_locations = [
            Path(__file__).parent.parent / ".env",          # apps/api/.env
            Path(__file__).parent.parent.parent / ".env",   # root/.env
            Path.cwd() / ".env"                             # current working dir/.env
        ]
        for env_path in env_locations:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                print(f"LLMService: Loaded .env from {env_path.absolute()}")

        # 1. LOAD GOOGLE KEY FIRST
        self.google_api_key = (os.getenv("GOOGLE_API_KEY") or os.getenv("google_api_key") or "").strip().strip('"').strip("'")
        
        # 2. DECIDE ON OPENAI KEY
        # functionality: If Google is present, we FORCE api_key to None so OpenAI can never run.
        if self.google_api_key:
            print("LLMService: 🟢 GOOGLE_API_KEY found. IGNORING OpenAI Key completely.")
            self.api_key = None 
        else:
            self.api_key = os.getenv("OPENAI_API_KEY", "").strip().strip('"').strip("'")
        
        self.llm = None
        self.gemini_llm = None

        # 3. INITIALIZE MODELS
        if self.google_api_key:
            print("LLMService: SWITCHING TO GEMINI EXCLUSIVE MODE.")
            # List of models to try in order of preference
            # Using Gemini 1.5 Pro as requested by User
            models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro"]
            
            for model_name in models_to_try:
                try:
                    print(f"LLMService: Attempting to initialize with {model_name}...")
                    self.gemini_llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        temperature=0.3,
                        google_api_key=self.google_api_key,
                        convert_system_message_to_human=True
                    )
                    # Test call to verify model availability
                    from langchain_core.messages import HumanMessage
                    import asyncio
                    # We can't easily await in __init__, so we just assume if it doesn't crash here it's okay
                    # or we can just try another one if ainvoke fails later.
                    print(f"LLMService: {model_name} initialized (pending verification).")
                    break
                except Exception as e:
                    print(f"LLMService: Failed to init {model_name}: {e}")
                    continue
            
            if not self.gemini_llm:
                print("LLMService: CRITICAL - All Gemini models failed to initialize.")
        
        elif self.api_key:
            print("LLMService: No Google Key. Defaulting to OpenAI.")
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                openai_api_key=self.api_key
            )
        else:
            print("LLMService: 🔴 NO API KEYS FOUND.")

    async def generate_content(self, task_name: str, variables: Dict[str, Any], prompt_template: str) -> str:
        final_prompt = prompt_template
        for k, v in variables.items():
            final_prompt = final_prompt.replace(f"{{{k}}}", str(v))
        
        from langchain_core.messages import HumanMessage
        
        # EXCLUSIVE PATH: GEMINI
        if self.gemini_llm:
            async def try_generate(model_inst):
                print(f"LLMService: ⚡ Using {model_inst.model} for {task_name}...")
                response = await model_inst.ainvoke([HumanMessage(content=final_prompt)])
                return response.content

            try:
                return await try_generate(self.gemini_llm)
            except Exception as e:
                # If the primary model failed (e.g. 404) or hit quota (429), try the fallback list
                err_msg = str(e).lower()
                if any(x in err_msg for x in ["404", "not found", "not supported", "429", "quota", "resourceexhausted"]):
                    print(f"LLMService: Primary model {self.gemini_llm.model} failed or rate limited ({e}). Trying fallbacks...")
                    # User requested priority
                    fallbacks = ["models/gemini-1.5-pro", "models/gemini-1.5-flash"]
                    for fb_name in fallbacks:
                        if fb_name == self.gemini_llm.model: continue
                        try:
                            fb_llm = ChatGoogleGenerativeAI(
                                model=fb_name,
                                temperature=0.3,
                                google_api_key=self.google_api_key,
                                convert_system_message_to_human=True
                            )
                            result = await try_generate(fb_llm)
                            self.gemini_llm = fb_llm # Update to working model
                            return result
                        except Exception:
                            continue
                print(f"LLMService: ❌ Gemini Generation ERROR: {e}")
                
                # FALLBACK FOR QUOTA/404 if everything fails
                if any(x in str(e).lower() for x in ["429", "quota", "limit", "404", "not found"]):
                    return "Limit Exists"
                
                raise e # Fail hard for other errors
        
        # EXCLUSIVE PATH: OPENAI (Only if Gemini is null)
        if self.llm:
            try:
                print(f"LLMService: Using OpenAI for {task_name}...")
                response = await self.llm.ainvoke([HumanMessage(content=final_prompt)])
                return response.content
            except Exception as e:
                print(f"LLMService: OpenAI Error: {e}")
                raise e
        
        raise Exception("LLMService: No available LLM initialized.")

    async def _enrich_image_prompt(self, user_prompt: str) -> str:
        """
        Uses Gemini to transform a basic prompt into a high-fidelity, 
        professional design prompt for Imagen.
        """
        if not self.gemini_llm:
            return user_prompt
            
        enrichment_prompt = f"""
        Act as a World-Class UI/UX Prompt Engineer for Imagen 3.
        Your goal is to take a basic screen description and expand it into a 
        high-fidelity, photorealistic, and premium design prompt.
        
        Input: "{user_prompt}"
        
        Rules for the new prompt:
        1. Expand the description for clarity and detail.
        2. Focus on professional UI/UX composition.
        3. Describe layout, typography, and functional clarity.
        4. Maintain the core intent of the original prompt.
        
        Output ONLY the expanded prompt text. No commentary.
        """
        try:
            from langchain_core.messages import HumanMessage
            print(f"LLMService: ✨ Enriching prompt for higher quality...")
            response = await self.gemini_llm.ainvoke([HumanMessage(content=enrichment_prompt)])
            enriched = response.content.strip()
            print(f"LLMService: ✅ Prompt Enriched (Length: {len(enriched)})")
            return enriched
        except Exception as e:
            print(f"LLMService: Prompt enrichment failed: {e}")
            raise e

    async def generate_image(self, prompt: str) -> str:
        """
        Generates an image using Google's Imagen 3 model via the Gemini API key.
        Matches user request: 'Generate with Gemini 3 Pro Image'
        Automatically 'enriches' the prompt for premium results.
        """
        debug_log = Path("llm_debug.txt")
        def log(msg):
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"{msg}\n")
        
        log(f"\n--- New Image Request: {prompt[:30]} ---")
        try:
            if not self.google_api_key:
                log("ERROR: Google API Key missing")
                return ""

            # NEW: Enrich the prompt first to get 'Chat Quality' results
            log("Enriching prompt...")
            final_prompt = await self._enrich_image_prompt(prompt)
            log(f"Enriched prompt: {final_prompt[:100]}...")

            log(f"Initializing genai with key...")
            genai.configure(api_key=self.google_api_key)
            
            # Use Imagen 3 model (STRICTLY ENFORCED)
            try:
                log("Loading strictly imagen-3.0-generate-001...")
                imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
            except Exception as e:
                log(f"ERROR: Could not load imagen: {e}")
                return ""
                
            log("Executing generate_images...")
            result = imagen_model.generate_images(
                prompt=final_prompt,
                number_of_images=1,
            )
            log("Execution finished.")
            
            if not result or not result.images:
                log("ERROR: No images returned in result")
                return ""

            img = result.images[0]
            log("Image object received.")
            
            # Save to a temp file
            base_dir = Path(__file__).parent.parent.parent.parent / "data" / "artifacts" / "tmp"
            base_dir.mkdir(parents=True, exist_ok=True)
            
            tmp_name = f"temp_gen_{os.urandom(4).hex()}.png"
            tmp_path = base_dir / tmp_name
            
            log(f"Saving to {tmp_path}...")
            img.save(tmp_path)
            log("Save successful.")
            
            # Return a file:// URL that urllib can handle
            return f"file:///{str(tmp_path.absolute()).replace(os.sep, '/')}"

        except Exception as e:
            log(f"CRITICAL ERROR in generate_image: {e}")
            import traceback
            log(traceback.format_exc())
            return ""

    async def download_image_bytes(self, url: str) -> Optional[bytes]:
        """
        Downloads image bytes from a URL using standard urllib.
        Supports file:// protocol for local temp files.
        """
        try:
            print(f"LLMService: Downloading bytes from {url[:30]}...")
            
            # For file:// URLs, we don't need (and shouldn't use) headers
            if url.startswith("file://"):
                with urllib.request.urlopen(url) as response:
                    return response.read()
            
            # For http/https URLs
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0'
                }
            )
            with urllib.request.urlopen(req) as response:
                return response.read()
        except Exception as e:
            print(f"LLMService: Download failed: {e}")
            return None
