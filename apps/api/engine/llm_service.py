import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import urllib.request
import urllib.parse
import google.generativeai as legacy_genai
try:
    from google import genai
    NEW_SDK_AVAILABLE = True
except ImportError:
    NEW_SDK_AVAILABLE = False

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

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
        self.ollama_llm = None

        # 4. INITIALIZE OLLAMA (Local Fallback)
        if OLLAMA_AVAILABLE:
            try:
                self.ollama_llm = ChatOllama(model="llama3", temperature=0.3)
                print("LLMService: 🟢 Ollama (llama3) initialized as local fallback.")
            except Exception as e:
                print(f"LLMService: Ollama init failed: {e}")

        # 3. INITIALIZE MODELS
        if self.google_api_key:
            print("LLMService: SWITCHING TO GEMINI EXCLUSIVE MODE.")
            # List of models to try in order of preference
            models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro"]
            # models_to_try = ["gemini-2.5-flash", "gemini-2.5-pro"]
            
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
                # FINAL FALLBACK: OLLAMA (Local)
                if self.ollama_llm:
                    try:
                        print(f"LLMService: 🏠 Cloud failed. Falling back to LOCAL OLLAMA for {task_name}...")
                        return await try_generate(self.ollama_llm)
                    except Exception as ollama_err:
                        print(f"LLMService: ❌ Ollama also failed: {ollama_err}")

                # FALLBACK FOR QUOTA/404 if everything fails
                if any(x in str(e).lower() for x in ["429", "quota", "limit", "404", "not found"]):
                    return "# ERROR: AI Rate Limit or Model Not Found. Generation skipped."
                
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
        1. Keep the "STRICT LAYOUT INSTRUCTIONS" from the input intact and prioritized.
        2. Expand the visual descriptions for clarity and premium detail (lighting, texture, colors).
        3. Focus on professional UI/UX composition.
        4. Describe layout, typography, and functional clarity.
        5. DO NOT hallucinate new elements that conflict with the layout.
        
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
            # FAIL-SAFE: If enrichment fails (e.g. Rate Limit 429), just use the original prompt.
            # Do NOT crash the entire image generation process.
            print(f"LLMService: ⚠️ Prompt enrichment failed/skipped ({e}). Using raw prompt.")
            return user_prompt

    async def generate_image(self, prompt: str) -> str:
        """
        Generates an image using Google's Imagen 3 model via the Gemini API key.
        Matches user request: 'Generate with Gemini 3 Pro Image'
        Automatically 'enriches' the prompt for premium results.
        """
        debug_log = Path("llm_debug_v2.txt")
        def log(msg):
            print(f"LLM: {msg}", flush=True)
            with open(debug_log, "a", encoding="utf-8") as f:
                f.write(f"{msg}\n")

        
        log(f"\n--- New Image Request: {prompt[:30]} ---")
        try:
            if not self.google_api_key:
                log("ERROR: Google API Key missing")
                return ""

            # SKIP ENRICHMENT to save quota.
            # log("Enriching prompt...")
            # final_prompt = await self._enrich_image_prompt(prompt)
            final_prompt = prompt 
            log(f"Using raw prompt (Enrichment skipped to save quota): {final_prompt[:100]}...")

            log("Initializing genai with key...")
            
            # Use NEW SDK if available, else fallback to legacy with safety
            if NEW_SDK_AVAILABLE:
                log("Using NEW google-genai SDK...")
                
                # FORCE TRY EXPERIMENTAL FREE MODELS FIRST
                api_versions = ['v1beta']
                possible_models = [
                    'models/gemini-2.0-flash-exp-image-generation',
                    'models/gemini-2.5-flash-image',
                    'models/gemini-3-pro-image-preview'
                ]
                
                success = False
                for version in api_versions:
                    if success: break
                    log(f"--- Testing API Version: {version} ---")
                    client = genai.Client(api_key=self.google_api_key, http_options={'api_version': version})
                    
                    # Log what's actually available
                    try:
                        avail = [m.name for m in client.models.list()]
                        log(f"Models available for {version}: {avail}")
                    except:
                        log(f"Could not list models for {version}")

                    for model_id in possible_models:

                        try:
                            log(f"Attempting {model_id} (Version: {version})...")
                            result = client.models.generate_images(
                                model=model_id,
                                prompt=final_prompt,
                                config=genai.types.GenerateImagesConfig(
                                    number_of_images=1,
                                )
                            )
                            log(f"SUCCESS with {model_id} on {version}")
                            success = True
                            break
                        except Exception as e:
                            log(f"Failed {model_id} on {version}: {e}")
                
                if not success:
                    log("All Imagen variations failed. This usually means your Google AI Studio account does not have access to Imagen 3 yet.")
                    return ""


            else:
                log("NEW SDK NOT FOUND. Falling back to LEGACY SDK...")
                legacy_genai.configure(api_key=self.google_api_key)
                model_name = "imagen-3.0-generate-001"
                try:
                    # Legacy SDK usually uses GenerativeModel for everything now
                    imagen_model = legacy_genai.GenerativeModel(model_name)
                    log(f"Calling legacy generate_content on {model_name}...")
                    result = imagen_model.generate_content(final_prompt)
                except Exception as e:
                    log(f"LEGACY SDK Error: {e}")
                    raise e

            if not result or not result.generated_images if NEW_SDK_AVAILABLE else not result:
                log("ERROR: No images returned in result")
                return ""

            # Standardize image access between SDKs
            if NEW_SDK_AVAILABLE:
                img_data = result.generated_images[0].image_bytes
                # We need to save bytes to file
                base_dir = Path(__file__).parent.parent.parent.parent / "data" / "artifacts" / "tmp"
                base_dir.mkdir(parents=True, exist_ok=True)
                tmp_name = f"temp_gen_{os.urandom(4).hex()}.png"
                tmp_path = base_dir / tmp_name
                log(f"Saving bytes to {tmp_path}...")
                with open(tmp_path, "wb") as f:
                    f.write(img_data)
            else:
                # Legacy handling (assumes result.images[0])
                if not hasattr(result, 'images') or not result.images:
                    log("LEGACY ERROR: No images in result object")
                    return ""
                img = result.images[0]
                base_dir = Path(__file__).parent.parent.parent.parent / "data" / "artifacts" / "tmp"
                base_dir.mkdir(parents=True, exist_ok=True)
                tmp_name = f"temp_gen_{os.urandom(4).hex()}.png"
                tmp_path = base_dir / tmp_name
                log(f"Saving PIL image to {tmp_path}...")
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
