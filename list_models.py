import google.generativeai as genai
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path('apps/api/.env')
load_dotenv(env_path)
key = os.getenv('GOOGLE_API_KEY') or os.getenv('google_api_key')

if not key:
    print("No key found")
    exit()

genai.configure(api_key=key)

print("Listing models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error: {e}")
